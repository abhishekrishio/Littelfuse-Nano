"""
# =============================================================================
# MEASUREMENTS  (all in mm)
# =============================================================================

BODY_LENGTH = 10.62
BODY_WIDTH  =  5.03
BODY_HEIGHT =  4.24

CLIP_PAD_LENGTH = 3.81
CLIP_PAD_HEIGHT = 2.13
CLIP_THICKNESS  = 0.25

BODY_BOTTOM_Z = CLIP_PAD_HEIGHT
BODY_TOP_Z    = BODY_BOTTOM_Z + BODY_HEIGHT

SLOT_LENGTH = 8.60
SLOT_WIDTH  = 2.80
SLOT_DEPTH  = 3.10

FUSE_LENGTH = 8.50
FUSE_WIDTH  = 2.54
FUSE_HEIGHT = 3.56

# =============================================================================
# TRIANGLE STORE
# =============================================================================

all_triangles = []

# =============================================================================
# GEOMETRY HELPERS
# =============================================================================

def add_triangle(p1, p2, p3):
    """Compute outward normal and store triangle.  Points in CCW order from outside."""
    ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
    bx, by, bz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
    nx = ay*bz - az*by
    ny = az*bx - ax*bz
    nz = ax*by - ay*bx
    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    if length > 1e-6:
        nx, ny, nz = nx/length, ny/length, nz/length
    all_triangles.append(((nx, ny, nz), p1, p2, p3))


def add_quad(p1, p2, p3, p4):
    """Split a CCW quad into two triangles.
         p1──p4
         │    │
         p2──p3
    """
    add_triangle(p1, p2, p3)
    add_triangle(p1, p3, p4)


def add_box(cx, cy, cz, length, width, height):
    """Solid axis-aligned box centred at (cx, cy, cz)."""
    x0, x1 = cx - length/2, cx + length/2
    y0, y1 = cy - width/2,  cy + width/2
    z0, z1 = cz - height/2, cz + height/2

    add_quad((x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1))  # top    Z+
    add_quad((x0,y1,z0), (x1,y1,z0), (x1,y0,z0), (x0,y0,z0))  # bottom Z-
    add_quad((x1,y0,z0), (x1,y0,z1), (x1,y1,z1), (x1,y1,z0))  # right  X+
    add_quad((x0,y1,z0), (x0,y1,z1), (x0,y0,z1), (x0,y0,z0))  # left   X-
    add_quad((x0,y1,z0), (x1,y1,z0), (x1,y1,z1), (x0,y1,z1))  # front  Y+
    add_quad((x1,y0,z0), (x0,y0,z0), (x0,y0,z1), (x1,y0,z1))  # back   Y-


def add_box_with_slot_on_top(
        center_x, center_y, bottom_z, length, width, height,
        slot_cx, slot_cy, slot_length, slot_width, slot_depth):
    """Box with a rectangular through-slot cut into its top face."""

    x0, x1 = center_x - length/2, center_x + length/2
    y0, y1 = center_y - width/2,  center_y + width/2
    z0, z1 = bottom_z,            bottom_z + height

    sx0, sx1 = slot_cx - slot_length/2, slot_cx + slot_length/2
    sy0, sy1 = slot_cy - slot_width/2,  slot_cy + slot_width/2
    sz = z1 - slot_depth   # slot floor Z

    # Bottom (solid)
    add_quad((x0,y0,z0), (x1,y0,z0), (x1,y1,z0), (x0,y1,z0))

    # Top: 4 strips around the slot opening
    add_quad((x0,y0,z1), (x1,y0,z1), (x1,sy0,z1), (x0,sy0,z1))   # back strip
    add_quad((x0,sy1,z1), (x1,sy1,z1), (x1,y1,z1), (x0,y1,z1))   # front strip
    add_quad((x0,sy0,z1), (sx0,sy0,z1), (sx0,sy1,z1), (x0,sy1,z1)) # left strip
    add_quad((sx1,sy0,z1), (x1,sy0,z1), (x1,sy1,z1), (sx1,sy1,z1)) # right strip

    # 4 outer side walls
    add_quad((x0,y0,z0), (x0,y0,z1), (x1,y0,z1), (x1,y0,z0))   # back
    add_quad((x1,y0,z0), (x1,y0,z1), (x1,y1,z1), (x1,y1,z0))   # right
    add_quad((x1,y1,z0), (x1,y1,z1), (x0,y1,z1), (x0,y1,z0))   # front
    add_quad((x0,y1,z0), (x0,y1,z1), (x0,y0,z1), (x0,y0,z0))   # left

    # Slot floor
    add_quad((sx0,sy0,sz), (sx1,sy0,sz), (sx1,sy1,sz), (sx0,sy1,sz))

    # 4 inner slot walls
    add_quad((sx0,sy0,sz), (sx0,sy0,z1), (sx1,sy0,z1), (sx1,sy0,sz))  # back inner
    add_quad((sx1,sy0,sz), (sx1,sy0,z1), (sx1,sy1,z1), (sx1,sy1,sz))  # right inner
    add_quad((sx1,sy1,sz), (sx1,sy1,z1), (sx0,sy1,z1), (sx0,sy1,sz))  # front inner
    add_quad((sx0,sy1,sz), (sx0,sy1,z1), (sx0,sy0,z1), (sx0,sy0,sz))  # left inner

# =============================================================================
# BUILD THE MODEL
# =============================================================================

print("Building plastic housing...")
add_box_with_slot_on_top(
    center_x=0, center_y=0, bottom_z=BODY_BOTTOM_Z,
    length=BODY_LENGTH, width=BODY_WIDTH, height=BODY_HEIGHT,
    slot_cx=0, slot_cy=0,
    slot_length=SLOT_LENGTH, slot_width=SLOT_WIDTH, slot_depth=SLOT_DEPTH
)

print("Building metal clips...")
for side in (-1, +1):
    pad_cx = side * (BODY_LENGTH/2 - CLIP_PAD_LENGTH/2)

    # 1. Flat SMD pad
    add_box(pad_cx, 0, CLIP_THICKNESS/2,
            CLIP_PAD_LENGTH, BODY_WIDTH, CLIP_THICKNESS)

    # 2. Front side wall
    add_box(pad_cx, BODY_WIDTH/2 - CLIP_THICKNESS/2,
            CLIP_THICKNESS + CLIP_PAD_HEIGHT/2,
            CLIP_PAD_LENGTH, CLIP_THICKNESS, CLIP_PAD_HEIGHT)

    # 3. Back side wall
    add_box(pad_cx, -(BODY_WIDTH/2 - CLIP_THICKNESS/2),
            CLIP_THICKNESS + CLIP_PAD_HEIGHT/2,
            CLIP_PAD_LENGTH, CLIP_THICKNESS, CLIP_PAD_HEIGHT)

    # 4. Outer end wall (full height)
    total_clip_height = CLIP_PAD_HEIGHT + BODY_HEIGHT
    end_wall_x = side * BODY_LENGTH/2 + side * CLIP_THICKNESS/2
    add_box(end_wall_x, 0,
            CLIP_THICKNESS + total_clip_height/2,
            CLIP_THICKNESS, BODY_WIDTH, total_clip_height)

    # 5. Top retainer bar
    add_box(pad_cx, 0, BODY_TOP_Z + CLIP_THICKNESS/2,
            CLIP_PAD_LENGTH, BODY_WIDTH, CLIP_THICKNESS)

print("Building fuse element...")
fuse_center_z = BODY_BOTTOM_Z + BODY_HEIGHT - SLOT_DEPTH + FUSE_HEIGHT/2
add_box(0, 0, fuse_center_z, FUSE_LENGTH, FUSE_WIDTH, FUSE_HEIGHT)

# =============================================================================
# SAVE STL
# =============================================================================

def save_stl(filename, triangles):
    """Write a binary STL file."""
    header = b"Littelfuse Nano2 154 - STL generator".ljust(80, b"\x00")
    with open(filename, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(triangles)))
        for (normal, p1, p2, p3) in triangles:
            f.write(struct.pack("<fff", *normal))
            f.write(struct.pack("<fff", *p1))
            f.write(struct.pack("<fff", *p2))
            f.write(struct.pack("<fff", *p3))
            f.write(b"\x00\x00")

    size_kb = os.path.getsize(filename) / 1024     # FIX: was `littlefuse` (NameError)
    print(f"Saved : {filename}")
    print(f"  Triangles : {len(triangles)}")
    print(f"  File size : {size_kb:.1f} KB")


output_file = "/home/claude/littelfuse_nano2_154.stl"   # FIX: portable path (was Windows)
save_stl(output_file, all_triangles)

print()
print("=== Model Summary ===")
print(f"Plastic body : {BODY_LENGTH} x {BODY_WIDTH} x {BODY_HEIGHT} mm")
print(f"Fuse slot    : {SLOT_LENGTH} x {SLOT_WIDTH} x {SLOT_DEPTH} mm deep")
print(f"Contact pads : {CLIP_PAD_LENGTH} x {BODY_WIDTH} x {CLIP_THICKNESS} mm")
print(f"Total height : 0 to {BODY_TOP_Z + CLIP_THICKNESS:.2f} mm")
print("Done!")
