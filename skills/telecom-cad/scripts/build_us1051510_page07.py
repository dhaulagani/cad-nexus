r"""
build_us1051510_page07.py
Builds clean, precise Tower Elevation drawing for Site US1051510 (Denio)
- Based on survey sketch: Elevation.jpeg and US1051510_Denio_Elevation Table.xlsx
- 2-section tapered monopole:
  * Section 1 (S1): 0.00' to 18.53' (Height = 18.53', Base Dia = 2.53', Top Dia = 1.95')
  * Section 2 (S2): 18.53' to 63.00' (Height = 44.47', Base Dia = 1.95', Top Dia = 1.33')
  * Lightning Arrester: Height = 15.89', Top Elevation = 78.89'
- All inputs in decimal feet (no feet-inch)
- Standalone drawing object (no kop), fit to paper
- Output to: O:\Documents\Document Gani\Project\Uirtus\output_automated\US1051510_Denio\Page-07\
"""

import os
import math
import subprocess
import pymupdf
from PIL import Image, ImageChops
import ezdxf

template_dxf = r"c:\Apps\cad\Page-07.dxf"
out_dir = r"O:\Documents\Document Gani\Project\Uirtus\output_automated\US1051510_Denio\Page-07"
os.makedirs(out_dir, exist_ok=True)

out_dxf = os.path.join(out_dir, "US1051510_Denio_Page-07.dxf")
out_dwg = os.path.join(out_dir, "US1051510_Denio_Page-07.dwg")
out_pdf = os.path.join(out_dir, "US1051510_Denio_Page-07.pdf")
out_png = os.path.join(out_dir, "US1051510_Denio_Page-07.png")
scr_path = os.path.join(out_dir, "plot_us1051510_page07.scr")

doc = ezdxf.readfile(template_dxf)
msp = doc.modelspace()

# ==============================================================================
# 1. SURVEY PARAMETERS (US1051510 Denio)
# ==============================================================================
# Diameters & Radii in inches:
# Base (0.00'):   dia 2.53' = 30.36" -> r = 15.18"
# Mid (18.53'):   dia 1.95' = 23.40" -> r = 11.70"
# Top (63.00'):   dia 1.33' = 15.96" -> r = 7.98"
r_base = 15.18
r_mid = 11.70
r_top = 7.98

# Heights in inches:
# Datum 0.00' is at foundation top Y = 1148.40 (block Y = 5.0)
h_s1_in = 18.53 * 12.0         # 222.36"
h_s2_in = 44.47 * 12.0         # 533.64"
h_struct_in = 63.00 * 12.0     # 756.00"
h_arrester_in = 78.89 * 12.0   # 946.68"

y_0 = 1148.40
y_mid = y_0 + h_s1_in          # 1370.76
y_top = y_0 + h_struct_in      # 1904.40
y_arr = y_0 + h_arrester_in    # 2095.08

# Block local Y:
yb_base = 7.0                      # Datum 0.00' (top of base plate)
yb_mid = yb_base + h_s1_in         # 229.36 (Joint S1-S2)
yb_top = yb_base + h_struct_in     # 763.00 (Puncak tiang)
yb_arr = yb_base + h_arrester_in   # 953.68 (Puncak lightning arrester)

# ==============================================================================
# 2. UPDATE MP-60_2 BLOCK (US1051510 Geometry - 2 Tapered Sections)
# ==============================================================================
block_mp = doc.blocks.get('MP-60_2')
for e in list(block_mp):
    block_mp.delete_entity(e)

