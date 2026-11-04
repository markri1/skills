"""Validate dependencies, drivers and optional expected delivery settings."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from _scene_tools import arguments, atomic_json, effective_size, scene_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resolution', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'))
    parser.add_argument('--fps', type=float)
    parser.add_argument('--require-camera', action='store_true')
    args = arguments(parser)
    s = bpy.context.scene
    report = scene_report(s)
    errors = []
    if report['missing_media']:
        errors.append('Missing external media')
    if report['invalid_drivers']:
        errors.append('Invalid drivers')
    if args.require_camera and s.camera is None:
        errors.append('Missing active camera')
    if args.resolution and effective_size(s) != args.resolution:
        errors.append('Effective resolution differs from requested resolution')
    if args.fps is not None and abs(s.render.fps / s.render.fps_base - args.fps) > 1e-6:
        errors.append('Frame rate differs from requested rate')
    report.update({'valid': not errors, 'errors': errors})
    atomic_json(args.output, report)
    if errors:
        raise RuntimeError('; '.join(errors))
    print('SCENE_VALIDATED', str(args.output))


if __name__ == '__main__':
    main()
