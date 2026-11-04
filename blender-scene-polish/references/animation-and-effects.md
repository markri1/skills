# Animation and effects

## Preserve the motion contract

Read frame rate including `fps_base`, range, keyframes, drivers, constraints and parents. Match timing to that contract instead of assuming a duration or rate. Camera/subject edits can affect focus, reflections, dependent lights, media and distance/facing-based audio automation.

For layered/slotted Actions, inspect layers, strips and channelbags; older Actions expose `action.fcurves`. Preserve ownership and slot assignment. Do not replace an entire Action to change one event.

## Choose the right space

Attached lights, exposed wires and contact arcs follow their source object. Evaluate the source transform at emission. Detached fragments should continue in world space unless intentionally object-bound; parenting debris to a rotating source can bend its flight unnaturally.

Derive velocity, size and lifetime from scale, gravity and framing. Handle actual collision surfaces; a fixed height cutoff is appropriate only for a known horizontal floor. Do not introduce sparks, smoke, flicker or sound just because machinery exists.

Use ordinary keyframes for a small directed effect, or Geometry Nodes/baked simulation for larger systems. Background rendering must not depend on an interactive frame-change handler that is absent in a fresh process. Include or document simulation caches.

## Design temporal contrast

Relate intensity, frequency and duration to the desired attention level. Sparse irregular events can support atmosphere; rhythm may suit another brief. Explicitly key off states around intermittent bursts so interpolation/extrapolation cannot leave lights on.

Use continuous motion/cooling and sharp ignition where appropriate. Check first/last frames, repeated events, bright moments and inactive moments. Inspect encoded output at delivery size: a tiny effect visible close up may disappear after compression.

## Media and audio, when present

Inspect source movie rates, offsets, starts, durations and loops. Do not assume source rate equals scene rate. Remapping may be necessary; retiming video alone can create sound drift.

Preserve sequencer tracks and automation. Recalculate camera/source-relative audio dependencies when edited transforms affect them. Check mixed length, peaks, event alignment and clipping; volume automation alone is not spatial audio.

Add soundtrack/effects audio only when the request covers it. Enable a suitable codec when exporting existing sound and verify the actual muxed file rather than relying on configured settings.
