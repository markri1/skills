"""Resumable composited PNG animation, optionally encoded with existing sound."""
import argparse
import gc
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from _scene_tools import (arguments, atomic_json, digest, effective_size, enum_set,
                          configure_device, media_dependencies, png_valid,
                          render_configuration, require_render_context, set_engine,
                          set_png, set_samples, add_device_args)


def encode_movie(scene, folder, video, start, end, size, crf):
    editor = scene.sequence_editor_create()
    strips = getattr(editor, 'strips', None)
    if strips is None:
        strips = editor.sequences
    all_strips = getattr(editor, 'strips_all', getattr(editor, 'sequences_all', []))
    has_audio = any(st.type == 'SOUND' for st in all_strips)
    channel = max((st.channel for st in strips), default=0) + 1
    sequence = strips.new_image('Composited render frames', str(folder / f'{start:06d}.png'),
                                channel=channel, frame_start=start)
    for frame in range(start + 1, end + 1):
        sequence.elements.append(f'{frame:06d}.png')
    sequence.frame_final_duration = end - start + 1
    scene.render.use_sequencer = True
    scene.render.use_compositing = False
    enum_set(scene.view_settings, 'view_transform', 'Standard')
    enum_set(scene.view_settings, 'look', 'None')
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    if hasattr(scene.view_settings, 'use_curve_mapping'):
        scene.view_settings.use_curve_mapping = False
    if hasattr(sequence, 'colorspace_settings'):
        enum_set(sequence.colorspace_settings, 'name', 'sRGB')
    if hasattr(scene.render.image_settings, 'media_type'):
        enum_set(scene.render.image_settings, 'media_type', 'VIDEO')
    enum_set(scene.render.image_settings, 'file_format', 'FFMPEG')
    enum_set(scene.render.ffmpeg, 'format', 'MPEG4')
    enum_set(scene.render.ffmpeg, 'codec', 'H264')
    try:
        enum_set(scene.render.ffmpeg, 'constant_rate_factor', 'CUSTOM')
    except ValueError as exc:
        raise ValueError('This encoder lacks custom CRF; use PNG frames with a configured external encoder') from exc
    if not hasattr(scene.render.ffmpeg, 'custom_constant_rate_factor'):
        raise ValueError('This Blender version lacks the requested custom CRF control')
    scene.render.ffmpeg.custom_constant_rate_factor = crf
    enum_set(scene.render.ffmpeg, 'audio_codec', 'AAC' if has_audio else 'NONE')
    if has_audio:
        scene.render.ffmpeg.audio_mixrate = 48000
        scene.render.ffmpeg.audio_bitrate = 192
    video.parent.mkdir(parents=True, exist_ok=True)
    temporary = video.with_name(video.stem + '.encoding.mp4')
    scene.render.filepath = str(temporary)
    bpy.ops.render.render(animation=True)
    clip = bpy.data.movieclips.load(str(temporary), check_existing=False)
    try:
        if clip.frame_duration != end - start + 1 or list(clip.size) != size:
            raise RuntimeError('Encoded video dimensions/frame count mismatch')
        fps = scene.render.fps / scene.render.fps_base
        if abs(clip.fps - fps) > .05:
            raise RuntimeError('Encoded video frame-rate mismatch')
        result = {'path': str(video), 'frames': clip.frame_duration, 'fps': fps,
                  'seconds': clip.frame_duration / fps, 'resolution': size, 'crf': crf,
                  'audio': has_audio, 'bytes': temporary.stat().st_size}
    finally:
        bpy.data.movieclips.remove(clip)
    if has_audio:
        import aud
        sound = aud.Sound.file(str(temporary))
        data = sound.data()
        if not len(data):
            raise RuntimeError('Encoded audio is empty')
        result['audio_seconds'] = len(data) / sound.specs[0]
        result['audio_peak'] = max(abs(float(data.min())), abs(float(data.max())))
        del data, sound
    gc.collect()
    # A remaining OS decoder lock leaves the completed temporary file available.
    try:
        temporary.rename(video)
    except OSError as exc:
        raise RuntimeError(f'Encoding finished. After Blender exits, finalize {temporary} to {video}; do not rerender frames') from exc
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--engine')
    parser.add_argument('--samples', type=int)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--video', type=Path, help='Optional new .mp4 output; opaque sRGB delivery')
    parser.add_argument('--crf', type=int, default=12)
    parser.add_argument('--max-new-frames', type=int, help='Explicit per-run budget; resume later')
    add_device_args(parser)
    args = arguments(parser)
    scene = bpy.context.scene
    require_render_context(scene)
    source = Path(bpy.data.filepath)
    if not bpy.data.filepath or not source.is_file():
        raise ValueError('Save a separate scene snapshot before rendering')
    if args.max_new_frames is not None and args.max_new_frames < 1:
        raise ValueError('Frame budget must be positive')
    if not 0 <= args.crf <= 51:
        raise ValueError('CRF must be between 0 and 51')
    start = scene.frame_start if args.start is None else args.start
    end = scene.frame_end if args.end is None else args.end
    if end < start:
        raise ValueError('End frame precedes start frame')
    scene.frame_start, scene.frame_end, scene.frame_step = start, end, 1
    set_engine(scene, args.engine)
    set_samples(scene, args.samples)
    configure_device(scene, args.device, args.compute_device)
    set_png(scene, 8)
    scene.render.use_file_extension = True
    size = effective_size(scene)
    dependencies = media_dependencies(scene)
    if any(not d['exists'] for d in dependencies):
        raise ValueError('Missing media; run validate_scene.py first')
    video = args.video.expanduser().resolve() if args.video else None
    if video:
        if video.exists():
            raise FileExistsError(video)
        if video.suffix.lower() != '.mp4' or any(n % 2 for n in size):
            raise ValueError('H.264 MP4 needs an .mp4 path and even output dimensions')
        if scene.display_settings.display_device.lower() != 'srgb':
            raise ValueError('Optional encoder supports sRGB display output; use a custom encoder for this OCIO setup')
        if not hasattr(scene.render.ffmpeg, 'custom_constant_rate_factor'):
            raise ValueError('This Blender version lacks custom CRF; render PNGs and use a configured external encoder')
        old_crf = scene.render.ffmpeg.constant_rate_factor
        try:
            enum_set(scene.render.ffmpeg, 'constant_rate_factor', 'CUSTOM')
        finally:
            enum_set(scene.render.ffmpeg, 'constant_rate_factor', old_crf)
        editor = scene.sequence_editor
        if editor and any(st.type == 'SCENE' for st in getattr(editor, 'strips_all', getattr(editor, 'sequences_all', []))):
            raise ValueError('Scene-strip audio needs a project-specific mix/encode workflow')
    prefs = bpy.context.preferences.addons.get('cycles')
    prefs = prefs.preferences if prefs else None
    device_state = {'backend': getattr(prefs, 'compute_device_type', None),
                    'devices': sorted([d.name, d.type, bool(d.use)] for d in getattr(prefs, 'devices', []))}
    manifest = {'schema': 1, 'source': str(source.resolve()), 'source_sha256': digest(source),
                'helper_sha256': digest(__file__),
                'common_sha256': digest(Path(__file__).with_name('_scene_tools.py')),
                'blender': list(bpy.app.version), 'scene': scene.name, 'start': start, 'end': end,
                'configuration': render_configuration(scene), 'devices': device_state,
                'dependencies': dependencies, 'video': str(video) if video else None, 'crf': args.crf}
    folder = args.output_dir.expanduser().resolve()
    manifest_path = folder / 'manifest.json'
    if manifest_path.exists():
        if not args.resume:
            raise FileExistsError('Existing render cache; use --resume or a new output directory')
        if json.loads(manifest_path.read_text(encoding='utf-8')) != manifest:
            raise ValueError('Resume rejected: snapshot, assets, configuration or delivery settings changed')
    else:
        if args.resume:
            raise ValueError('Resume requested but no manifest exists')
        if folder.exists() and any(folder.iterdir()):
            raise FileExistsError('Initial render output directory must be empty')
        folder.mkdir(parents=True, exist_ok=True)
        atomic_json(manifest_path, manifest)
    journal_path = folder / 'frames.json'
    journal = json.loads(journal_path.read_text(encoding='utf-8')) if journal_path.exists() else {}
    total = end - start + 1
    began = time.perf_counter()
    durations = []
    reused = 0

    def progress(stage, complete, **extra):
        warm = durations[-30:] if len(durations) < 2 else durations[1:][-30:]
        mean = sum(warm) / len(warm) if warm else None
        result = {'stage': stage, 'completed': complete, 'total': total, 'reused': reused,
                  'new_frames': len(durations), 'elapsed_seconds': time.perf_counter() - began,
                  'recent_seconds_per_frame': mean,
                  'estimated_remaining_seconds': mean * (total - complete) if mean else None, **extra}
        atomic_json(folder / 'progress.json', result)
        return result

    for frame in range(start, end + 1):
        path = folder / f'{frame:06d}.png'
        if path.exists():
            if not png_valid(path, size):
                raise ValueError('Incomplete cached frame; remove this frame to regenerate: ' + str(path))
            actual = digest(path)
            if str(frame) in journal and journal[str(frame)]['sha256'] != actual:
                raise ValueError('Modified cached frame rejected: ' + str(path))
            journal[str(frame)] = {'sha256': actual, 'seconds': journal.get(str(frame), {}).get('seconds')}
            atomic_json(journal_path, journal)
            reused += 1
            progress('rendering', frame - start + 1)
            continue
        if args.max_new_frames is not None and len(durations) >= args.max_new_frames:
            progress('incomplete', frame - start)
            print('RENDER_FRAME_BUDGET_REACHED; resume with identical arguments and --resume', flush=True)
            return
        progress('rendering', frame - start, frame=frame)
        temporary = folder / f'{frame:06d}.part.png'
        scene.frame_set(frame)
        scene.render.filepath = str(temporary)
        tick = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        if not png_valid(temporary, size):
            raise RuntimeError('Invalid rendered PNG: ' + str(temporary))
        temporary.replace(path)
        duration = time.perf_counter() - tick
        durations.append(duration)
        journal[str(frame)] = {'sha256': digest(path), 'seconds': duration}
        atomic_json(journal_path, journal)
        progress('rendering', frame - start + 1)
        print('RENDER_FRAME_COMPLETE', frame, 'OF', end, flush=True)
    result = progress('encoding' if video else 'complete', total)
    if video:
        encoded = encode_movie(scene, folder, video, start, end, size, args.crf)
        result = progress('complete', total, video=encoded)
    atomic_json(folder / 'report.json', {**result, 'manifest': str(manifest_path)})
    print('ANIMATION_RENDER_COMPLETE', str(folder), flush=True)


if __name__ == '__main__':
    main()
