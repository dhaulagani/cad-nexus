"""
telecom_cad_auto.tower_builder
Generates exact Tower Elevation Line Diagram (Page 7) and Monopole Top View block
following AutoCAD telecom standards and Quemado survey data.
"""

import os
import math
import subprocess
import pymupdf
from PIL import Image
import numpy as np
import ezdxf


ACCORE_EXE = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"


def create_quemado_monopole_block(doc: ezdxf.document.Drawing) -> str:
    """
    Creates/updates the MP-60_2 block with Quemado's 2-section geometry:
    - Base to 25.00' (Y=5 to Y=305 in block units = 300" height)
      Base dia = 2.14' (25.68", r=12.84")
      Trans dia = 1.94' (23.28", r=11.64")
    - 25.00' to 60.00' (Y=305 to Y=725 in block units = 420" height)
      Trans dia = 1.94' (23.28", r=11.64")
      Top dia = 1.48' (17.76", r=8.88")
    - Lightning Arrester on top:
      4.22' (50.64") from Y=725 to Y=775.64
    """
    block_name = "MP-60_2"
    if block_name in doc.blocks:
        block = doc.blocks.get(block_name)
        for e in list(block):
            block.delete_entity(e)
    else:
        block = doc.blocks.new(name=block_name)

    # 1. Foundation box (0 to 5)
    block.add_line((-18.0, 5.0, 0), (18.0, 5.0, 0), dxfattribs={'layer': '0'})
    block.add_line((18.0, 5.0, 0), (18.0, 0.0, 0), dxfattribs={'layer': '0'})
    block.add_line((18.0, 0.0, 0), (-18.0, 0.0, 0), dxfattribs={'layer': '0'})
    block.add_line((-18.0, 0.0, 0), (-18.0, 5.0, 0), dxfattribs={'layer': '0'})

    # 2. Base plate (Y=5 to 7)
    block.add_lwpolyline(
        [(15.0, 5.0), (-15.0, 5.0), (-15.0, 7.0), (15.0, 7.0)],
        close=True,
        dxfattribs={'layer': '0'}
    )

    # 3. Anchor bolts on base plate
    if "Bolt2" in doc.blocks:
        block.add_blockref("Bolt2", (0.0, 7.0, 0), dxfattribs={'layer': 'MP'})
        block.add_blockref("Bolt2", (10.0, 7.0, 0), dxfattribs={'layer': 'MP'})
        block.add_blockref("Bolt2", (13.5, 7.0, 0), dxfattribs={'layer': 'MP'})
        block.add_blockref("Bolt2", (-10.0, 7.0, 0), dxfattribs={'layer': 'MP'})
        block.add_blockref("Bolt2", (-13.5, 7.0, 0), dxfattribs={'layer': 'MP'})

    # 4. Monopole 18-sided polygon facets in elevation
    angles = [0.0, 20.0, 40.0, 60.0, 80.0]
    cos_angles = [math.cos(math.radians(a)) for a in angles]

    r_base = 12.84     # Base radius (at Y=7)
    r_trans = 11.64    # Transition radius (at Y=307)
    r_top = 8.88       # Top radius (at Y=727)

    y_base = 7.0
    y_trans = 307.0    # 25' = 300" above base plate
    y_top = 727.0      # 60' = 720" above base plate
    y_arr = 777.64     # 64.22' top of lightning arrester

    # Outer profile lines
    block.add_line((r_base, y_base, 0), (r_trans, y_trans, 0), dxfattribs={'layer': '0'})
    block.add_line((-r_base, y_base, 0), (-r_trans, y_trans, 0), dxfattribs={'layer': '0'})
    block.add_line((r_trans, y_trans, 0), (r_top, y_top, 0), dxfattribs={'layer': '0'})
    block.add_line((-r_trans, y_trans, 0), (-r_top, y_top, 0), dxfattribs={'layer': '0'})

    # Transition joint ring line
    block.add_line((-r_trans, y_trans, 0), (r_trans, y_trans, 0), dxfattribs={'layer': '0'})

    # Top pole cap
    block.add_lwpolyline(
        [(-r_top, y_top), (r_top, y_top), (r_top, y_top + 0.4), (-r_top, y_top + 0.4)],
        close=True,
        dxfattribs={'layer': '0'}
    )

    # Centerline (axis)
    block.add_line((0.0, y_base, 0), (0.0, y_arr, 0), dxfattribs={'layer': 'Hatch'})

    # Facet lines (layer Hatch)
    for c in cos_angles[1:]:
        x_b = r_base * c
        x_tr = r_trans * c
        x_t = r_top * c
        block.add_line((x_b, y_base, 0), (x_tr, y_trans, 0), dxfattribs={'layer': 'Hatch'})
        block.add_line((x_tr, y_trans, 0), (x_t, y_top, 0), dxfattribs={'layer': 'Hatch'})
        block.add_line((-x_b, y_base, 0), (-x_tr, y_trans, 0), dxfattribs={'layer': 'Hatch'})
        block.add_line((-x_tr, y_trans, 0), (-x_t, y_top, 0), dxfattribs={'layer': 'Hatch'})

    # Lightning Arrester Rod
    block.add_line((0.0, y_top, 0), (0.0, y_arr, 0), dxfattribs={'layer': '0'})
    block.add_circle((0.0, y_arr, 0), radius=0.6, dxfattribs={'layer': '0'})

    print("[TowerBuilder] Configured MP-60_2 block for Quemado 25'/35' 60ft monopole.")
    return block_name


