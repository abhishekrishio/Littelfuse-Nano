# Littelfuse-Nano
# Littelfuse Nano2 154 — STL Generator

A pure-Python script that procedurally generates a binary STL file of the **Littelfuse Nano2 Series 154** miniature fuse holder, suitable for PCB 3D visualisation, assembly documentation, and CAD library use.

---

## Files

| File | Description |
|---|---|
| `littelfuse_fixed.py` | Main script — generates the STL |
| `littelfuse_nano2_154.stl` | Output STL produced by the script |

---

## Requirements

- Python 3.6 or higher
- No third-party packages — uses only the standard library (`math`, `os`, `struct`)

---

## Usage

```bash
python littelfuse_fixed.py
```

The script prints progress to the terminal and writes the STL file to the same directory:

```
Building plastic housing...
Building metal clips...
Building fuse element...
Saved : littelfuse_nano2_154.stl
  Triangles : 160
  File size : 7.9 KB

=== Model Summary ===
Plastic body : 10.62 x 5.03 x 4.24 mm
Fuse slot    : 8.6 x 2.8 x 3.1 mm deep
Contact pads : 3.81 x 5.03 x 0.25 mm
Total height : 0 to 6.62 mm
Done!
```

To change the output path, edit the `output_file` variable near the bottom of the script:

```python
output_file = "path/to/your/output.stl"
```

---

## Model Dimensions (mm)

All constants are defined at the top of the script and can be freely edited.

| Part | Parameter | Value (mm) |
|---|---|---|
| Plastic body | Length × Width × Height | 10.62 × 5.03 × 4.24 |
| Fuse slot | Length × Width × Depth | 8.60 × 2.80 × 3.10 |
| Metal clip pads | Length × Width × Thickness | 3.81 × 5.03 × 0.25 |
| Clip side walls | Height | 2.13 |
| Fuse element | Length × Width × Height | 8.50 × 2.54 × 3.56 |
| **Overall envelope** | **Length × Width × Height** | **11.12 × 5.03 × 6.62** |

The model is centred on the X/Y axes. The PCB surface sits at Z = 0.

---

## Model Structure

The model is composed of three parts built from axis-aligned box geometry:

```
┌─────────────────────────────────────────┐
│           Top retainer bars              │  ← thin bar clips over housing top
│  ┌──────────────────────────────────┐   │
│  │   Plastic housing + fuse slot    │   │  ← box with rectangular groove on top
│  └──────────────────────────────────┘   │
│           Clip side walls               │  ← front & back upright walls
│         Flat SMD solder pads            │  ← lies flat on PCB (Z=0)
└─────────────────────────────────────────┘
        Left clip          Right clip
```

**Part A — Plastic housing** (`add_box_with_slot_on_top`)
The main rectangular body with a rectangular slot cut into the top for the fuse element to sit in. Drawn by hand as individual faces (top ring, 4 sides, slot floor, 4 inner slot walls) instead of Boolean subtraction.

**Part B — Metal contact clips** (loop × 2)
Each clip consists of five boxes: a flat SMD pad, a front wall, a back wall, an outer end wall wrapping the housing end, and a top retainer bar.

**Part C — Fuse element** (`add_box`)
A simple box sitting inside the slot, representing the visible fuse glass/ceramic body.

---

## How It Works

The script builds geometry entirely from triangles stored in a list as `(normal, p1, p2, p3)` tuples, then writes them as a **binary STL** file.

```
add_triangle  ←  lowest level: computes outward normal + stores 1 triangle
add_quad      ←  splits a rectangle into 2 triangles
add_box       ←  6 quads = 12 triangles for a solid cuboid
add_box_with_slot_on_top  ←  custom face layout for slotted housing
```

**Binary STL format used:**

```
80 bytes   — header string
 4 bytes   — triangle count (uint32, little-endian)
50 bytes × N — per triangle:
    12 bytes  normal vector  (3 × float32)
    12 bytes  vertex 1       (3 × float32)
    12 bytes  vertex 2       (3 × float32)
    12 bytes  vertex 3       (3 × float32)
     2 bytes  attribute      (always 0x0000)
```

---

## Comparison with Reference CAD Model

A reference CAD file (`Littelfuse-Nano2-154.stl`) was used during development. Key differences:

| | Reference CAD | This Script |
|---|---|---|
| Units stored | Meters | Millimetres |
| Triangles | 2,726 | 160 |
| Geometry | Curved / chamfered | Box primitives |
| Length | 9.73 mm | 11.12 mm |
| Width | 3.81 mm | 5.03 mm |
| Height | 5.03 mm | 6.62 mm |

The generated model is intentionally simplified (no fillets, no curves) but correctly captures the overall topology — housing, clip metal work, and fuse element — making it suitable for clearance checking and PCB footprint validation.

---

## Bugs Fixed vs Original Script

| # | Bug | Fix Applied |
|---|---|---|
| 1 | `import struct` and `import os` missing at module level | Moved to top of file |
| 2 | `os.path.getsize(littlefuse)` — `littlefuse` was never defined (`NameError`) | Changed to `os.path.getsize(filename)` |
| 3 | `print(f"Saved: {littlefuse}")` — same undefined variable | Changed to `print(f"Saved: {filename}")` |
| 4 | Hard-coded Windows path `C:\Users\abhis\Desktop\...` | Replaced with portable relative path |
| 5 | `import math` called inside `calculate_normal` on every triangle | Moved to module level; normal calculation inlined into `add_triangle` |

---

## Customisation

All dimensions live in the constants block at the top of the script. To match a different fuse variant, adjust the values there — no other changes needed.

```python
BODY_LENGTH = 10.62   # change to match target part
BODY_WIDTH  =  5.03
BODY_HEIGHT =  4.24
# ... etc.
```

---

## License

This script was written for educational and documentation purposes.
Refer to the official [Littelfuse Nano2 Series datasheet](https://www.littelfuse.com) for certified dimensions before use in production PCB designs.
