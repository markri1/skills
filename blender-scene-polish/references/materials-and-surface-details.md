# Materials and surface details

## Read the material before modifying it

Check the shader and final light before deciding that a surface is wrong. A bright fleck may be a reflection, bump artifact or sampling noise rather than a color texture. Compare a neutral, temporary inspection render with the scene render when needed. Do not save inspection lights or cameras into the working scene unless requested.

Identify physical layers. Uncoated plastic, rubber, paper and ordinary dust are dielectrics; exposed metal may be metallic, while paint, oxide and dirt over that metal need their own response. Changing every material to one Metallic or Roughness value destroys those distinctions. Preserve deliberate stylization when the brief calls for it.

## Give wear an origin

- Contacts/protrusions: broken edge scuffs, rubbed corners, polished controls and impact marks.
- Face interiors: selected directional scratches, dragged objects, broad rubbed areas or local stains.
- Recesses/ledges: deposited dust and grime, with cleaner areas where handling has removed them.
- Repairs: adhesive ghosts, torn labels, replacement controls and occasional tape or fasteners.

Preserve quiet areas. Vary length, width, direction, age, depth and contrast; keep some objects lightly worn. Related marks from one incident often read better than uniform unrelated noise. A pristine product shot may instead need small manufacturing variation and controlled reflections, with no damage.

Color, roughness and relief should support the same event. Handling can polish a patch; a cut can have a dark recess and a lighter stressed edge. Plastic scratches do not expose a metallic substrate. Use shallow relief at the correct scale and inspect oblique lighting before increasing strength.

## Avoid repetition and swimming patterns

Choose coordinates deliberately. Object coordinates can suit local deposits; UVs or persistent attributes suit specific incidents. Keep new UVs separate from existing image-texture UVs. Preserve a physical mark when an object rotates or instances are duplicated.

Finite masks or sparse surface geometry can be easier to direct than dense noise. Derive mask dimensions/padding from UV layout and delivery resolution. Pack generated textures or place them in an explicit asset folder; verify reopening. Allocate per-object materials only when needed and preserve instancing elsewhere.

## Fit overlays and attached details

Inspect evaluated geometry when modifiers change the surface. Transform points and ray directions into target-local coordinates before ray casting; account for scale and transform normals correctly. Position the result in the attachment's space.

Choose clearance relative to scene units and feature size. Test plate/decal interiors as well as vertices so a flat detail cannot bridge a tapered or curved surface. Distinguish intentional protrusions from a floating backing. Avoid Z-fighting, excessive shadow gaps and clipping.

Inspect all users of shared meshes, materials and groups before editing them. Copy locally for variants that should not propagate. Preserve unrelated controls, connectors and screens. Recheck the silhouette and fitted attachments after geometry changes.