def create_quemado_top_view_block(doc: ezdxf.document.Drawing) -> str:
    """
    Creates/updates MP-60_2_Top (tampak atas pole) for compound use:
    - 18-sided polygon base pole (r = 12.84", dia = 2.14')
    - Circular base flange plate (r = 17.0", dia = 34")
    - Bolt circle with anchor bolts (r = 14.5")
    - 18-sided polygon top pole (r = 8.88", dia = 1.48')
    """
    block_name = "MP-60_2_Top"
    if block_name in doc.blocks:
        block = doc.blocks.get(block_name)
        for e in list(block):
            block.delete_entity(e)
    else:
        block = doc.blocks.new(name=block_name)

    r_base = 12.84
    r_top = 8.88
    r_flange = 17.5
    r_bolts = 15.0

    # 1. Circular base plate / flange ring
    block.add_circle((0.0, 0.0, 0), radius=r_flange, dxfattribs={'layer': '0'})

    # 2. Bolt circle line
    block.add_circle((0.0, 0.0, 0), radius=r_bolts, dxfattribs={'layer': 'Hatch'})

    # 3. Anchor bolts (12 bolts around circumference)
    for i in range(12):
        angle = i * (2.0 * math.pi / 12.0)
        bx = r_bolts * math.cos(angle)
        by = r_bolts * math.sin(angle)
        block.add_circle((bx, by, 0), radius=0.8, dxfattribs={'layer': '0'})

    # 4. 18-sided polygon base pole and top pole
    num_facets = 18
    base_poly_pts = []
    top_poly_pts = []
    for i in range(num_facets):
        angle = i * (2.0 * math.pi / num_facets)
        base_poly_pts.append((r_base * math.cos(angle), r_base * math.sin(angle)))
        top_poly_pts.append((r_top * math.cos(angle), r_top * math.sin(angle)))

    block.add_lwpolyline(base_poly_pts, close=True, dxfattribs={'layer': '0'})
    block.add_lwpolyline(top_poly_pts, close=True, dxfattribs={'layer': '0'})

    # 5. Center crosshair
    block.add_line((-r_flange * 1.15, 0.0, 0), (r_flange * 1.15, 0.0, 0), dxfattribs={'layer': 'Hatch'})
    block.add_line((0.0, -r_flange * 1.15, 0), (0.0, r_flange * 1.15, 0), dxfattribs={'layer': 'Hatch'})

    print("[TowerBuilder] Configured MP-60_2_Top block (Tampak Atas Pole).")
    return block_name


