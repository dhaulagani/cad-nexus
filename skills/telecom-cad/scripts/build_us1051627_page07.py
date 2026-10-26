"""
build_us1051627_page07.py
Builds clean, precise Tower Elevation drawing for Site US1051627 (Top Gun)
- Based on survey sketch: Elevation.jpeg and US1051627_Top Gun_Elevation Table.xlsx
- Single section tapered monopole (60.04' height, no transition splice)
- Top of lightning arrester at 66.24'
- Base diameter 1.77', Top diameter 1.02'
- All inputs in decimal feet (no feet-inch)
- Standalone drawing object (no kop), fit to paper
- Output to: output_automated/US1051627_Top_Gun/Page-07/
"""

import os
import math
import subprocess
import pymupdf
from PIL import Image, ImageChops
import ezdxf

template_dxf = r"c:\Apps\cad\Page-07.dxf"
out_dir = r"O:\Documents\Document Gani\Project\Uirtus\output_automated\US1051627_Top_Gun\Page-07"
os.makedirs(out_dir, exist_ok=True)

out_dxf = os.path.join(out_dir, "US1051627_Top_Gun_Page-07.dxf")
out_dwg = os.path.join(out_dir, "US1051627_Top_Gun_Page-07.dwg")
out_pdf = os.path.join(out_dir, "US1051627_Top_Gun_Page-07.pdf")
out_png = os.path.join(out_dir, "US1051627_Top_Gun_Page-07.png")
scr_path = os.path.join(out_dir, "plot_us1051627_page07.scr")

doc = ezdxf.readfile(template_dxf)
msp = doc.modelspace()

# ==============================================================================
# 1. SURVEY PARAMETERS (US1051627 Top Gun)
# ==============================================================================
# Diameters & Radii in inches:
# Base: dia 1.77' = 21.24" -> r = 10.62"
# Top:  dia 1.02' = 12.24" -> r = 6.12"
r_base = 10.62
r_top = 6.12

# Heights in inches:
# Datum 0.00' is at foundation top Y = 1148.40 (block Y = 5.0)
# Structure Height: 60.04' = 720.48" -> Modelspace Y = 1148.40 + 720.48 = 1868.88
# Lightning Arrester Top: 66.24' = 794.88" -> Modelspace Y = 1148.40 + 794.88 = 1943.28
h_struct_in = 720.48
h_arrester_in = 794.88

y_0 = 1148.40
y_top = y_0 + h_struct_in      # 1868.88
y_arr = y_0 + h_arrester_in    # 1943.28

# Block local Y:
yb_base = 7.0                      # Top of base plate
yb_top = 5.0 + h_struct_in         # 725.48 (Puncak tiang)
yb_arr = 5.0 + h_arrester_in       # 799.88 (Puncak lightning arrester)

# ==============================================================================
# 2. UPDATE MP-60_2 BLOCK (US1051627 Geometry)
# ==============================================================================
block_mp = doc.blocks.get('MP-60_2')
for e in list(block_mp):
    block_mp.delete_entity(e)

