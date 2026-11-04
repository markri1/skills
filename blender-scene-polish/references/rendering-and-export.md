# Rendering and export

## API and process boundaries

Inspect runtime RNA and actual node sockets. Find shader nodes by type rather than localized names; stable names are appropriate for workflow-owned nodes. Read enum choices where available. Dynamic enums can omit valid choices, so use guarded assignment errors instead of treating an empty list as proof of absence.

Compositor properties can move from attributes to input sockets. Check the version. Prefer persistent driver references through supported owning data-blocks and RNA paths: embedded node tree references can appear valid live and fail after reopening. Validate a saved copy in a fresh process.

Render from a unique save-copy with remapped relative paths in a separate background process. Helpers do not save the loaded `.blend` and require only Blender's Python/standard library. Replace `blender` below with the installed executable and use absolute paths. `--python-exit-code 1` exposes script failure to the caller.

```sh
blender --background /project/snapshot.blend --python-exit-code 1 --python /skills/blender-scene-polish/scripts/inspect_scene.py -- --output /project/reports/scene.json
blender --background /project/snapshot.blend --python-exit-code 1 --python /skills/blender-scene-polish/scripts/validate_scene.py -- --output /project/reports/validation.json --resolution 1920 1080
blender --background /project/snapshot.blend --python-exit-code 1 --python /skills/blender-scene-polish/scripts/render_comparison.py -- --output-dir /project/images/compare --frame 48 --engines CYCLES EEVEE --cycles-samples 64 --eevee-samples 64
blender --background /project/snapshot.blend --python-exit-code 1 --python /skills/blender-scene-polish/scripts/render_animation_resumable.py -- --output-dir /project/images/animation --start 1 --end 120 --engine EEVEE --samples 64 --video /project/movies/review.mp4
```

Choose quality for the actual request. `EEVEE` is a helper alias resolved against the running version. Optional explicit GPU settings, e.g. `--compute-device OPTIX --device GPU`, require compatible hardware. Unsupported choices fail rather than silently switching backend.

## Framing, finish and comparison

Account for resolution percentage and pixel aspect. Aspect changes can crop the subject with horizontal sensor fit. Decide which field of view to preserve and check bounds across the shot. Record lens/sensor/camera edits; camera transform changes can require dependent-system updates.

Separate sampling noise, surface detail and finishing grain. Apply deliberate grain after denoising. Define its strength, pixel/physical scale, temporal behavior and image domain. Resolution changes must not leave uncovered borders, stretch speckles or silently change contrast. Include the compositor in engine comparisons.

Use the same snapshot, frame, camera, color management and effects for comparisons, with stated per-engine settings. Separate shader/texture preparation from steady frame time. Benchmark representative frames and extrapolate a range rather than multiplying a single cold frame time by the full sequence.

## Long renders and resumption

The animation helper writes lossless composited RGB PNGs, a manifest and atomic progress reports. It checks source `.blend` hash, dependency file sizes/timestamps, effective render configuration and completed PNGs before resuming. Keep inputs/caches fixed during a run. The manifest does not cover hidden remote state or every directory-based simulation-cache member; use a new snapshot/output folder if relevant input changes.

Resolution, frame rate, color and compositor settings come from the scene. Engine/sample overrides require explicit arguments. Existing final files and border renders are rejected. Caches are 8-bit display RGB for optional H.264 delivery. Use a dedicated linear EXR/high-bit-depth pipeline for grading, alpha, HDR or multilayer passes.

Optional MP4 encoding places the composed PNGs above existing sequencer tracks, preserving their audio. It requires an sRGB display pipeline, uses Standard view and neutral look/exposure/gamma during encoding, and bypasses the compositor to avoid applying display transform/grain twice. Custom OCIO, scene-strip audio, multiview, File Output nodes and simulation caching need project-specific handling. Render helpers reject File Output nodes until their paths are deliberately handled separately.

## Deliver the actual export

Check encoded dimensions, duration, count/rate, first/last frames, important events, audio and fine detail. Compare decoded frames and source PNGs using matching color interpretation. Low whole-image error alone cannot prove that a small spark or subtle grain survived.

Release decoder/audio handles before renaming on Windows. If a completed movie remains locked, finalize that known file after the process exits instead of rerendering. Keep unfinished movies under an explicit temporary name and preserve reusable completed frames after interruption.