def update_page7_diagram(doc: ezdxf.document.Drawing) -> None:
    """
    Updates the Page 7 layout elements (modelspace):
    - Table lines, labels, text
    - Dimension values and defpoints, including cached anonymous blocks
    - Datum level benchmark lines and elevations
    - Viewport framing in layout LINE DIAGRAM
    """
    msp = doc.modelspace()

    old_y_trans = 2808.40
    new_y_trans = 2796.40
    y_base = 2496.40
    y_top = 3216.40
    y_arr = 3267.04

    # 1. Update Table Divider Line and Heights
    for e in msp:
        if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
            pts = e.get_points()
            if len(pts) == 2 and abs(pts[0][1] - old_y_trans) < 1.0 and abs(pts[1][1] - old_y_trans) < 1.0:
                e.set_points([(pts[0][0], new_y_trans), (pts[1][0], new_y_trans)])

        if e.dxftype() in ['TEXT', 'MTEXT']:
            txt = getattr(e.dxf, 'text', '')
            if "2.76'" in txt:
                e.dxf.text = r"\A1;Ø 2.14' / Ø 1.94'"
                e.dxf.insert = (e.dxf.insert.x, 2646.40, 0)
            elif txt.strip() == r"\A1;1":
                e.dxf.insert = (e.dxf.insert.x, 2646.40, 0)
            elif "1.27'" in txt:
                e.dxf.text = r"\A1;Ø 1.94' / Ø 1.48'"
                e.dxf.insert = (e.dxf.insert.x, 3006.40, 0)
            elif txt.strip() == r"\A1;2":
                e.dxf.insert = (e.dxf.insert.x, 3006.40, 0)
            elif "26.00'" in txt:
                e.dxf.text = r"\A1;\pxqr;25.00'"
                e.dxf.insert = (e.dxf.insert.x, 2814.70, 0)

    # 2. Update Datum Benchmark Lines for 25.00'
    for e in msp:
        if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'Layer Table':
            pts = e.get_points()
            if any(abs(p[1] - old_y_trans) < 1.0 for p in pts):
                new_pts = []
                for p in pts:
                    dy = p[1] - old_y_trans
                    new_pts.append((p[0], new_y_trans + dy))
                e.set_points(new_pts)

    # 3. Update Dimensions & their cached anonymous blocks
    # *D12: Section 1 Height (was 26'-0" -> now 25'-0")
    b_d12 = doc.blocks.get('*D12')
    if b_d12:
        for be in b_d12:
            if be.dxftype() in ['TEXT', 'MTEXT']:
                be.dxf.text = r"\A1;25'-0\""
                be.dxf.insert = (be.dxf.insert.x, 2646.40, 0)
            elif be.dxftype() == 'LINE':
                # Update upper witness line and dimension line
                if abs(be.dxf.start.y - old_y_trans) < 2.0:
                    be.dxf.start = (be.dxf.start.x, new_y_trans, 0)
                if abs(be.dxf.end.y - old_y_trans) < 2.0:
                    be.dxf.end = (be.dxf.end.x, new_y_trans, 0)

    # *D13: Section 2 Height (was 34'-0" -> now 35'-0")
    b_d13 = doc.blocks.get('*D13')
    if b_d13:
        for be in b_d13:
            if be.dxftype() in ['TEXT', 'MTEXT']:
                be.dxf.text = r"\A1;35'-0\""
                be.dxf.insert = (be.dxf.insert.x, 3006.40, 0)
            elif be.dxftype() == 'LINE':
                if abs(be.dxf.start.y - old_y_trans) < 2.0:
                    be.dxf.start = (be.dxf.start.x, new_y_trans, 0)
                if abs(be.dxf.end.y - old_y_trans) < 2.0:
                    be.dxf.end = (be.dxf.end.x, new_y_trans, 0)

    # *D112: Base Diameter (was 2'-9" -> now 2'-2")
    b_d112 = doc.blocks.get('*D112')
    if b_d112:
        for be in b_d112:
            if be.dxftype() in ['TEXT', 'MTEXT']:
                be.dxf.text = r"\A1;2'-2\""

    # *D113: Transition Diameter (was 1.93' -> now 1.94')
    b_d113 = doc.blocks.get('*D113')
    if b_d113:
        for be in b_d113:
            if be.dxftype() in ['TEXT', 'MTEXT']:
                be.dxf.text = r"\A1;1.94'"
                be.dxf.insert = (be.dxf.insert.x, new_y_trans + 4.0, 0)
            elif be.dxftype() == 'LINE':
                if abs(be.dxf.start.y - old_y_trans) < 10.0:
                    dy = be.dxf.start.y - old_y_trans
                    be.dxf.start = (be.dxf.start.x, new_y_trans + dy, 0)
                if abs(be.dxf.end.y - old_y_trans) < 10.0:
                    dy = be.dxf.end.y - old_y_trans
                    be.dxf.end = (be.dxf.end.x, new_y_trans + dy, 0)

    # *D152: Top Diameter (was 1'-3" -> now 1'-6")
    b_d152 = doc.blocks.get('*D152')
    if b_d152:
        for be in b_d152:
            if be.dxftype() in ['TEXT', 'MTEXT']:
                be.dxf.text = r"\A1;1'-6\""

    # Update DIMENSION entities in modelspace
    for e in msp:
        if e.dxftype() == 'DIMENSION':
            if abs(e.dxf.defpoint2.y - y_base) < 2.0 and abs(e.dxf.defpoint3.y - old_y_trans) < 2.0:
                e.dxf.defpoint3 = (e.dxf.defpoint3.x, new_y_trans, 0)
                e.dxf.defpoint = (e.dxf.defpoint.x, new_y_trans, 0)
                e.dxf.text = '25\'-0"'
            elif abs(e.dxf.defpoint2.y - old_y_trans) < 2.0 and abs(e.dxf.defpoint3.y - y_top) < 2.0:
                e.dxf.defpoint2 = (e.dxf.defpoint2.x, new_y_trans, 0)
                e.dxf.text = '35\'-0"'
            elif "1.93'" in getattr(e.dxf, 'text', '') or abs(e.dxf.defpoint2.y - old_y_trans) < 2.0:
                e.dxf.text = "1.94'"
                e.dxf.defpoint2 = (9544.30 - 11.64, new_y_trans, 0)
                e.dxf.defpoint3 = (9544.30 + 11.64, new_y_trans, 0)
                e.dxf.defpoint = (9544.30 + 11.64, new_y_trans, 0)
            elif abs(e.dxf.defpoint2.y - 2469.60) < 5.0 and abs(e.dxf.defpoint.y - 2451.61) < 5.0:
                e.dxf.defpoint2 = (9544.30 - 12.84, 2469.60, 0)
                e.dxf.defpoint3 = (9544.30 + 12.84, 2469.60, 0)
                e.dxf.defpoint = (9544.30 + 12.84, 2451.61, 0)
                e.dxf.text = '2\'-2"'
            elif abs(e.dxf.defpoint2.y - 3226.00) < 5.0:
                e.dxf.defpoint2 = (9544.30 - 8.88, 3226.00, 0)
                e.dxf.defpoint3 = (9544.30 + 8.88, 3226.00, 0)
                e.dxf.defpoint = (9544.30 + 8.88, 3236.07, 0)
                e.dxf.text = '1\'-6"'

    # 4. Top of Lightning Arrester Level Symbol
    msp.add_lwpolyline(
        [(9660.80, y_arr), (9715.08, y_arr)],
        dxfattribs={'layer': 'Layer Table'}
    )
    msp.add_lwpolyline(
        [(9680.81, y_arr), (9675.51, y_arr + 6.1)],
        dxfattribs={'layer': 'Layer Table'}
    )
    msp.add_lwpolyline(
        [(9680.81, y_arr), (9696.38, y_arr + 13.55), (9744.06, y_arr + 13.55)],
        dxfattribs={'layer': 'Layer Table'}
    )
    msp.add_mtext(
        r"\A1;\pxqr;64.22'",
        dxfattribs={'layer': '0', 'insert': (9698.96, y_arr + 14.0, 0), 'char_height': 5.72}
    )

    # Dimension for Lightning Arrester (4.22') placed on left side of top of pole
    msp.add_line((9544.30 - 8.88, y_top, 0), (9520.0, y_top, 0), dxfattribs={'layer': 'Dim'})
    msp.add_line((9544.30, y_arr, 0), (9520.0, y_arr, 0), dxfattribs={'layer': 'Dim'})
    msp.add_line((9525.0, y_top, 0), (9525.0, y_arr, 0), dxfattribs={'layer': 'Dim'})
    msp.add_line((9523.0, y_top - 2.0, 0), (9527.0, y_top + 2.0, 0), dxfattribs={'layer': 'Dim'})
    msp.add_line((9523.0, y_arr - 2.0, 0), (9527.0, y_arr + 2.0, 0), dxfattribs={'layer': 'Dim'})
    msp.add_mtext(
        r"\A1;4.22'",
        dxfattribs={'layer': 'Dim', 'insert': (9505.0, (y_top + y_arr) / 2.0, 0), 'char_height': 5.72}
    )

    # Clean up draft/scratch notes from template
    for e in list(msp):
        if e.dxftype() in ['TEXT', 'MTEXT']:
            txt = getattr(e.dxf, 'text', '')
            if 'Normal Text' in txt:
                msp.delete_entity(e)

    # 5. Adjust Layout Viewport to fit whole tower nicely without capturing compass South or draft text
    lay = doc.layouts.get('LINE DIAGRAM')
    if lay:
        for vp in lay:
            if vp.dxftype() == 'VIEWPORT' and vp.dxf.handle.upper() == '8C153':
                vp.dxf.view_center_point = (9544.297, 2860.0, 0.0)
                vp.dxf.view_height = 885.0

    print("[TowerBuilder] Updated Page 7 diagram entities to Quemado dimensions.")


