# Story and Generation Formats

Read this reference for short-form narrative design, storyboards, or prompts intended for AI image and video generators.

## Short-form narrative

Start with visible curiosity in the first one to three seconds: a strange object, distant movement, unsettling action, unusual local ritual, hiding protagonist, impossible figure, or disturbing discovery. Prefer an image-based hook over explanatory on-screen text.

A useful structure is:

1. Establish a legible place and ordinary situation.
2. Introduce one wrong detail.
3. Let the environment or local rule escalate it.
4. Reveal an encounter, sound, trace, or discovery.
5. End on an implication rather than a complete explanation.

Adapt or discard this structure when the user's premise calls for something else. For a 60–90 second story, usually create several distinct visual beats; approximately 5–10 shots often works better than one continuous shot. Do not force that count when the user requests a different duration or format.

Each beat should change the information, spatial relationship, or threat. Maintain continuity in character appearance, wardrobe, props, weather, light direction, geography, and entity design.

## Generation-prompt anatomy

For tools such as Higgsfield, Kling, Seedance, Veo, Runway, or comparable image/video models, describe the following when relevant:

1. Subject
2. Environment
3. Observable action
4. Camera position and lens relationship
5. Camera movement
6. Lighting source and direction
7. Weather and atmosphere
8. Period-specific materials, clothing, architecture, and props
9. Visual realism and image character
10. Pacing and subtle environmental motion

Adapt syntax to a named model when its prompt behavior is known and relevant. Do not claim unsupported model-specific features. Avoid contradictory camera instructions, nonvisual lore dumps, redundant adjectives, and empty quality labels.

For motion, state what changes over time: breathing, hesitant steps, cloth tugged by wind, ripples, smoke drift, lantern sway, distant movement, focus adjustment, or a slow reveal. Keep camera and subject motion compatible.

## Default output for one prompt

Use this structure unless the user requests another format:

### Concept

One short description of the scene.

### Generation Prompt

A polished, paste-ready prompt for the requested model.

### Optional Negative Constraints

Include only when they would prevent likely failure modes. Make them specific to the prompt rather than a generic blocklist.

In prompt-expansion mode, do not add concept alternatives unless requested.

## Default output for a multi-shot video

Whenever the brief contains or implies multiple scenes, use numbered scenes with one generation prompt per scene. Do not merge the sequence into one continuous prompt, even when the user's idea arrives as a single paragraph. Give each scene a distinct narrative or visual function while repeating only the continuity details the model needs.

Estimate the duration of every scene in seconds and show an approximate total runtime for the full sequence. Base the estimate on the visible action, reveal, camera movement, and intended rhythm; use a range when exact timing would be misleading. Keep the sum of the scene estimates consistent with the stated total.

For each scene, suggest a camera perspective, framing, and movement that supports its dramatic purpose. Plan the sequence as an edit: vary shot scale, height, angle, distance, or movement when the contrast strengthens the reveal, while preserving screen direction, geography, eyelines, light, wardrobe, props, weather, and entity design. Prefer motivated transitions such as a match on action, gaze, shape, sound, occlusion, or a deliberate hard cut. Avoid arbitrary angle changes, nonstop camera motion, and incompatible directions. Do not label the sequence or its camera directions as a “one-shot,” “single take,” or “continuous take” unless the user explicitly requests that form.

Example skeleton:

### Overview

Estimated total runtime: approximately 28–36 seconds

### Scene 1 — Hook (approximately 4–5 seconds)

**Suggested camera:** Perspective, framing, and movement chosen for the hook.

Prompt

**Cut to Scene 2:** Brief transition logic.

### Scene 2 — Wrong detail (approximately 5–6 seconds)

**Suggested camera:** A motivated contrast or continuation from Scene 1.

Prompt

**Cut to Scene 3:** Brief transition logic.

### Scene 3 — Escalation (approximately 6–8 seconds)

**Suggested camera:** Perspective, framing, and movement.

Prompt

**Cut to Scene 4:** Brief transition logic.

### Scene 4 — Encounter (approximately 7–9 seconds)

**Suggested camera:** Perspective, framing, and movement.

Prompt

**Cut to Scene 5:** Brief transition logic.

### Scene 5 — Unresolved ending (approximately 6–8 seconds)

**Suggested camera:** Perspective, framing, and movement.

Prompt

Do not let the template override the user's sequence, shot count, viewpoint, or narrative intent.
