"""Inspect the loaded scene without saving or changing it."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from _scene_tools import arguments, atomic_json, scene_report
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON report path')
    args = arguments(parser)
    report = scene_report(bpy.context.scene)
    if args.output:
        atomic_json(args.output, report)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    print('SCENE_INSPECTED', report['scene'], 'missing_media=', len(report['missing_media']))


if __name__ == '__main__':
    main()
