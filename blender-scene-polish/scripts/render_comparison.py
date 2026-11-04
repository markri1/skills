"""Matched stills; runs only in a separate Blender background session."""
import argparse
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from _scene_tools import (arguments, atomic_json, configure_device, effective_size,
                          require_render_context, render_configuration, set_engine,
                          set_png, set_samples, png_valid, add_device_args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--frame', type=int, required=True)
    parser.add_argument('--engines', nargs='+', required=True)
    parser.add_argument('--cycles-samples', type=int)
    parser.add_argument('--eevee-samples', type=int)
    add_device_args(parser)
    args = arguments(parser)
    s = bpy.context.scene
    require_render_context(s)
    output = args.output_dir.expanduser().resolve()
    names = [e.replace('/', '_').replace('\\', '_') for e in args.engines]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate engines')
    paths = [output / f'{name}_frame_{args.frame:06d}.png' for name in names]
    if any(p.exists() for p in paths):
        raise FileExistsError('Choose a new output directory; comparison files already exist')
    output.mkdir(parents=True, exist_ok=True)
    s.frame_set(args.frame)
    set_png(s, 16)
    report = []
    for requested, path in zip(args.engines, paths):
        engine = set_engine(s, requested)
        if engine == 'CYCLES':
            set_samples(s, args.cycles_samples)
            configure_device(s, args.device, args.compute_device)
        elif 'EEVEE' in engine:
            set_samples(s, args.eevee_samples)
        s.render.filepath = str(path)
        start = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        if not png_valid(path, effective_size(s), 16):
            raise RuntimeError('Incomplete or incorrectly sized PNG: ' + str(path))
        report.append({'engine': engine, 'frame': args.frame, 'path': str(path),
                       'seconds_including_preparation': time.perf_counter() - start,
                       'configuration': render_configuration(s)})
        atomic_json(output / 'comparison.json', report)
        print('COMPARISON_FRAME_COMPLETE', str(path), flush=True)


if __name__ == '__main__':
    main()