def generate_page7_deliverable(
    template_dxf: str,
    output_dir: str,
    site_info: dict
) -> dict:
    """
    Main function to generate Page 7 CAD drawings and plot to PDF & PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    site_id = site_info.get("Site ID", "US1051600")
    site_name = site_info.get("Site Name", "Quemado")

    dxf_out = os.path.join(output_dir, f"{site_id}_{site_name}_Rev_A_Page7.dxf")
    dwg_out = os.path.join(output_dir, f"{site_id}_{site_name}_Rev_A_Page7.dwg")
    pdf_out = os.path.join(output_dir, f"{site_id}_{site_name}_Rev_A_Page7.pdf")
    png_out = os.path.join(output_dir, f"{site_id}_{site_name}_Rev_A_Page7.png")
    scr_out = os.path.join(output_dir, "plot_page7.scr")

    doc = ezdxf.readfile(template_dxf)

    # 1. Update/Create MP-60_2 Monopole elevation block
    create_quemado_monopole_block(doc)

    # 2. Create MP-60_2_Top block for Compound drawing
    create_quemado_top_view_block(doc)

    # 3. Update Page 7 drawing entities in modelspace
    update_page7_diagram(doc)

    doc.saveas(dxf_out)
    print(f"[TowerBuilder] Saved updated DXF to {dxf_out}")

    # 4. Generate AutoCAD script to plot Layout LINE DIAGRAM and save DWG
    scr_lines = [
        '(setvar "EXPERT" 2)',
        '(setvar "CTAB" "LINE DIAGRAM")',
        '-PLOT', 'Y', '', 'AutoCAD PDF (General Documentation).pc3',
        'ISO full bleed A3 (420.00 x 297.00 MM)',
        'I', 'L', 'N', 'Layout', 'Fit', '0.0,0.0', 'Y', 'acad.ctb', 'Y', 'N', 'N', 'N',
        pdf_out, 'N', 'Y',
        f'SAVEAS\n2018\n"{dwg_out}"',
        'QUIT Y\n'
    ]

    with open(scr_out, "w", encoding="ascii") as f:
        f.write('\n'.join(scr_lines))

    if os.path.exists(pdf_out):
        os.remove(pdf_out)

    # 5. Run AutoCAD headless
    print("[TowerBuilder] Running AutoCAD accoreconsole to plot Page 7...")
    cmd = [ACCORE_EXE, "/i", dxf_out, "/s", scr_out]
    res = subprocess.run(cmd, capture_output=True, timeout=120)

    if not os.path.exists(pdf_out):
        raise RuntimeError(f"Failed to plot Page 7 PDF: {res.stdout.decode('latin-1', errors='ignore')}")

    # 6. Render high-res PNG
    pdf_doc = pymupdf.open(pdf_out)
    page = pdf_doc[0]
    pix = page.get_pixmap(dpi=150)
    pix.save(png_out)
    text_content = page.get_text()
    pdf_doc.close()

    print(f"[TowerBuilder] Successfully generated Page 7 PDF and PNG: {pdf_out}")
    return {
        "dxf": dxf_out,
        "dwg": dwg_out,
        "pdf": pdf_out,
        "png": png_out,
        "text": text_content
    }
