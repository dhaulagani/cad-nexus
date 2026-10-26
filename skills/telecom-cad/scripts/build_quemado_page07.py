"""
build_quemado_page07_v4.py
Flawless execution of Quemado Monopole Page 7:
- All dimensions converted to survey decimal feet (no feet-inch)
- All geometry block entities set to layer 'Dim' so they plot
- Top pole aligned to 60.00' datum (Y = 1868.40)
- Top diameter 1.48' cleanly positioned with no duplicates
- Transition diameter 1.94' exactly on 25.00' datum (Y = 1448.40)
- Elevation benchmark texts raised above lines with no background mask
- Exact handle targeting for elevation benchmarks (BA46B=0.00', BA510=25.00', BA518=60.00')
- Table headers & section data centered inside cells without border collisions
- Multi-line wrap on middle note so it does not overflow
- Window plot from modelspace tightly focused on drawing objects (no kop)
- Outputs directly to Page-07 subfolder
"""

import os
import math
import subprocess
import pymupdf
from PIL import Image, ImageChops
import ezdxf

template_dxf = r"c:\Apps\cad\Page-07.dxf"
out_dir = r"O:\Documents\Document Gani\Project\Uirtus\output_automated\US1051600_Quemado\Page-07"
os.makedirs(out_dir, exist_ok=True)

out_dxf = os.path.join(out_dir, "US1051600_Quemado_Page-07.dxf")
out_dwg = os.path.join(out_dir, "US1051600_Quemado_Page-07.dwg")
out_pdf = os.path.join(out_dir, "US1051600_Quemado_Page-07.pdf")
out_png = os.path.join(out_dir, "US1051600_Quemado_Page-07.png")
scr_path = os.path.join(out_dir, "plot_quemado_page07.scr")

doc = ezdxf.readfile(template_dxf)
msp = doc.modelspace()

# ==============================================================================
# 1. UPDATE MP-60_2 BLOCK (Quemado Monopole Elevation Geometry)
# ==============================================================================
block_mp = doc.blocks.get('MP-60_2')
for e in list(block_mp):
    block_mp.delete_entity(e)