# Foundation box (34" wide, Y=0 to 5.0)
block_mp.add_line((-17.0, 5.0, 0), (17.0, 5.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((17.0, 5.0, 0), (17.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((17.0, 0.0, 0), (-17.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-17.0, 0.0, 0), (-17.0, 5.0, 0), dxfattribs={'layer': '0'})

# Base plate (Y=5.0 to 7.0, 34" wide)
block_mp.add_lwpolyline(
    [(17.0, 5.0), (-17.0, 5.0), (-17.0, 7.0), (17.0, 7.0)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Anchor bolts
if 'Bolt2' in doc.blocks:
    for bx in [0.0, 9.5, 13.5, -9.5, -13.5]:
        block_mp.add_blockref('Bolt2', (bx, 7.0, 0), dxfattribs={'layer': 'MP'})

# Outer profile lines:
# Section 1 (tapered from r_base to r_mid)
block_mp.add_line((r_base, yb_base, 0), (r_mid, yb_mid, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_base, yb_base, 0), (-r_mid, yb_mid, 0), dxfattribs={'layer': '0'})

# Joint / Flange connection between S1 & S2 at yb_mid
block_mp.add_line((-r_mid - 0.6, yb_mid, 0), (r_mid + 0.6, yb_mid, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_mid - 0.6, yb_mid - 0.6, 0), (r_mid + 0.6, yb_mid - 0.6, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_mid - 0.6, yb_mid - 0.6, 0), (-r_mid - 0.6, yb_mid, 0), dxfattribs={'layer': '0'})
block_mp.add_line((r_mid + 0.6, yb_mid - 0.6, 0), (r_mid + 0.6, yb_mid, 0), dxfattribs={'layer': '0'})

# Section 2 (tapered from r_mid to r_top)
block_mp.add_line((r_mid, yb_mid, 0), (r_top, yb_top, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_mid, yb_mid, 0), (-r_top, yb_top, 0), dxfattribs={'layer': '0'})

# Top cap
block_mp.add_lwpolyline(
    [(-r_top, yb_top), (r_top, yb_top), (r_top, yb_top + 0.5), (-r_top, yb_top + 0.5)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Lightning Arrester rod (from top cap to yb_arr)
block_mp.add_line((0.0, yb_top + 0.5, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})
# Arrester tip
block_mp.add_line((-0.5, yb_arr - 1.2, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})
block_mp.add_line((0.5, yb_arr - 1.2, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})

# Centerline (axis) on layer Hatch
block_mp.add_line((0.0, yb_base, 0), (0.0, yb_arr + 10.0, 0), dxfattribs={'layer': 'Hatch'})

# 18-sided polygon facets in elevation
for angle_deg in [20.0, 40.0, 60.0, 80.0]:
    c = math.cos(math.radians(angle_deg))
    xb = r_base * c
    xm = r_mid * c
    xt = r_top * c
    # S1 facets
    block_mp.add_line((xb, yb_base, 0), (xm, yb_mid, 0), dxfattribs={'layer': 'Hatch'})
    block_mp.add_line((-xb, yb_base, 0), (-xm, yb_mid, 0), dxfattribs={'layer': 'Hatch'})
    # S2 facets
    block_mp.add_line((xm, yb_mid, 0), (xt, yb_top, 0), dxfattribs={'layer': 'Hatch'})
    block_mp.add_line((-xm, yb_mid, 0), (-xt, yb_top, 0), dxfattribs={'layer': 'Hatch'})

print("[1] Configured MP-60_2 block for US1051510 (2 tapered sections + joint + lightning arrester).")

# ==============================================================================
# 3. UPDATE MP-60_2_Top BLOCK (Tampak Atas Pole US1051510)
# ==============================================================================
block_top = doc.blocks.get('MP-60_2_Top')
for e in list(block_top):
    block_top.delete_entity(e)

r_flange = 17.0
r_bolts = 14.5

# Base flange circle
block_top.add_circle((0.0, 0.0, 0), radius=r_flange, dxfattribs={'layer': '0'})
# Bolt circle line
block_top.add_circle((0.0, 0.0, 0), radius=r_bolts, dxfattribs={'layer': 'Hatch'})

# 12 Anchor bolts
for i in range(12):
    ang = i * (2.0 * math.pi / 12.0)
    block_top.add_circle((r_bolts * math.cos(ang), r_bolts * math.sin(ang), 0), radius=0.75, dxfattribs={'layer': '0'})

# 18-sided polygon base, mid, and top
poly_base = []
poly_mid = []
poly_top = []
for i in range(18):
    ang = i * (2.0 * math.pi / 18.0)
    poly_base.append((r_base * math.cos(ang), r_base * math.sin(ang)))
    poly_mid.append((r_mid * math.cos(ang), r_mid * math.sin(ang)))
    poly_top.append((r_top * math.cos(ang), r_top * math.sin(ang)))

block_top.add_lwpolyline(poly_base, close=True, dxfattribs={'layer': '0'})
block_top.add_lwpolyline(poly_mid, close=True, dxfattribs={'layer': 'Hatch'})
block_top.add_lwpolyline(poly_top, close=True, dxfattribs={'layer': '0'})

# Center lightning rod circle
block_top.add_circle((0.0, 0.0, 0), radius=1.0, dxfattribs={'layer': '0'})

# Crosshairs
block_top.add_line((-r_flange * 1.15, 0.0, 0), (r_flange * 1.15, 0.0, 0), dxfattribs={'layer': 'Hatch'})
block_top.add_line((0.0, -r_flange * 1.15, 0), (0.0, r_flange * 1.15, 0), dxfattribs={'layer': 'Hatch'})

print("[2] Configured MP-60_2_Top block for US1051510.")

# ==============================================================================
# 4. UPDATE MODELSPACE TABLE & BENCHMARKS
# ==============================================================================
entities_to_delete = []

def clear_bg_fill(entity):
    for attr in ['bg_fill', 'bg_fill_color', 'box_fill_scale', 'bg_fill_transparency']:
        entity.dxf.discard(attr)

# 4.1 Delete residual underline DF85D
e_df85d = doc.entitydb.get('DF85D')
if e_df85d:
    entities_to_delete.append(e_df85d)

# 4.2 Fix Footing Foundation Hatch BA51E (thin hatch line instead of black blob)
h_ba51e = doc.entitydb.get('BA51E')
if h_ba51e:
    h_ba51e.dxf.layer = 'Hatch'
    h_ba51e.dxf.pattern_scale = 25.0

# 4.3 Update Table Lines (B91EB, B91EC, B91ED, B91F2, B91F5)
for handle in ['B91EB', 'B91EC', 'B91ED']:
    ent = doc.entitydb.get(handle)
    if ent and ent.dxftype() == 'LWPOLYLINE':
        pts = ent.get_points()
        x_col = pts[0][0]
        ent.set_points([(x_col, 1148.40), (x_col, y_mid), (x_col, y_top)])

# Middle divider line (B91F2)
ent_mid = doc.entitydb.get('B91F2')
if ent_mid and ent_mid.dxftype() == 'LWPOLYLINE':
    ent_mid.set_points([(19262.31, y_mid), (19319.21, y_mid)])

# Top border line (B91F5)
ent_top = doc.entitydb.get('B91F5')
if ent_top and ent_top.dxftype() == 'LWPOLYLINE':
    ent_top.set_points([(19262.31, y_top), (19319.21, y_top)])

# 4.4 Elevation Benchmarks (Leaders, Ticks, Lines)
# 18.53' Benchmark Entities: BA511 (line), BA50E (tick), BA50F (leader)
ent = doc.entitydb.get('BA511')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19616.51, y_mid), (19670.78, y_mid)])

ent = doc.entitydb.get('BA50E')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19636.52, y_mid), (19631.21, y_mid + 6.09)])

ent = doc.entitydb.get('BA50F')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19636.52, y_mid), (19652.08, y_mid + 13.55), (19699.76, y_mid + 13.55)])

