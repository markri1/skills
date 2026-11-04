"""Shared Blender helpers. No save/reload operations or project-specific names."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import sys
from collections import Counter

import bpy


def arguments(parser):
    return parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def atomic_json(path, value):
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def enum_set(obj, prop, value):
    if not hasattr(obj, prop):
        raise ValueError('Unavailable property: ' + prop)
    choices = [item.identifier for item in obj.bl_rna.properties[prop].enum_items]
    # Some Blender enums under-report choices; assignment is authoritative.
    try:
        setattr(obj, prop, value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{prop}={value!r} unavailable; reported choices={choices}: {exc}') from exc


def set_engine(scene, requested):
    if not requested:
        return scene.render.engine
    if requested.upper() == 'EEVEE':
        choices = [i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items]
        candidates = ([scene.render.engine] if 'EEVEE' in scene.render.engine else [])
        candidates += [v for v in choices if 'EEVEE' in v]
        candidates += ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']
        for candidate in dict.fromkeys(candidates):
            try:
                enum_set(scene.render, 'engine', candidate)
                return candidate
            except ValueError:
                continue
        raise ValueError('No EEVEE engine available in this Blender version')
    enum_set(scene.render, 'engine', requested)
    return scene.render.engine


def set_samples(scene, count):
    if count is None:
        return
    if count < 1:
        raise ValueError('Samples must be positive')
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = count
    elif 'EEVEE' in scene.render.engine and hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = count
    else:
        raise ValueError('Sample override unsupported for ' + scene.render.engine)


def configure_device(scene, device=None, backend=None):
    if not (device or backend):
        return
    if scene.render.engine != 'CYCLES':
        raise ValueError('Device/backend overrides apply only to Cycles')
    prefs = bpy.context.preferences.addons['cycles'].preferences
    if backend:
        enum_set(prefs, 'compute_device_type', backend)
    if device == 'GPU' or backend:
        prefs.get_devices()
        selected = backend or prefs.compute_device_type
        available = [d for d in prefs.devices if d.type == selected and d.type != 'CPU']
        if not available:
            raise ValueError('No compatible GPU found for backend ' + selected)
        for entry in prefs.devices:
            entry.use = entry in available
    if device:
        enum_set(scene.cycles, 'device', device)


def compositor_tree(scene):
    return getattr(scene, 'compositing_node_group', None) or getattr(scene, 'node_tree', None)


def node_trees(tree, seen=None):
    seen = set() if seen is None else seen
    if tree is None or tree.as_pointer() in seen:
        return
    seen.add(tree.as_pointer())
    yield tree
    for node in tree.nodes:
        if node.type == 'GROUP' and not node.mute:
            yield from node_trees(getattr(node, 'node_tree', None), seen)


def require_render_context(scene):
    if not bpy.app.background:
        raise RuntimeError('Render helper requires a separate --background Blender process')
    if not scene.camera:
        raise ValueError('Scene has no active camera')
    if scene.render.use_border:
        raise ValueError('Border rendering requires a project-specific output workflow')
    if getattr(scene.render, 'use_multiview', False):
        raise ValueError('Multiview rendering requires a project-specific output workflow')
    if scene.render.use_compositing:
        outputs = [n.name for tree in node_trees(compositor_tree(scene)) for n in tree.nodes if n.type == 'OUTPUT_FILE' and not n.mute]
        if outputs:
            raise ValueError('Handle compositor File Output paths explicitly first: ' + ', '.join(outputs))


def effective_size(scene):
    return [max(1, int(scene.render.resolution_x * scene.render.resolution_percentage / 100)),
            max(1, int(scene.render.resolution_y * scene.render.resolution_percentage / 100))]


def scalar_properties(obj, exclude=()):
    if obj is None:
        return {}
    result = {}
    for prop in obj.bl_rna.properties:
        if prop.identifier in exclude or prop.type not in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            continue
        try:
            value = getattr(obj, prop.identifier)
            if isinstance(value, set):
                value = sorted(value)
            elif not isinstance(value, (str, bool, int, float)) and hasattr(value, '__iter__'):
                value = list(value)
            json.dumps(value)
            result[prop.identifier] = value
        except (AttributeError, TypeError, ValueError, RuntimeError):
            continue
    return result


def render_configuration(scene):
    return {'engine': scene.render.engine, 'resolution': effective_size(scene),
            'render': scalar_properties(scene.render, {'filepath', 'frame_path'}),
            'image_settings': scalar_properties(scene.render.image_settings),
            'view': scalar_properties(scene.view_settings), 'display': scalar_properties(scene.display_settings),
            'cycles': scalar_properties(getattr(scene, 'cycles', None)),
            'eevee': scalar_properties(getattr(scene, 'eevee', None))}


def media_dependencies(scene):
    entries = []
    for collection in ('images', 'sounds', 'movieclips', 'fonts', 'libraries', 'cache_files', 'volumes'):
        for block in getattr(bpy.data, collection, []):
            raw = getattr(block, 'filepath', '')
            if not raw or raw == '<builtin>' or getattr(block, 'source', '') in {'GENERATED', 'VIEWER'}:
                continue
            if getattr(block, 'packed_file', None) or bool(getattr(block, 'packed_files', [])):
                continue
            absolute = bpy.path.abspath(raw, library=getattr(block, 'library', None))
            path = Path(absolute).resolve()
            pattern = path.name.replace('<UDIM>', '[0-9][0-9][0-9][0-9]').replace('<UVTILE>', 'u*_v*')
            pattern = re.sub(r'#+', '*', pattern)
            candidates = sorted(path.parent.glob(pattern)) if pattern != path.name else [path]
            files = [p for p in candidates if p.is_file()]
            entries.append({'owner': collection + ':' + block.name, 'raw': raw, 'path': str(path),
                            'exists': bool(files), 'files': [file_state(p) for p in files]})
    editor = scene.sequence_editor
    if editor:
        for strip in getattr(editor, 'strips_all', getattr(editor, 'sequences_all', [])):
            paths = []
            if strip.type == 'IMAGE':
                paths = [Path(bpy.path.abspath(strip.directory)) / element.filename for element in strip.elements]
            elif strip.type == 'MOVIE':
                paths = [Path(bpy.path.abspath(strip.filepath))]
            for path in paths:
                path = path.resolve()
                entries.append({'owner': 'sequencer:' + strip.name, 'raw': str(path), 'path': str(path),
                                'exists': path.is_file(), 'files': [file_state(path)] if path.is_file() else []})
    return sorted(entries, key=lambda e: (e['owner'], e['path']))


def file_state(path):
    stat = path.stat()
    return {'path': str(path), 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}


def invalid_drivers():
    blocks = []
    for collection in ('objects', 'meshes', 'curves', 'shape_keys', 'materials', 'worlds', 'lights', 'cameras', 'node_groups', 'scenes', 'sounds', 'textures'):
        blocks.extend(getattr(bpy.data, collection, []))
    blocks += [getattr(b, 'node_tree', None) for b in blocks]
    blocks += [compositor_tree(s) for s in bpy.data.scenes]
    seen = set()
    invalid = []
    for block in blocks:
        if block is None or block.as_pointer() in seen:
            continue
        seen.add(block.as_pointer())
        ad = getattr(block, 'animation_data', None)
        for curve in ad.drivers if ad else []:
            if not curve.driver.is_valid:
                invalid.append({'owner': block.name, 'path': curve.data_path, 'index': curve.array_index})
    return invalid


def scene_report(scene):
    deps = media_dependencies(scene)
    camera = scene.camera
    return {'blender_version': bpy.app.version_string, 'file': bpy.data.filepath,
            'unsaved_changes': bpy.data.is_dirty, 'scene': scene.name,
            'object_counts': dict(Counter(o.type for o in scene.objects)),
            'frame': scene.frame_current, 'frame_range': [scene.frame_start, scene.frame_end],
            'fps': scene.render.fps / scene.render.fps_base, 'configuration': render_configuration(scene),
            'camera': {'name': camera.name, 'type': camera.data.type, 'lens': camera.data.lens,
                       'sensor_fit': camera.data.sensor_fit, 'matrix_world': [list(v) for v in camera.matrix_world]} if camera else None,
            'dependencies': deps, 'missing_media': [d for d in deps if not d['exists']],
            'invalid_drivers': invalid_drivers()}


def png_valid(path, size, depth=8):
    path = Path(path)
    if not path.is_file() or path.stat().st_size < 45:
        return False
    with path.open('rb') as stream:
        head = stream.read(25)
        stream.seek(-12, 2)
        tail = stream.read()
    return (head[:8] == b'\x89PNG\r\n\x1a\n' and list(struct.unpack('>II', head[16:24])) == list(size)
            and head[24] == depth and tail.endswith(b'IEND\xaeB`\x82'))


def set_png(scene, depth=8):
    if hasattr(scene.render.image_settings, 'media_type'):
        enum_set(scene.render.image_settings, 'media_type', 'IMAGE')
    enum_set(scene.render.image_settings, 'file_format', 'PNG')
    enum_set(scene.render.image_settings, 'color_mode', 'RGB')
    enum_set(scene.render.image_settings, 'color_depth', str(depth))


def add_device_args(parser):
    parser.add_argument('--device', choices=['CPU', 'GPU'])
    parser.add_argument('--compute-device', help='Cycles backend supported by this installation')
