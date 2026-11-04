---
name: blender-scene-polish
description: Inspect and refine existing Blender scenes, improve composition, lighting, materials and surface detail, and produce checked comparison renders or resumable animation exports. Use for scene polishing and render production in Blender; derive the aesthetic and settings from the user's brief and scene.
---

# Blender Scene Polish

Improve the supplied scene while preserving the user's intended style and the work that already functions. Apply only the relevant parts of this workflow. A stylized, pristine or abstract scene may need no realistic wear, atmosphere, grain, audio or simulation.

## Establish the actual starting point

Read project instructions and inspect the connected Blender session before opening a file from disk. Record the active file, unsaved state, Blender version, scene, camera, frame range/rate, output dimensions, pixel aspect, renderer and color management. Check linked media and dependencies relevant to the requested edit.

Look through the final camera. Distinguish surface defects from intentional textures, film grain, insufficient sampling, denoising artifacts and video compression. Use references to establish composition, material identity, contrast, color and atmosphere. Identify fixed choices and the requested scope; resolve routine choices from the brief rather than introducing another approval step.

Use a connected Blender API when available. A local Blender executable can inspect saved scenes and render in a separate background process. The included scripts use Blender's Python, not ordinary system Python; invoke them by absolute path.

## Preserve a recoverable scene

Before substantial edits, make a unique save-copy of the live state, including unsaved changes, with relative paths remapped. Do not reload a saved file over newer live work. Keep the user's renderer and other settings unless their request requires changing them. Separate render-only overrides from scene edits.

Keep parents, instances, modifiers, constraints, UVs, drivers, linked libraries and media intact. When an edit could affect them, compare the relevant geometry, transforms, keyframes or references before and after. After saving, reopen a copy in a background process to check persistence rather than relying only on the live view.

## Refine from the whole image to local detail

Address composition and visual hierarchy before small details. Evaluate lighting, materials and atmosphere together, using the final view and a neutral inspection view when useful. Read only the references needed for the request:

- [Materials and surface details](references/materials-and-surface-details.md): material response, localized wear, variation and fitted details.
- [Animation and effects](references/animation-and-effects.md): spatial attachment, timing, deterministic effects, media and audio continuity.
- [Rendering and export](references/rendering-and-export.md): API differences, aspect ratio, grain, comparisons, estimates, resumable renders and export checks.

Vary details for a reason: contact, exposure, manufacturing differences, maintenance or environment. Judge close-up readability and contribution at delivery resolution. Derive sizes, quantities and intensities from scene scale, framing and the desired look.

## Render and verify the requested deliverable

For comparisons, use the same frame, saved snapshot, camera and color pipeline. Report each engine's quality settings. Check aspect-ratio changes for unintended cropping; preserve the chosen framing deliberately rather than changing lens or camera movement by accident.

Benchmark representative frames at the requested quality. Separate first-frame preparation from steady frame time. For long renders, use a snapshot and lossless intermediate frames with a manifest that prevents resuming from a different source or configuration. Keep checking the job through completion or a reported failure, with progress and revised estimates based on measurements.

Check the actual exported file: dimensions, duration, frame count/rate, decoded frames, retained detail/grain and audio when present. Compare with source frames to catch double color transforms, missing effects or excessive compression. Release decoder handles before renaming files, especially on Windows. Do not publish an unfinished temporary movie as the final deliverable.

## Included helpers

- `scripts/inspect_scene.py`: scene and dependency report without saving the scene.
- `scripts/validate_scene.py`: targeted media, driver and optional render-setting checks.
- `scripts/render_comparison.py`: matched PNGs from specified engines and frames.
- `scripts/render_animation_resumable.py`: resumable PNG animation and optional MP4 with existing sequencer sound.
- `scripts/_scene_tools.py`: shared implementation.

Render helpers require a background Blender process and never save the loaded `.blend`. Read their arguments and the rendering reference before use. Write scene-specific geometry and shader edits for the actual asset rather than applying a universal preset.

## Leave a clear handoff

Keep generated files within the agreed project/output location. Follow an existing folder convention; otherwise separate current scene, archives, scripts, image renders, movies, audio and reports. Preserve asset paths when moving `.blend` files. Delete historical scripts only after establishing that they are superseded and unreferenced within the authorized cleanup scope.

Document the current file and decisions needed for the next session, including known limitations. Deliver files with concise notes on changes and actual checks. Keep project paths, hardware, frame counts, stylistic recipes and preferred grain levels in project context rather than hardcoding them into this skill.