# 63.00' Benchmark Entities: BA519 (line), BA516 (tick), BA517 (leader)
ent = doc.entitydb.get('BA519')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19616.51, y_top), (19670.78, y_top)])

ent = doc.entitydb.get('BA516')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19636.52, y_top), (19631.21, y_top + 6.09)])

ent = doc.entitydb.get('BA517')
if ent and ent.dxftype() == 'LWPOLYLINE':
    ent.set_points([(19636.52, y_top), (19652.08, y_top + 13.55), (19699.76, y_top + 13.55)])

# 78.89' Benchmark Entities (Top of Lightning Arrester)
# Horizontal benchmark tick across at y_arr
msp.add_lwpolyline([(19616.51, y_arr), (19670.78, y_arr)], dxfattribs={'layer': 'Layer Table'})
# Small 45-degree pointer tick
msp.add_lwpolyline([(19636.52, y_arr), (19631.21, y_arr + 6.09)], dxfattribs={'layer': 'Layer Table'})
# Leader line to text
msp.add_lwpolyline([(19636.52, y_arr), (19652.08, y_arr + 13.55), (19699.76, y_arr + 13.55)], dxfattribs={'layer': 'Layer Table'})

# Elevation Benchmark Texts
for e in msp:
    if e.dxftype() == 'MTEXT':
        handle = e.dxf.handle.upper()
        if handle == 'BA46B':
            e.dxf.text = r"\A1;\pxqr;0.00'"
            e.dxf.insert = (19654.67, 1169.50, 0)
            clear_bg_fill(e)
        elif handle == 'BA510':
            e.dxf.text = r"\A1;\pxqr;18.53'"
            e.dxf.insert = (19654.67, y_mid + 20.55, 0)
            clear_bg_fill(e)
        elif handle == 'BA518':
            e.dxf.text = r"\A1;\pxqr;63.00'"
            e.dxf.insert = (19654.67, y_top + 20.55, 0)
            clear_bg_fill(e)