# Foundation box (30" wide, Y=0 to 5.0)
block_mp.add_line((-15.0, 5.0, 0), (15.0, 5.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((15.0, 5.0, 0), (15.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((15.0, 0.0, 0), (-15.0, 0.0, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-15.0, 0.0, 0), (-15.0, 5.0, 0), dxfattribs={'layer': '0'})

# Base plate (Y=5.0 to 7.0, 26" wide)
block_mp.add_lwpolyline(
    [(13.0, 5.0), (-13.0, 5.0), (-13.0, 7.0), (13.0, 7.0)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Anchor bolts
if 'Bolt2' in doc.blocks:
    for bx in [0.0, 8.5, 11.5, -8.5, -11.5]:
        block_mp.add_blockref('Bolt2', (bx, 7.0, 0), dxfattribs={'layer': 'MP'})

# Outer profile lines (Single tapered section!)
block_mp.add_line((r_base, yb_base, 0), (r_top, yb_top, 0), dxfattribs={'layer': '0'})
block_mp.add_line((-r_base, yb_base, 0), (-r_top, yb_top, 0), dxfattribs={'layer': '0'})

# Top cap
block_mp.add_lwpolyline(
    [(-r_top, yb_top), (r_top, yb_top), (r_top, yb_top + 0.4), (-r_top, yb_top + 0.4)],
    close=True,
    dxfattribs={'layer': '0'}
)

# Lightning Arrester rod (from top cap to yb_arr)
block_mp.add_line((0.0, yb_top + 0.4, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})
# Small arrester tip
block_mp.add_line((-0.4, yb_arr - 1.0, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})
block_mp.add_line((0.4, yb_arr - 1.0, 0), (0.0, yb_arr, 0), dxfattribs={'layer': '0'})

# Centerline (axis) on layer Hatch
block_mp.add_line((0.0, yb_base, 0), (0.0, yb_arr + 9.0, 0), dxfattribs={'layer': 'Hatch'})

# 18-sided polygon facets in elevation
for angle_deg in [20.0, 40.0, 60.0, 80.0]:
    c = math.cos(math.radians(angle_deg))
    xb = r_base * c
    xt = r_top * c
    # Right facets
    block_mp.add_line((xb, yb_base, 0), (xt, yb_top, 0), dxfattribs={'layer': 'Hatch'})
    # Left facets
    block_mp.add_line((-xb, yb_base, 0), (-xt, yb_top, 0), dxfattribs={'layer': 'Hatch'})

print("[1] Configured MP-60_2 block for US1051627 (Single section + lightning arrester).")

# ==============================================================================
# 3. UPDATE MP-60_2_Top BLOCK (Tampak Atas Pole US1051627)
# ==============================================================================
block_top = doc.blocks.get('MP-60_2_Top')
for e in list(block_top):
    block_top.delete_entity(e)

r_flange = 15.0
r_bolts = 12.5

# Base flange circle
block_top.add_circle((0.0, 0.0, 0), radius=r_flange, dxfattribs={'layer': '0'})
# Bolt circle line
block_top.add_circle((0.0, 0.0, 0), radius=r_bolts, dxfattribs={'layer': 'Hatch'})

# 12 Anchor bolts
for i in range(12):
    ang = i * (2.0 * math.pi / 12.0)
    block_top.add_circle((r_bolts * math.cos(ang), r_bolts * math.sin(ang), 0), radius=0.7, dxfattribs={'layer': '0'})

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

print("[2] Configured MP-60_2_Top block for US1051627.")

# ==============================================================================
# 4. UPDATE MODELSPACE TABLE & BENCHMARKS
# ==============================================================================
entities_to_delete = []

# Delete old note underline DF85D
e_df85d = doc.entitydb.get('DF85D')
if e_df85d:
    entities_to_delete.append(e_df85d)

for e in msp:
    if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
        pts = e.get_points()
        # Remove middle divider line at 1460.40
        if len(pts) == 2 and abs(pts[0][1] - 1460.40) < 5.0 and abs(pts[1][1] - 1460.40) < 5.0:
            entities_to_delete.append(e)
        # Update top border line of table to y_top (1868.88)
        elif len(pts) == 2 and abs(pts[0][1] - 1868.40) < 5.0 and abs(pts[1][1] - 1868.40) < 5.0:
            e.set_points([(pts[0][0], y_top), (pts[1][0], y_top)])
        # Update vertical lines of table to end at y_top
        elif len(pts) >= 2 and any(abs(p[1] - 1868.40) < 5.0 for p in pts):
            new_pts = []
            for p in pts:
                if abs(p[1] - 1868.40) < 5.0:
                    new_pts.append((p[0], y_top))
                elif abs(p[1] - 1460.40) < 5.0:
                    continue
                else:
                    new_pts.append(p)
            e.set_points(new_pts)

def clear_bg_fill(entity):
    for attr in ['bg_fill', 'bg_fill_color', 'box_fill_scale', 'bg_fill_transparency']:
        entity.dxf.discard(attr)

# Update / adjust Elevation Benchmarks:
for e in msp:
    if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
        pts = e.get_points()
        # Old 26.00' leader (at ~1460.40) -> move to 66.24' (Y = 1943.28)
        if any(abs(p[1] - 1460.40) < 5.0 for p in pts):
            dy_arr = y_arr - 1460.40
            new_pts = [(p[0], p[1] + dy_arr) for p in pts]
            e.set_points(new_pts)
        # Old 60.00' leader (at ~1868.40) -> adjust to 60.04' (Y = 1868.88)
        elif any(abs(p[1] - 1868.40) < 5.0 for p in pts):
            dy_top = y_top - 1868.40
            new_pts = [(p[0], p[1] + dy_top) for p in pts]
            e.set_points(new_pts)

# Add horizontal datum line for 66.24'
msp.add_lwpolyline([(19500.00, y_arr), (19636.52, y_arr)], dxfattribs={'layer': 'Layer Table'})

for e in msp:
    if e.dxftype() == 'MTEXT':
        handle = e.dxf.handle.upper()
        # 0.00' datum
        if handle == 'BA46B':
            e.dxf.text = r"\A1;\pxqr;0.00'"
            e.dxf.insert = (19654.67, 1169.50, 0)
            clear_bg_fill(e)
        # 66.24' datum (Top of Lightning Arrester)
        elif handle == 'BA510':
            e.dxf.text = r"\A1;\pxqr;66.24'"
            e.dxf.insert = (19654.67, y_arr + 13.55 + 7.0, 0)
            clear_bg_fill(e)
        # 60.04' datum (Top of Pole)
        elif handle == 'BA518':
            e.dxf.text = r"\A1;\pxqr;60.04'"
            e.dxf.insert = (19654.67, y_top + 13.55 + 7.0, 0)
            clear_bg_fill(e)

# Update Table Texts & Notes:
y_tab_center = (y_0 + y_top) / 2.0  # 1508.64

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
        elif "2.76'" in txt or "2.14'" in txt or "1.77'" in txt:
            e.dxf.text = r"\A1;%%C1.77' / %%C1.02'"
            e.dxf.insert = (19304.99, y_tab_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 4.5
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif txt.strip() in [r"\A1;1", "1"]:
            e.dxf.text = r"\A1;1"
            e.dxf.insert = (19276.54, y_tab_center, 0)
            e.dxf.attachment_point = 5
            e.dxf.char_height = 5.0
            e.dxf.width = 0.0
            e.dxf.rotation = 90.0
            clear_bg_fill(e)
        elif "1.27'" in txt or "1.48'" in txt or txt.strip() in [r"\A1;2", "2"]:
            entities_to_delete.append(e)
        elif 'Note:' in txt:
            e.dxf.text = r"Note: Only one section Monopole."
            e.dxf.insert = (19535.00, y_tab_center, 0)
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

        # Feet-inch & unneeded dimensions to delete:
        if handle in ['D98B5', 'B921C', 'B9234', 'DCDBF', 'D7AA3', 'DCF04', 'DCDA9']:
            entities_to_delete.append(e)

        # 5.1. Total Pole Height: B9204 (60.04')
        elif handle == 'B9204':
            e.dxf.layer = 'Dim'
            e.dxf.text = "60.04'"
            e.dxf.defpoint = (19356.25, y_top, 0)
            e.dxf.defpoint3 = (19470.00, y_top, 0)
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;60.04'"
                        be.dxf.insert = (be.dxf.insert.x, y_tab_center, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.y - 1868.40) < 5.0:
                            be.dxf.start = (be.dxf.start.x, y_top, 0)
                        if abs(be.dxf.end.y - 1868.40) < 5.0:
                            be.dxf.end = (be.dxf.end.x, y_top, 0)

        # 5.2. Base Diameter: D7611 (1.77')
        elif handle == 'D7611':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 - r_base, 1121.60, 0)
            e.dxf.defpoint3 = (19500.00 + r_base, 1121.60, 0)
            e.dxf.defpoint = (19500.00 + r_base, 1103.60, 0)
            e.dxf.text = "1.77'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.77'"

        # 5.3. Top Diameter: E01F4 (1.02')
        elif handle == 'E01F4':
            e.dxf.layer = 'Dim'
            e.dxf.defpoint2 = (19500.00 + r_top, y_top + 9.6, 0)
            e.dxf.defpoint3 = (19500.00 - r_top, y_top + 9.6, 0)
            e.dxf.defpoint = (19500.00 - r_top, y_top + 20.0, 0)
            e.dxf.text = "1.02'"
            if geom_block:
                for be in geom_block:
                    if be.dxf.layer == 'Defpoints' and be.dxftype() in ['LINE', 'MTEXT', 'TEXT', 'INSERT']:
                        be.dxf.layer = 'Dim'
                    if be.dxftype() in ['TEXT', 'MTEXT']:
                        be.dxf.text = r"\A1;1.02'"
                        be.dxf.insert = (19522.60, y_top + 24.0, 0)
                    elif be.dxftype() == 'LINE':
                        if abs(be.dxf.start.x - 19492.4) < 5.0 or be.dxf.start.x < 19500.0:
                            be.dxf.start = (19500.00 - r_top, y_top + 9.6, 0)
                            be.dxf.end = (19500.00 - r_top, y_top + 28.0, 0)
                        elif abs(be.dxf.start.x - 19507.6) < 5.0 or be.dxf.start.x > 19500.0:
                            be.dxf.start = (19500.00 + r_top, y_top + 9.6, 0)
                            be.dxf.end = (19500.00 + r_top, y_top + 28.0, 0)

for e in entities_to_delete:
    msp.delete_entity(e)

print(f"[3] Cleaned entities and converted dimensions to survey decimal feet (1.77', 1.02', 60.04').")

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
# 7. PLOT TO PDF (WINDOW PLOT AROUND TOWER OBJECTS ONLY, FIT TO PAPER)
# ==============================================================================
# Window bounding box:
# X: 19220.0 (left of table) to 19780.0 (right of elevation leader lines)
# Y: 850.0 (below MP-60_2_Top) to 1990.0 (above lightning arrester & 66.24' datum)
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
    '19780.0,1990.0',
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

print("[6] Running AutoCAD accoreconsole to generate DWG and verification PDF...")
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
        print(f"[7] Auto-cropped PNG to content: {cropped.size}")

    print(f"[8] Final Deliverables for US1051627:")
    print(f"    DWG: {out_dwg}")
    print(f"    PNG: {out_png}")
else:
    print("AutoCAD execution failed:")
    print(res.stdout.decode('latin-1', errors='ignore'))