# Foundation box (36" wide, Y=0 to 5.0)
block_mp.add_line((-18.0, 5.0, 0), (18.0, 5.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((18.0, 5.0, 0), (18.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((18.0, 0.0, 0), (-18.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-18.0, 0.0, 0), (-18.0, 5.0, 0), dxfattribs={'layer': '0'})

# Base plate (Y=5.0 to 7.0, 30" wide)
block_mp.add_lwpolyline(
    [(15.0, 5.0), (-15.0, 5.0), (-15.0, 7.0), (15.0, 7.0)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Anchor bolts
if 'Bolt2' in doc.blocks:
    for bx in [0.0, 10.0, 13.5, -10.0, -13.5]:
        block_mp.add_blockref('Bolt2', (bx, 7.0, 0), dxfattribs={'layer': 'MP'})

# Survey Radii in inches (Quemado):
# Base: dia 2.14' = 25.68" -> r = 12.84"
# Transition (25.00'): dia 1.94' = 23.28" -> r = 11.64"
# Top (60.00'): dia 1.48' = 17.76" -> r = 8.88"
r_base = 12.84
r_trans = 11.64
r_top = 8.88

# Exact Y levels inside block:
# Datum 0.00' is at foundation top Y = 5.0
# Section 1 transition (25.00' = 300") -> Y = 5.0 + 300.0 = 305.0
# Top of pole (60.00' = 720") -> Y = 5.0 + 720.0 = 725.0
y_b = 7.0     # Base of pole shaft (top of base plate)
y_tr = 305.0  # Transition splice line (exactly at 25.00' datum)
y_t = 725.0   # Top of pole shaft (exactly at 60.00' datum)

# Outer profile lines
# Section 1
block_mp.add_line((r_base, y_b, 0), (r_trans, y_tr, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_base, y_b, 0), (-r_trans, y_tr, 0), dxfattribs={'layer': '0'})
# Section 2
block_mp.add_line((r_trans, y_tr, 0), (r_top, y_t, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_trans, y_tr, 0), (-r_top, y_t, 0), dxfattribs={'layer': '0'})

# Transition joint line
block_mp.add_line((-r_trans, y_tr, 0), (r_trans, y_tr, 0), dxfattribs={'layer': '0'})

# Top cap (from y_t to y_t + 0.4)
block_mp.add_lwpolyline(
    [(-r_top, y_t), (r_top, y_t), (r_top, y_t + 0.4), (-r_top, y_t + 0.4)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Centerline (axis) on layer Hatch
block_mp.add_line((0.0, y_b, 0), (0.0, y_t + 9.0, 0), dxfattribs={'layer': 'Hatch'})

# 18-sided polygon facets in elevation
for angle_deg in [20.0, 40.0, 60.0, 80.0]:
    c = math.cos(math.radians(angle_deg))
    xb = r_base * c
    xtr = r_trans * c
    xt = r_top * c
    # Right facets
    block_mp.add_line((xb, y_b, 0), (xtr, y_tr, 0), dxfattribs={'layer': 'Hatch'})
    block_mp.add_line((xtr, y_tr, 0), (xt, y_t, 0), dxfattribs={'layer': 'Hatch'})
    # Left facets
    block_mp.add_line((-xb, y_b, 0), (-xtr, y_tr, 0), dxfattribs={'layer': 'Hatch'})
    block_mp.add_line((-xtr, y_tr, 0), (-xt, y_t, 0), dxfattribs={'layer': 'Hatch'})

print("[1] Configured MP-60_2 block with exact datum alignments.")

# ==============================================================================
# 2. UPDATE MP-60_2_Top BLOCK (Tampak Atas Pole)
# ==============================================================================
block_top = doc.blocks.get('MP-60_2_Top')
for e in list(block_top):
    block_top.delete_entity(e)

r_flange = 17.5
r_bolts = 15.0

# Base flange circle
block_top.add_circle((0.0, 0.0, 0), radius=r_flange, dxfattribs={'layer': '0'})
# Bolt circle line
block_top.add_circle((0.0, 0.0, 0), radius=r_bolts, dxfattribs={'layer': 'Hatch'})

# 12 Anchor bolts
for i in range(12):
    ang = i * (2.0 * math.pi / 12.0)
    block_top.add_circle((r_bolts * math.cos(ang), r_bolts * math.sin(ang), 0), radius=0.8, dxfattribs={'layer': '0'})

# 18-sided polygon base and top
poly_base = []
poly_top = []
for i in range(18):
    ang = i * (2.0 * math.pi / 18.0)
    poly_base.append((r_base * math.cos(ang), r_base * math.sin(ang)))
    poly_top.append((r_top * math.cos(ang), r_top * math.sin(ang)))

block_top.add_lwpolyline(poly_base, close=True, dxfattribs={'layer': '0'})
block_top.add_lwpolyline(poly_top, close=True, dxfattribs={'layer': '0'})

# Crosshairs
block_top.add_line((-r_flange * 1.15, 0.0, 0), (r_flange * 1.15, 0.0, 0), dxfattribs={'layer': 'Hatch'})
block_top.add_line((0.0, -r_flange * 1.15, 0), (0.0, r_flange * 1.15, 0), dxfattribs={'layer': 'Hatch'})

print("[2] Configured MP-60_2_Top block.")

# ==============================================================================
# 3. UPDATE MODELSPACE ENTITIES (Table, Elevation Benchmarks, Text)
# ==============================================================================
y_0 = 1148.40
old_y_26 = 1460.40
new_y_25 = 1448.40
y_60 = 1868.40
dy = new_y_25 - old_y_26  # -12.00

# 3.1. Table Divider Lines at X: 19262.31 to 19319.21
for e in msp:
    if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
        pts = e.get_points()
        if len(pts) == 2 and abs(pts[0][1] - old_y_26) < 1.0 and abs(pts[1][1] - old_y_26) < 1.0:
            e.set_points([(pts[0][0], new_y_25), (pts[1][0], new_y_25)])

# 3.2. Elevation Benchmark Leader Lines for 25.00' (was at 1460.40)
for e in msp:
    if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
        pts = e.get_points()
        if any(abs(p[1] - old_y_26) < 1.0 for p in pts):
            new_pts = [(p[0], p[1] + dy) for p in pts]
            e.set_points(new_pts)

def clear_bg_fill(entity):
    for attr in ['bg_fill', 'bg_fill_color', 'box_fill_scale', 'bg_fill_transparency']:
        entity.dxf.discard(attr)

# 3.3. Elevation Benchmark Texts (Disable Mask & Raise Text cleanly above leader)
# Explicit handle targeting prevents substring collision!
# BA46B -> 0.00'
# BA510 -> 25.00' (was 26.00')
# BA518 -> 60.00'
for e in msp:
    if e.dxftype() == 'MTEXT':
        handle = e.dxf.handle.upper()
        if handle == 'BA46B':
            e.dxf.text = r"\A1;\pxqr;0.00'"
            e.dxf.insert = (19654.67, 1169.50, 0)
            clear_bg_fill(e)
        elif handle == 'BA510':
            e.dxf.text = r"\A1;\pxqr;25.00'"
            e.dxf.insert = (19654.67, 1469.50, 0)
            clear_bg_fill(e)
        elif handle == 'BA518':
            e.dxf.text = r"\A1;\pxqr;60.00'"
            e.dxf.insert = (19654.67, 1889.50, 0)
            clear_bg_fill(e)

# 3.4. Table Texts (Headers & Data Rows) & Middle Note
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
        elif "2.76'" in txt or "2.14'" in txt:
            # Section 1 Data: center Y = (1148.40 + 1448.40)/2 = 1298.40
            e.dxf.text = r"\A1;%%C2.14' / %%C1.94'"
            e.dxf.insert = (19304.99, 1298.40, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.5
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif txt.strip() in [r"\A1;1", "1"]:
            e.dxf.text = r"\A1;1"
            e.dxf.insert = (19276.54, 1298.40, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 5.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif "1.27'" in txt or "1.48'" in txt:
            # Section 2 Data: center Y = (1448.40 + 1868.40)/2 = 1658.40
            e.dxf.text = r"\A1;%%C1.94' / %%C1.48'"
            e.dxf.insert = (19304.99, 1658.40, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.5
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif txt.strip() in [r"\A1;2", "2"]:
            e.dxf.text = r"\A1;2"
            e.dxf.insert = (19276.54, 1658.40, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 5.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif 'Note:' in txt:
            # Wrap cleanly on 2 lines so it fits between tower and benchmarks
            e.dxf.text = r"Note: Monopole structure with tapered leg\Pconnection from section 1 to section 2."
            e.dxf.width = 0.0
            clear_bg_fill(e)

print("[3] Updated modelspace table and elevation benchmark texts.")

# ==============================================================================
# 4. UPDATE ALL DIMENSIONS TO DECIMAL FEET (ENABLE PLOTTING VIA 'Dim' LAYER)
# ==============================================================================
entities_to_delete = []

for e in msp:
    if e.dxftype() == 'DIMENSION':
        handle = e.dxf.handle.upper()
        geom_name = getattr(e.dxf, 'geometry', '')
        geom_block = doc.blocks.get(geom_name) if geom_name else None

        # Feet-inch duplicates to delete:
        if handle in ['D98B5', 'B921C', 'B9234', 'DCF04']:
            entities_to_delete.append(e)

        # 4.1. Total Height: B9204 (Decimal Feet: 60.00')
        elif handle == 'B9204':
            e.dxf.layer = 'Dim'
            e.dxf.text = "60.00'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;60.00'"

        # 4.2. Section 1 Height: DCDA9 (Decimal Feet: 25.00')
        elif handle == 'DCDA9':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint = (e.dxf.defpoint.x, new_y_25, 0)
            e.dxf.defpoint2 = (e.dxf.defpoint2.x, new_y_25, 0)
            e.dxf.text = "25.00'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;25.00'"
                        be.dxf.insert = (be.dxf.insert.x, 1298.40, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.y - old_y_26) < 2.0:
                            be.dxf.start = (be.dxf.start.x, new_y_25, 0)
                        if abs(be.dxf.end.y - old_y_26) < 2.0:
                            be.dxf.end = (be.dxf.end.x, new_y_25, 0)

        # 4.3. Section 2 Height: DCDBF (Decimal Feet: 35.00')
        elif handle == 'DCDBF':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint = (e.dxf.defpoint.x, new_y_25, 0)
            e.dxf.defpoint2 = (e.dxf.defpoint2.x, new_y_25, 0)
            e.dxf.text = "35.00'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;35.00'"
                        be.dxf.insert = (be.dxf.insert.x, 1658.40, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.y - old_y_26) < 2.0:
                            be.dxf.start = (be.dxf.start.x, new_y_25, 0)
                        if abs(be.dxf.end.y - old_y_26) < 2.0:
                            be.dxf.end = (be.dxf.end.x, new_y_25, 0)

        # 4.4. Base Diameter: D7611 (Decimal Feet: 2.14')
        elif handle == 'D7611':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 - r_base, 1121.60, 0)
            e.dxf.defpoint3 = (19500.00 + r_base, 1121.60, 0)
            e.dxf.defpoint = (19500.00 + r_base, 1103.60, 0)
            e.dxf.text = "2.14'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;2.14'"

        # 4.5. Transition Diameter: D7AA3 (Decimal Feet: 1.94', exactly at 1448.40)
        elif handle == 'D7AA3':
            e.dxf.layer = 'Dim'
            e.dxf.text = "1.94'"
            e.dxf.defpoint2 = (19500.00 - r_trans, new_y_25, 0)
            e.dxf.defpoint3 = (19500.00 + r_trans, new_y_25, 0)
            e.dxf.defpoint = (19500.00 + r_trans, new_y_25, 0)
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.94'"
                        be.dxf.insert = (19527.70, new_y_25 + 4.0, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.y - old_y_26) < 10.0:
                            be.dxf.start = (be.dxf.start.x, new_y_25, 0)
                        if abs(be.dxf.end.y - old_y_26) < 10.0:
                            be.dxf.end = (be.dxf.end.x, new_y_25, 0)

        # 4.6. Top Diameter: E01F4 (Decimal Feet: 1.48', neatly above top cap)
        elif handle == 'E01F4':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 + r_top, y_60 + 9.6, 0)
            e.dxf.defpoint3 = (19500.00 - r_top, y_60 + 9.6, 0)
            e.dxf.defpoint = (19500.00 - r_top, y_60 + 20.0, 0)
            e.dxf.text = "1.48'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.48'"
                        be.dxf.insert = (19522.60, y_60 + 24.0, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.x - 19492.4) < 1.0:
                            be.dxf.start = (19500.00 - r_top, be.dxf.start.y, 0)
                            be.dxf.end = (19500.00 - r_top, be.dxf.end.y, 0)
                        elif abs(be.dxf.start.x - 19507.6) < 1.0:
                            be.dxf.start = (19500.00 + r_top, be.dxf.start.y, 0)
                            be.dxf.end = (19500.00 + r_top, be.dxf.end.y, 0)

for e in entities_to_delete:
    msp.delete_entity(e)

print(f"[4] Deleted {len(entities_to_delete)} feet-inch duplicate dimensions. All dimensions converted to decimal feet on layer Dim.")

# ==============================================================================
# 5. VERIFY MP-60_2_Top AT (19500.00, 903.00)
# ==============================================================================
has_top_insert = False
for e in msp:
    if e.dxftype() == 'INSERT' and e.dxf.name == 'MP-60_2_Top':
        has_top_insert = True
        e.dxf.insert = (19500.00, 903.00, 0)

if not has_top_insert:
    msp.add_blockref('MP-60_2_Top', (19500.00, 903.00, 0), dxfattribs={'layer': '0'})

print("[5] Verified MP-60_2_Top block.")

# Save modified DXF
doc.saveas(out_dxf)
print(f"[6] Saved DXF to {out_dxf}")

# ==============================================================================
# 6. PLOT TO PDF (WINDOW PLOT AROUND TOWER OBJECTS ONLY, FIT TO PAPER)
# ==============================================================================
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
    '19780.0,1950.0',
    'Fit',
    'Center',
    'Y',
    'acad.ctb',
    'N',
    'N',
    out_pdf,
    'N',
    'Y',
    f'SAVEAS\n2018\n"{out_dwg}"',
    'QUIT Y\n'
]

with open(scr_path, 'w', encoding='ascii') as f:
    f.write('\n'.join(scr_lines))

if os.path.exists(out_pdf):
    os.remove(out_pdf)

print("[7] Running AutoCAD accoreconsole to generate DWG and verification PDF...")
cmd = [r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe", "/i", out_dxf, "/s", scr_path]
res = subprocess.run(cmd, capture_output=True, timeout=120)

if os.path.exists(out_pdf):
    pdoc = pymupdf.open(out_pdf)
    page = pdoc[0]
    pix = page.get_pixmap(dpi=300)
    pix.save(out_png)
    pdoc.close()
    
    im = Image.open(out_png)
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        pad = 40
        w, h = im.size
        crop_box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
        cropped = im.crop(crop_box)
        cropped.save(out_png)
        print(f"[8] Auto-cropped PNG to content: {cropped.size}")

    print(f"[9] Final Deliverables:")
    print(f"    DWG: {out_dwg}")
    print(f"    PNG: {out_png}")
else:
    print("AutoCAD execution failed:")
    print(res.stdout.decode('latin-1', errors='ignore'))
