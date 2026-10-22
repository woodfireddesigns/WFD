# Body map renders

Source of `img/body-*.webp` (sculpted render) and `img/body-*-id.png` (muscle group ID maps).

- Model: [Z-Anatomy](https://github.com/LluisV/Z-Anatomy) (CC BY-SA 4.0): `MuscularSystem100.fbx`,
  `SkeletalSystem100.fbx`, `Regions of human body100.fbx` from `Resources/Models/FBX/` on the `PC-Version` branch.
- Head: Lee Perry-Smith scan by Infinite Realities (CC BY 3.0), `examples/models/gltf/LeePerrySmith/LeePerrySmith.glb`
  in the three.js repo. Passed as `scanhead`; it replaces the atlas head and is trimmed to a neck column.
- Blender: `pip install bpy` (5.2, Python 3.13), run headless.
- `groups.py` maps anatomical muscle names to Kiln's 14 groups. ID value = (group index + 1) * 16.

```
COMMON='"fbx": ".../MuscularSystem100.fbx", "skel": ".../SkeletalSystem100.fbx", "skin": ".../Regions of human body100.fbx",
  "views": ["front", "back"], "res": [600, 1200], "head_z": 1.535, "core_dy": 0.015, "core_s": 0.84, "core_sy": 0.78, "eye_back": 2.6, "scanhead": ".../LeePerrySmith.glb",
  "neck_rx": 0.066, "neck_ry": 0.074, "scan_cut": 1.385, "back_cut": 1.44, "flush_band": 0.055,
  "neck_flare": 0.18, "neck_top": 1.535, "jaw_keep_x": 1.0, "masc": {"neck": 0, "jaw": 0, "chin": 0, "brow": 0, "dome": 1, "skull_w": 0}'
python -I render.py "{\"mode\": \"id\", \"out\": \"out\", $COMMON}"            # rename to *-id.png
python -I render.py "{\"mode\": \"beauty\", \"out\": \"out\", \"samples\": 128, \"light\": 0.28, \"clay\": [0.045,0.044,0.043], $COMMON}"
```

Then crop both views to the shared alpha bounding box (+6px), save beauty as WebP q84, and snap ID values to multiples of 16.