# MTEXT for 78.89'
txt_arr = msp.add_mtext(
    r"\A1;\pxqr;78.89'",
    dxfattribs={
        'layer': 'Layer Table',
        'char_height': 6.0,
        'insert': (19654.67, y_arr + 20.55, 0),
        'attachment_point': 1
    }
)
clear_bg_fill(txt_arr)

# 4.5 Table Cell Centers
y_s1_center = (y_0 + y_mid) / 2.0  # 1259.58
y_s2_center = (y_mid + y_top) / 2.0 # 1637.58

for e in msp:
    if e.dxftype() == 'MTEXT':
        txt = getattr(e.dxf, 'text', '')
        if 'SECTION' in txt:
            e.dxf.text = r"\pxqc;SECTION"
            e.dxf.insert = (19276.54, 1119.88, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif 'LEG (DIA.)' in txt:
            e.dxf.text = r"\pxqc;LEG (DIA.)"
            e.dxf.insert = (19304.99, 1119.88, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 3.5
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif txt.strip() in [r"\A1;1", "1"]:
            e.dxf.text = r"\A1;1"
            e.dxf.insert = (19276.54, y_s1_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 5.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif txt.strip() in [r"\A1;2", "2"]:
            e.dxf.text = r"\A1;2"
            e.dxf.insert = (19276.54, y_s2_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 5.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        # S1 diameter: 2.53' / 1.95'
        elif "2.76'" in txt:
            e.dxf.text = r"\A1;%%C2.53' / %%C1.95'"
            e.dxf.insert = (19304.99, y_s1_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        # S2 diameter: 1.95' / 1.33'
        elif "1.27'" in txt or "1.48'" in txt:
            e.dxf.text = r"\A1;%%C1.95' / %%C1.33'"
            e.dxf.insert = (19304.99, y_s2_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif 'Note:' in txt:
            e.dxf.text = r"Note: Monopole structure with tapered leg connection\Pfrom section 1 to section 2."
            e.dxf.insert = (19535.00, y_s2_center + 40.0, 0)
            e.dxf.width = 0.0
            clear_bg_fill(e)

# ==============================================================================
# 5. UPDATE DIMENSIONS (Decimal Feet Only)
# ==============================================================================
for e in msp:
    if e.dxftype() == 'DIMENSION':
        handle = e.dxf.handle.upper()
        geom_name = getattr(e.dxf, 'geometry', '')
        geom_block = doc.blocks.get(geom_name) if geom_name else None

        # Delete duplicate feet-inch dimensions
        if handle in ['D98B5', 'DCDA9', 'DCDBF', 'DCF04']:
            entities_to_delete.append(e)

        # 5.1 Total Pole Height: B9204 (63.00')
        elif handle == 'B9204':
            e.dxf.layer = 'Dim'
            e.dxf.text = "63.00'"
            e.dxf.defpoint = (19356.25, y_top, 0)
            e.dxf.defpoint3 = (19470.00, y_top, 0)
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;63.00'"
                        be.dxf.insert = (be.dxf.insert.x, (y_0 + y_top) / 2.0, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if abs(be.dxf.insert.y - 1868.40) < 15.0:
                            be.dxf.insert = (be.dxf.insert.x, y_top, 0)
                    elif be.dxftype() == 'LINE':
                        # Upper extension line
                        if abs(be.dxf.start.y - 1868.40) < 5.0 and abs(be.dxf.end.y - 1868.40) < 5.0:
                            be.dxf.start = (be.dxf.start.x, y_top, 0)
                            be.dxf.end = (be.dxf.end.x, y_top, 0)
                        # Vertical dimension line
                        elif abs(be.dxf.start.x - 19356.25) < 2.0 and abs(be.dxf.end.x - 19356.25) < 2.0:
                            be.dxf.start = (19356.25, 1142.68, 0)
                            be.dxf.end = (19356.25, y_top + 5.72, 0)

        # 5.2 Section 1 Height: B921C (18.53')
        elif handle == 'B921C':
            e.dxf.layer = 'Dim'
            e.dxf.text = "18.53'"
            e.dxf.defpoint = (19404.50, y_mid, 0)
            e.dxf.defpoint3 = (19428.12, y_mid, 0)
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;18.53'"
                        be.dxf.insert = (be.dxf.insert.x, y_s1_center, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if abs(be.dxf.insert.y - 1460.40) < 15.0:
                            be.dxf.insert = (be.dxf.insert.x, y_mid, 0)
                    elif be.dxftype() == 'LINE':
                        # Upper extension line
                        if abs(be.dxf.start.y - 1460.40) < 5.0 and abs(be.dxf.end.y - 1460.40) < 5.0:
                            be.dxf.start = (be.dxf.start.x, y_mid, 0)
                            be.dxf.end = (be.dxf.end.x, y_mid, 0)
                        # Vertical dimension line
                        elif abs(be.dxf.start.x - 19404.50) < 2.0 and abs(be.dxf.end.x - 19404.50) < 2.0:
                            be.dxf.start = (19404.50, 1142.68, 0)
                            be.dxf.end = (19404.50, y_mid + 5.72, 0)

        # 5.3 Section 2 Height: B9234 (44.47')
        elif handle == 'B9234':
            e.dxf.layer = 'Dim'
            e.dxf.text = "44.47'"
            e.dxf.defpoint = (19404.50, y_top, 0)
            e.dxf.defpoint2 = (19428.12, y_mid, 0)
            e.dxf.defpoint3 = (19428.12, y_top, 0)
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;44.47'"
                        be.dxf.insert = (be.dxf.insert.x, y_s2_center, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if abs(be.dxf.insert.y - 1460.40) < 15.0:
                            be.dxf.insert = (be.dxf.insert.x, y_mid, 0)
                        elif abs(be.dxf.insert.y - 1868.40) < 15.0:
                            be.dxf.insert = (be.dxf.insert.x, y_top, 0)
                    elif be.dxftype() == 'LINE':
                        # Lower extension line
                        if abs(be.dxf.start.y - 1460.40) < 5.0 and abs(be.dxf.end.y - 1460.40) < 5.0:
                            be.dxf.start = (be.dxf.start.x, y_mid, 0)
                            be.dxf.end = (be.dxf.end.x, y_mid, 0)
                        # Upper extension line
                        elif abs(be.dxf.start.y - 1868.40) < 5.0 and abs(be.dxf.end.y - 1868.40) < 5.0:
                            be.dxf.start = (be.dxf.start.x, y_top, 0)
                            be.dxf.end = (be.dxf.end.x, y_top, 0)
                        # Vertical dimension line
                        elif abs(be.dxf.start.x - 19404.50) < 2.0 and abs(be.dxf.end.x - 19404.50) < 2.0:
                            be.dxf.start = (19404.50, y_mid - 5.72, 0)
                            be.dxf.end = (19404.50, y_top + 5.72, 0)

        # 5.4 Base Diameter: D7611 (2.53')
        elif handle == 'D7611':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 - r_base, 1120.20, 0)
            e.dxf.defpoint3 = (19500.00 + r_base, 1120.20, 0)
            e.dxf.defpoint = (19500.00 + r_base, 1103.60, 0)
            e.dxf.text = "2.53'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;2.53'"
                        be.dxf.insert = (19500.00, 1107.60, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if be.dxf.insert.x < 19500.0:
                            be.dxf.insert = (19500.00 - r_base, 1103.60, 0)
                        else:
                            be.dxf.insert = (19500.00 + r_base, 1103.60, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.y - 1103.60) < 1.0 and abs(be.dxf.end.y - 1103.60) < 1.0:
                            be.dxf.start = (19500.00 - r_base - 5.72, 1103.60, 0)
                            be.dxf.end = (19500.00 + r_base + 5.72, 1103.60, 0)
                        elif be.dxf.start.x < 19500.0:
                            be.dxf.start = (19500.00 - r_base, 1120.20, 0)
                            be.dxf.end = (19500.00 - r_base, 1097.90, 0)
                        elif be.dxf.start.x > 19500.0:
                            be.dxf.start = (19500.00 + r_base, 1120.20, 0)
                            be.dxf.end = (19500.00 + r_base, 1097.90, 0)

        # 5.5 Mid Diameter: D7AA3 (1.95')
        elif handle == 'D7AA3':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 - r_mid, y_mid, 0)
            e.dxf.defpoint3 = (19500.00 + r_mid, y_mid, 0)
            e.dxf.defpoint = (19500.00 + r_mid, y_mid, 0)
            e.dxf.text = "1.95'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.95'"
                        be.dxf.insert = (19525.00, y_mid + 4.0, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if be.dxf.insert.x < 19500.0:
                            be.dxf.insert = (19500.00 - r_mid, y_mid, 0)
                        else:
                            be.dxf.insert = (19500.00 + r_mid, y_mid, 0)
                    elif be.dxftype() == 'LINE':
                        # Horizontal line inside pole
                        if abs(be.dxf.start.y - 1460.40) < 2.0 and abs(be.dxf.end.y - 1460.40) < 2.0:
                            if be.dxf.start.x < 19500.0:
                                be.dxf.start = (19500.00 - r_mid - 5.72, y_mid, 0)
                                be.dxf.end = (19500.00 + r_mid, y_mid, 0)
                            else:
                                be.dxf.start = (19500.00 + r_mid, y_mid, 0)
                                be.dxf.end = (19500.00 + r_mid + 25.0, y_mid, 0)
                        # Vertical extension ticks
                        elif be.dxf.start.x < 19500.0:
                            be.dxf.start = (19500.00 - r_mid, y_mid + 1.4, 0)
                            be.dxf.end = (19500.00 - r_mid, y_mid + 5.72, 0)
                        elif be.dxf.start.x > 19500.0:
                            be.dxf.start = (19500.00 + r_mid, y_mid + 1.4, 0)
                            be.dxf.end = (19500.00 + r_mid, y_mid + 5.72, 0)

        # 5.6 Top Diameter: E01F4 (1.33')
        elif handle == 'E01F4':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 + r_top, y_top + 9.6, 0)
            e.dxf.defpoint3 = (19500.00 - r_top, y_top + 9.6, 0)
            e.dxf.defpoint = (19500.00 - r_top, y_top + 20.0, 0)
            e.dxf.text = "1.33'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.33'"
                        be.dxf.insert = (19522.60, y_top + 42.0, 0)
                    elif be.dxftype() == 'INSERT' and be.dxf.name == '_ArchTick':
                        if be.dxf.insert.x < 19500.0:
                            be.dxf.insert = (19500.00 - r_top, y_top + 38.0, 0)
                        else:
                            be.dxf.insert = (19500.00 + r_top, y_top + 38.0, 0)
                    elif be.dxftype() == 'LINE':
                        # Horizontal line
                        if abs(be.dxf.start.y - 1906.3) < 5.0 or abs(be.dxf.end.y - 1906.3) < 5.0:
                            if be.dxf.start.x < 19500.0:
                                be.dxf.start = (19500.00 - r_top, y_top + 38.0, 0)
                                be.dxf.end = (19500.00 + r_top + 5.0, y_top + 38.0, 0)
                            else:
                                be.dxf.start = (19500.00 + r_top, y_top + 38.0, 0)
                                be.dxf.end = (19500.00 + r_top + 24.0, y_top + 38.0, 0)
                        # Vertical extension lines
                        elif be.dxf.start.x < 19500.0:
                            be.dxf.start = (19500.00 - r_top, y_top + 11.0, 0)
                            be.dxf.end = (19500.00 - r_top, y_top + 44.0, 0)
                        elif be.dxf.start.x > 19500.0:
                            be.dxf.start = (19500.00 + r_top, y_top + 11.0, 0)
                            be.dxf.end = (19500.00 + r_top, y_top + 44.0, 0)

for e in entities_to_delete:
    msp.delete_entity(e)

print(f"[3] Cleaned entities and converted dimensions to survey decimal feet (2.53', 1.95', 1.33', 18.53', 44.47', 63.00').")

# ==============================================================================
# 6. VERIFY MP-60_2_Top AT (19500.00, 903.00)
# ==============================================================================
has_top_insert = False
for e in msp:
    if e.dxftype() == 'INSERT' and e.dxf.name == 'MP-60_2_Top':
        has_top_insert = True
        e.dxf.insert = (19500.00, 903.00, 0)

if not has_top_insert:
    msp.add_blockref('MP-60_2_Top', (19500.00, 903.00, 0), dxfattribs={'layer': '0'})

print("[4] Verified MP-60_2_Top block.")

# Save modified DXF
doc.saveas(out_dxf)
print(f"[5] Saved DXF to {out_dxf}")

# ==============================================================================
# 7. PLOT TO PDF (WINDOW PLOT AROUND TOWER OBJECTS ONLY, FIT TO PAPER, CRISP HAIRLINES)
# ==============================================================================
# Window bounding box:
# X: 19220.0 (left of table) to 19780.0 (right of elevation leader lines)
# Y: 850.0 (below MP-60_2_Top) to 2150.0 (above lightning arrester & 78.89' datum)
scr_lines = [
    '(setvar "EXPERT" 2)',
    '(setvar "CTAB" "Model")',
    '-PLOT',
    'Y',
    'Model',
    'AutoCAD PDF (General Documentation).pc3',
    'ANSI A (8.50 x 11.00 Inches)',
    'I',
    'P',
    'N',
    'W',
    '19220.0,850.0',
    '19780.0,2150.0',
    'Fit',
    'Center',
    'Y',
    'acad.ctb',
    'N',
    'N',
    f'"{out_pdf}"',
    'N',
    'Y',
    'SAVEAS',
    '2018',
    f'"{out_dwg}"',
    'QUIT',
    'Y'
]

with open(scr_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(scr_lines) + '\n')

print(f"[6] Written script to {scr_path}")

# Run accoreconsole
accoreconsole = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
cmd = [accoreconsole, "/i", out_dxf, "/s", scr_path]

print("[7] Running AutoCAD accoreconsole to generate genuine DWG and PDF...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(out_dwg):
    print(f" -> Successfully created DWG: {out_dwg} ({os.path.getsize(out_dwg)} bytes)")
else:
    print(" -> Warning: DWG not created.")

if os.path.exists(out_pdf):
    print(f" -> Successfully created PDF: {out_pdf} ({os.path.getsize(out_pdf)} bytes)")
else:
    print(" -> Warning: PDF not created.")

# ==============================================================================
# 8. RENDER HIGH-RES PNG FROM PDF (FIT TO PAPER & TIGHTLY CROPPED)
# ==============================================================================
if os.path.exists(out_pdf):
    print("[8] Rendering high-res PNG from PDF...")
    doc_pdf = pymupdf.open(out_pdf)
    page = doc_pdf[0]
    pix = page.get_pixmap(dpi=300)
    temp_png = out_png + ".raw.png"
    pix.save(temp_png)

    img = Image.open(temp_png).convert("RGB")
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        pad = 35
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(img.width, bbox[2] + pad)
        bottom = min(img.height, bbox[3] + pad)
        cropped = img.crop((left, top, right, bottom))
        cropped.save(out_png)
        print(f" -> Successfully generated cropped PNG: {out_png} ({cropped.size})")
    else:
        img.save(out_png)
        print(f" -> Saved full PNG: {out_png}")

    if os.path.exists(temp_png):
        os.remove(temp_png)

print("=== ALL PROCESSES COMPLETED FOR US1051510 (Denio) ===")
