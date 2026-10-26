r"""
build_quemado_page04.py
Generates Compound Plan Page-04 for US1051600 Quemado.
Adheres strictly to:
- No title block / kop (compound + legend only)
- Line composition, fence with 'X' cross symbol every ~80"-96" (with clearance gap, non-touching)
- All dimensions in decimal feet (no feet-inch)
- Equipment pads, shelters, monopole, ice bridge, transformer pad, gates
- Outputs .dwg, .pdf, and crisp hairline .png
"""

import os
import sys
import math
import subprocess
import ezdxf
from ezdxf.enums import TextEntityAlignment
import fitz  # PyMuPDF
from PIL import Image

TEMPLATE_DXF = r"C:\Apps\cad\Page-04.dxf"
OUTPUT_DIR = r"O:\Documents\Document Gani\Project\Uirtus\output_automated\US1051600_Quemado\Page-04"
OUT_BASE = os.path.join(OUTPUT_DIR, "US1051600_Quemado_Page-04")
ACCORECONSOLE = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Math / Geometry Helpers
# -------------------------------------------------------------
def dist(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def draw_rect(msp, x, y, w, h, layer="0", color=7):
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer, "color": color})

def draw_rotated_rect(msp, cx, cy, w, h, angle_deg=45.0, layer="0", color=7):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    hw, hh = w / 2.0, h / 2.0
    corners = [
        (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
    ]
    pts = []
    for dx, dy in corners:
        rx = cx + dx * cos_a - dy * sin_a
        ry = cy + dx * sin_a + dy * cos_a
        pts.append((rx, ry))
    return msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer, "color": color})

def draw_bubble(msp, cx, cy, text, radius=10.0, layer="TEXT", color=7):
    msp.add_circle((cx, cy), radius, dxfattribs={"layer": layer, "color": color})
    msp.add_text(
        text,
        dxfattribs={
            "layer": layer,
            "color": color,
            "height": radius * 1.1,
            "style": "Standard"
        }
    ).set_placement((cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)

def draw_tick_dim(msp, p1, p2, offset, text, layer="Dim Compound", tick_len=6.0, text_h=7.0):
    """
    Draws an architectural tick dimension line between p1 and p2 at specified perpendicular offset.
    Text is formatted strictly in decimal feet (e.g. 137.33').
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-4:
        return
    ux, uy = dx / L, dy / L
    vx, vy = -uy, ux  # perpendicular normal
    
    # Dimension line start & end
    d1 = (x1 + offset * vx, y1 + offset * vy)
    d2 = (x2 + offset * vx, y2 + offset * vy)
    
    # Extension lines
    ext_over = 4.0 if offset >= 0 else -4.0
    e1_start = (x1 + (2.0 if offset >= 0 else -2.0) * vx, y1 + (2.0 if offset >= 0 else -2.0) * vy)
    e1_end = (d1[0] + ext_over * vx, d1[1] + ext_over * vy)
    e2_start = (x2 + (2.0 if offset >= 0 else -2.0) * vx, y2 + (2.0 if offset >= 0 else -2.0) * vy)
    e2_end = (d2[0] + ext_over * vx, d2[1] + ext_over * vy)
    
    msp.add_line(e1_start, e1_end, dxfattribs={"layer": layer, "color": 7})
    msp.add_line(e2_start, e2_end, dxfattribs={"layer": layer, "color": 7})
    
    # Main dim line
    msp.add_line(d1, d2, dxfattribs={"layer": layer, "color": 7})
    
    # Architectural Ticks (45 deg slashes)
    t_arm = tick_len / math.sqrt(2.0)
    for dp in [d1, d2]:
        # 45 deg relative to dimension line
        tx1 = dp[0] - t_arm * (ux - vx)
        ty1 = dp[1] - t_arm * (uy - vy)
        tx2 = dp[0] + t_arm * (ux - vx)
        ty2 = dp[1] + t_arm * (uy - vy)
        msp.add_line((tx1, ty1), (tx2, ty2), dxfattribs={"layer": layer, "color": 7})
        
    # Dimension text
    mx = (d1[0] + d2[0]) / 2.0 + 5.0 * vx
    my = (d1[1] + d2[1]) / 2.0 + 5.0 * vy
    rot = math.degrees(math.atan2(dy, dx))
    if rot > 90.0 or rot <= -90.0:
        rot = (rot + 180.0) % 360.0
        
    t = msp.add_text(
        text,
        dxfattribs={
            "layer": layer,
            "color": 7,
            "height": text_h,
            "rotation": rot,
            "style": "Standard"
        }
    )
    t.set_placement((mx, my), align=TextEntityAlignment.BOTTOM_CENTER)

# -------------------------------------------------------------
# Fence Generator with Non-Touching 'X' Crosses
# -------------------------------------------------------------
def draw_fence_line(msp, p1, p2, layer="0", color=7, cross_spacing=96.0, cross_size=6.0, gap=1.25):
    """
    Draws fence polyline segments interrupted by 'X' crosses.
    The cross is 6x6 inches.
    Gaps of 1.25 inches ensure line and X NEVER touch ('tidak bersentuhan').
    Crosses repeat approximately every 80-96 inches (~8 feet).
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    if L < 24.0:
        msp.add_line(p1, p2, dxfattribs={"layer": layer, "color": color})
        return
        
    ux, uy = dx / L, dy / L
    vx, vy = -uy, ux
    
    # Calculate number of crosses
    n_crosses = max(1, int(round(L / cross_spacing)))
    actual_spacing = L / (n_crosses + 1)
    
    half_c = cross_size / 2.0
    half_gap = half_c + gap
    
    curr_pt = (x1, y1)
    for i in range(1, n_crosses + 1):
        cx = x1 + i * actual_spacing * ux
        cy = y1 + i * actual_spacing * uy
        
        # Segment up to cross gap
        seg_end = (cx - half_gap * ux, cy - half_gap * uy)
        msp.add_line(curr_pt, seg_end, dxfattribs={"layer": layer, "color": color})
        
        # Draw 'X' cross
        arm1_p1 = (cx - half_c * ux - half_c * vx, cy - half_c * uy - half_c * vy)
        arm1_p2 = (cx + half_c * ux + half_c * vx, cy + half_c * uy + half_c * vy)
        arm2_p1 = (cx - half_c * ux + half_c * vx, cy - half_c * uy + half_c * vy)
        arm2_p2 = (cx + half_c * ux - half_c * vx, cy + half_c * uy - half_c * vy)
        
        msp.add_line(arm1_p1, arm1_p2, dxfattribs={"layer": layer, "color": color})
        msp.add_line(arm2_p1, arm2_p2, dxfattribs={"layer": layer, "color": color})
        
        # Resume point
        curr_pt = (cx + half_gap * ux, cy + half_gap * uy)
        
    # Final segment
    msp.add_line(curr_pt, (x2, y2), dxfattribs={"layer": layer, "color": color})


# -------------------------------------------------------------
# Main Generation Function
# -------------------------------------------------------------
def generate_page04():
    print(f"Loading template: {TEMPLATE_DXF}")
    doc = ezdxf.readfile(TEMPLATE_DXF)
    msp = doc.modelspace()
    
    # Clear old modelspace entities
    ents_to_remove = list(msp)
    for e in ents_to_remove:
        msp.delete_entity(e)
    print(f"Cleared {len(ents_to_remove)} old entities from modelspace.")
    
    # Set model units to inches
    doc.header["$INSUNITS"] = 1  # 1 = Inches
    
    # Ensure required linetypes exist
    if "DASHED" not in doc.linetypes:
        doc.linetypes.new("DASHED", dxfattribs={"description": "Dashed __ __", "pattern": [0.5, 0.5, -0.25]})
    if "CENTER" not in doc.linetypes:
        doc.linetypes.new("CENTER", dxfattribs={"description": "Center ____ _ ____ _", "pattern": [1.25, 0.75, -0.125, 0.125, -0.125]})

    # Define layers if missing
    layers_needed = [
        ("0", 7, "Continuous"),
        ("Dim Compound", 7, "Continuous"),
        ("Dim", 7, "Continuous"),
        ("TEXT", 7, "Continuous"),
        ("ICE Bridge", 7, "Continuous"),
        ("MP", 7, "Continuous"),
        ("Hatch", 7, "Continuous")
    ]
    for l_name, l_col, l_lt in layers_needed:
        if l_name not in doc.layers:
            doc.layers.add(l_name, color=l_col, linetype=l_lt)
            
    # Coordinate Setup (Inches)
    # Origin of Compound
    X0 = 420.0
    Y0 = 100.0
    
    W_ft = 137.33
    H_ft = 73.68
    W_in = W_ft * 12.0  # 1647.96"
    H_in = H_ft * 12.0  # 884.16"
    
    # ---------------------------------------------------------
    # 1. Compound Perimeter & Fence
    # ---------------------------------------------------------
    # Corners:
    # BL = (X0, Y0)
    # BR = (X0 + W_in, Y0)
    # TR = (X0 + W_in, Y0 + H_in)
    # Recessed North Fence:
    # From TR left 35.80' = 429.60" -> X_step_east = X0 + W_in - 429.60 = X0 + 1218.36
    # Steps down 5.0' = 60.0" -> Y_recess = Y0 + H_in - 60.0 = Y0 + 824.16
    # Runs west to X_step_west = X0 + 58.7' * 12 = X0 + 704.40
    # Steps up 60.0" to Y0 + H_in
    # Runs west to TL = (X0, Y0 + H_in)
    
    X_step_east = X0 + W_in - 35.80 * 12.0
    X_step_west = X0 + (6.0 + 32.8 + 10.1 + 9.8) * 12.0
    Y_recess = Y0 + H_in - 5.0 * 12.0
    
    # South Fence (Bottom)
    draw_fence_line(msp, (X0, Y0), (X0 + W_in, Y0), cross_spacing=96.0)
    
    # East Fence (Right)
    draw_fence_line(msp, (X0 + W_in, Y0), (X0 + W_in, Y0 + H_in), cross_spacing=96.0)
    
    # North Fence (Top segments)
    draw_fence_line(msp, (X0 + W_in, Y0 + H_in), (X_step_east, Y0 + H_in), cross_spacing=96.0)
    # Step down line
    msp.add_line((X_step_east, Y0 + H_in), (X_step_east, Y_recess), dxfattribs={"layer": "0", "color": 7})
    # Recessed run
    draw_fence_line(msp, (X_step_east, Y_recess), (X_step_west, Y_recess), cross_spacing=96.0)
    # Step up line
    msp.add_line((X_step_west, Y_recess), (X_step_west, Y0 + H_in), dxfattribs={"layer": "0", "color": 7})
    # Top left run
    draw_fence_line(msp, (X_step_west, Y0 + H_in), (X0, Y0 + H_in), cross_spacing=96.0)
    
    # West Fence (Left) with Gates
    # Gates:
    # Double swing gate: 18.0' (216.0") between Y_gate1_bot and Y_gate1_top
    # Pedestrian gate: 2.1' (25.2") between Y_gate2_bot and Y_gate2_top
    Y_gate1_bot = Y0 + (5.5 + 11.28 + 4.0) * 12.0  # Y0 + 249.36
    Y_gate1_top = Y_gate1_bot + 18.0 * 12.0        # Y0 + 465.36
    Y_gate2_bot = Y_gate1_top + 2.3 * 12.0         # Y0 + 492.96
    Y_gate2_top = Y_gate2_bot + 2.1 * 12.0         # Y0 + 518.16
    
    # Solid sections of West fence
    draw_fence_line(msp, (X0, Y0), (X0, Y_gate1_bot), cross_spacing=96.0)
    # Post / Gate 1 opening
    msp.add_circle((X0, Y_gate1_bot), 3.0, dxfattribs={"layer": "0", "color": 7})
    msp.add_circle((X0, Y_gate1_top), 3.0, dxfattribs={"layer": "0", "color": 7})
    # Gate swing lines and arcs for 18' double gate (two 9' leaves)
    leaf = 9.0 * 12.0
    msp.add_line((X0, Y_gate1_bot), (X0 - leaf * 0.707, Y_gate1_bot + leaf * 0.707), dxfattribs={"layer": "0", "color": 7})
    msp.add_line((X0, Y_gate1_top), (X0 - leaf * 0.707, Y_gate1_top - leaf * 0.707), dxfattribs={"layer": "0", "color": 7})
    msp.add_arc((X0, Y_gate1_bot), leaf, 90.0, 135.0, dxfattribs={"layer": "0", "color": 7, "linetype": "DASHED"})
    msp.add_arc((X0, Y_gate1_top), leaf, 225.0, 270.0, dxfattribs={"layer": "0", "color": 7, "linetype": "DASHED"})
    
    # Middle fence post between gates
    draw_fence_line(msp, (X0, Y_gate1_top), (X0, Y_gate2_bot), cross_spacing=96.0)
    
    # Gate 2 opening (2.1' pedestrian gate)
    msp.add_circle((X0, Y_gate2_bot), 2.5, dxfattribs={"layer": "0", "color": 7})
    msp.add_circle((X0, Y_gate2_top), 2.5, dxfattribs={"layer": "0", "color": 7})
    leaf2 = 2.1 * 12.0
    msp.add_line((X0, Y_gate2_bot), (X0 - leaf2 * 0.707, Y_gate2_bot + leaf2 * 0.707), dxfattribs={"layer": "0", "color": 7})
    msp.add_arc((X0, Y_gate2_bot), leaf2, 90.0, 135.0, dxfattribs={"layer": "0", "color": 7, "linetype": "DASHED"})
    
    # Upper West fence
    draw_fence_line(msp, (X0, Y_gate2_top), (X0, Y0 + H_in), cross_spacing=96.0)
    
    # Gate text labels
    msp.add_text("18.0' DOUBLE SWING GATE", dxfattribs={"layer": "TEXT", "height": 6.0, "rotation": 90.0, "style": "Standard"}).set_placement((X0 - 25.0, (Y_gate1_bot + Y_gate1_top) / 2.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("2.1' PED. GATE", dxfattribs={"layer": "TEXT", "height": 5.0, "rotation": 90.0, "style": "Standard"}).set_placement((X0 - 20.0, (Y_gate2_bot + Y_gate2_top) / 2.0), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # ---------------------------------------------------------
    # 2. Equipment Objects & Foundations
    # ---------------------------------------------------------
    
    # --- Shelter A ---
    XA = X0 + 3.0 * 12.0
    YA = Y0 + 5.5 * 12.0
    WA = 8.55 * 12.0   # width along X = 102.6"
    HA = 11.74 * 12.0  # height along Y = 140.88"
    draw_rect(msp, XA, YA, WA, HA, layer="0")
    draw_rect(msp, XA + 4.0, YA + 4.0, WA - 8.0, HA - 8.0, layer="0")
    draw_bubble(msp, XA + WA / 2.0, YA + HA / 2.0, "A", radius=10.0)
    msp.add_text("SHELTER A", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((XA + WA / 2.0, YA - 12.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("11.74' x 8.55'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XA + WA / 2.0, YA - 22.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Fuel Tank B ---
    XB_pad = XA + WA + 14.7 * 12.0
    YB_pad = YA
    WB_pad = 10.85 * 12.0
    HB_pad = 3.46 * 12.0
    draw_rect(msp, XB_pad, YB_pad, WB_pad, HB_pad, layer="0")
    WT = 14.69 * 12.0
    HT = 2.84 * 12.0
    c_tank_x = XB_pad + WB_pad / 2.0
    c_tank_y = YB_pad + HB_pad / 2.0
    tank_r = HT / 2.0
    tank_l = WT - 2.0 * tank_r
    msp.add_line((c_tank_x - tank_l / 2.0, c_tank_y - tank_r), (c_tank_x + tank_l / 2.0, c_tank_y - tank_r), dxfattribs={"layer": "0", "color": 7})
    msp.add_line((c_tank_x - tank_l / 2.0, c_tank_y + tank_r), (c_tank_x + tank_l / 2.0, c_tank_y + tank_r), dxfattribs={"layer": "0", "color": 7})
    msp.add_arc((c_tank_x + tank_l / 2.0, c_tank_y), tank_r, 270.0, 90.0, dxfattribs={"layer": "0", "color": 7})
    msp.add_arc((c_tank_x - tank_l / 2.0, c_tank_y), tank_r, 90.0, 270.0, dxfattribs={"layer": "0", "color": 7})
    draw_bubble(msp, c_tank_x, c_tank_y, "B", radius=10.0)
    msp.add_text("FUEL TANK B", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((c_tank_x, YB_pad - 12.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("14.69' x 2.84'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((c_tank_x, YB_pad - 22.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Generator C on Pad ---
    XC_pad = X0 + 44.5 * 12.0
    YC_pad = Y0 + 28.0 * 12.0
    WC_pad = 7.16 * 12.0
    HC_pad = 3.90 * 12.0
    draw_rect(msp, XC_pad, YC_pad, WC_pad, HC_pad, layer="0")
    WC_gen = 4.90 * 12.0
    HC_gen = 2.37 * 12.0
    draw_rect(msp, XC_pad + (WC_pad - WC_gen) / 2.0, YC_pad + (HC_pad - HC_gen) / 2.0, WC_gen, HC_gen, layer="0")
    draw_bubble(msp, XC_pad + WC_pad / 2.0, YC_pad + HC_pad / 2.0, "C", radius=9.0)
    msp.add_text("GENERATOR C", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((XC_pad + WC_pad / 2.0, YC_pad - 12.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("4.90' x 2.37'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XC_pad + WC_pad / 2.0, YC_pad - 22.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Shelter D & Shelter E ---
    YD_top = Y0 + H_in - 8.6 * 12.0
    HD = 22.88 * 12.0
    YD = YD_top - HD
    XD = X0 + (6.0 + 32.8) * 12.0  # 38.8' = 465.6"
    WD = 18.48 * 12.0
    draw_rect(msp, XD, YD, WD, HD, layer="0")
    draw_rect(msp, XD + 5.0, YD + 5.0, WD - 10.0, HD - 10.0, layer="0")
    draw_bubble(msp, XD + WD / 2.0, YD + HD / 2.0, "D", radius=12.0)
    msp.add_text("SHELTER D", dxfattribs={"layer": "TEXT", "height": 7.0, "style": "Standard"}).set_placement((XD + WD / 2.0, YD + 32.0), align=TextEntityAlignment.BOTTOM_CENTER)
    msp.add_text("18.48' x 22.88'", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((XD + WD / 2.0, YD + 18.0), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # Shelter E
    WE = 13.33 * 12.0
    HE = 17.98 * 12.0
    XE = XD - WE
    YE = YD + (HD - HE) / 2.0
    draw_rect(msp, XE, YE, WE, HE, layer="0")
    draw_rect(msp, XE + 5.0, YE + 5.0, WE - 10.0, HE - 10.0, layer="0")
    draw_bubble(msp, XE + WE / 2.0, YE + HE / 2.0, "E", radius=11.0)
    msp.add_text("SHELTER E", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((XE + WE / 2.0, YE + 26.0), align=TextEntityAlignment.BOTTOM_CENTER)
    msp.add_text("17.71' x 10.54'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XE + WE / 2.0, YE + 14.0), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # ACU F (2 units): 2.60' x 1.20' (31.2" x 14.4") on East wall of D
    WF = 1.20 * 12.0  # projection out from wall
    HF = 2.60 * 12.0  # along wall
    XF = XD + WD
    YF1 = YD + HD * 0.30
    YF2 = YD + HD * 0.65
    draw_rect(msp, XF, YF1, WF, HF, layer="0")
    draw_rect(msp, XF, YF2, WF, HF, layer="0")
    draw_bubble(msp, XF + WF + 14.0, YF1 + HF / 2.0, "F", radius=7.0)
    draw_bubble(msp, XF + WF + 14.0, YF2 + HF / 2.0, "F", radius=7.0)
    msp.add_text("ACU F (TYP. 2)", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XF + WF + 28.0, (YF1 + YF2) / 2.0), align=TextEntityAlignment.MIDDLE_LEFT)
    
    # --- Equipment Canopy / Pad (G, H, GPS) ---
    # Setback: 9.8' east of Shelter D
    XG_pad = XD + WD + 9.8 * 12.0
    WG_pad = 7.70 * 12.0
    HG_pad = 9.81 * 12.0
    YG_pad = YD + (HD - HG_pad) / 2.0
    draw_rect(msp, XG_pad, YG_pad, WG_pad, HG_pad, layer="0")
    
    # Hatch strip on East side of pad (canopy column / frame)
    w_strip = 2.0 * 12.0
    x_strip = XG_pad + WG_pad - w_strip
    draw_rect(msp, x_strip, YG_pad, w_strip, HG_pad, layer="0")
    # Diagonal hatching lines
    n_hatch = 10
    for h_i in range(n_hatch):
        hy = YG_pad + h_i * (HG_pad / n_hatch)
        msp.add_line((x_strip, hy), (x_strip + w_strip, hy + w_strip), dxfattribs={"layer": "0", "color": 7})
        
    # ACU H: 5.08' x 2.82' (60.96" x 33.84")
    WH = 2.82 * 12.0
    HH = 5.08 * 12.0
    XH = XG_pad + 10.0
    YH = YG_pad + (HG_pad - HH) / 2.0
    draw_rect(msp, XH, YH, WH, HH, layer="0")
    draw_bubble(msp, XH + WH / 2.0, YH + HH / 2.0, "H", radius=8.0)
    
    # Outdoor Cabinet G: 1.80' x 0.70' (21.6" x 8.4")
    WG = 0.70 * 12.0
    HG = 1.80 * 12.0
    XG = XH + WH + 8.0
    YG = YH + 8.0
    draw_rect(msp, XG, YG, WG, HG, layer="0")
    draw_bubble(msp, XG + WG / 2.0, YG + HG / 2.0, "G", radius=7.0)
    
    # GPS Antenna circle on NE corner of canopy
    X_gps = XG_pad + WG_pad
    Y_gps = YG_pad + HG_pad
    msp.add_circle((X_gps, Y_gps), 5.0, dxfattribs={"layer": "0", "color": 7})
    msp.add_text("GPS", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((X_gps - 8.0, Y_gps + 10.0), align=TextEntityAlignment.BOTTOM_RIGHT)
    
    # Canopy Pad Label
    msp.add_text("CANOPY / PAD", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((XG_pad + WG_pad / 2.0, YG_pad - 12.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("7.70' x 9.81'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XG_pad + WG_pad / 2.0, YG_pad - 22.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Monopole Tower ---
    # Location: 24.65' east of canopy pad east edge
    X_MP = XG_pad + WG_pad + 24.65 * 12.0  # X0 + 1193.2"
    Y_MP = YG_pad + HG_pad / 2.0           # Centered with ice bridge
    
    # Tower base graphics (base plate, pole circle, bolts, centerlines)
    r_base = 24.0   # 48" dia base flange
    r_pole = 15.0   # 30" dia pole
    msp.add_circle((X_MP, Y_MP), r_base, dxfattribs={"layer": "MP", "color": 7})
    msp.add_circle((X_MP, Y_MP), r_pole, dxfattribs={"layer": "MP", "color": 7})
    # 12 anchor bolts
    for b_idx in range(12):
        angle = math.radians(b_idx * 30.0)
        bx = X_MP + (r_base - 4.0) * math.cos(angle)
        by = Y_MP + (r_base - 4.0) * math.sin(angle)
        msp.add_circle((bx, by), 2.0, dxfattribs={"layer": "MP", "color": 7})
    # Centerlines
    msp.add_line((X_MP - r_base - 10.0, Y_MP), (X_MP + r_base + 10.0, Y_MP), dxfattribs={"layer": "MP", "color": 7, "linetype": "CENTER"})
    msp.add_line((X_MP, Y_MP - r_base - 10.0), (X_MP, Y_MP + r_base + 10.0), dxfattribs={"layer": "MP", "color": 7, "linetype": "CENTER"})
    msp.add_text("MONOPOLE TOWER", dxfattribs={"layer": "TEXT", "height": 7.0, "style": "Standard"}).set_placement((X_MP, Y_MP - r_base - 14.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("ELEV: 60.0'", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((X_MP, Y_MP - r_base - 24.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Existing Ice Bridge ---
    # Width 2.0' (24.0"), runs from canopy east edge across monopole to equipment pad L
    X_IB_start = XG_pad + WG_pad
    X_IB_end = X_MP + 7.8 * 12.0  # reaches Equipment Pad L
    W_IB = 24.0
    Y_IB_bot = Y_MP - W_IB / 2.0
    Y_IB_top = Y_MP + W_IB / 2.0
    
    # Outer bridge rails
    msp.add_line((X_IB_start, Y_IB_bot), (X_IB_end, Y_IB_bot), dxfattribs={"layer": "ICE Bridge", "color": 7})
    msp.add_line((X_IB_start, Y_IB_top), (X_IB_end, Y_IB_top), dxfattribs={"layer": "ICE Bridge", "color": 7})
    # Bridge rungs every 12"
    rung_spacing = 12.0
    n_rungs = int((X_IB_end - X_IB_start) / rung_spacing)
    for r_i in range(1, n_rungs):
        rx = X_IB_start + r_i * rung_spacing
        # Don't draw rungs through monopole pole
        if abs(rx - X_MP) > r_pole:
            msp.add_line((rx, Y_IB_bot), (rx, Y_IB_top), dxfattribs={"layer": "ICE Bridge", "color": 7})
            
    msp.add_text("EXISTING ICE BRIDGE (2.0' WIDE)", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement(((X_IB_start + X_MP) / 2.0, Y_IB_top + 8.0), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # --- Equipment Pad L (L, M, N, O, K) ---
    # Size: 7.82' x 9.27' (93.84" x 111.24")
    # Setback: 7.8' from Monopole
    XL_pad = X_IB_end
    WL_pad = 7.82 * 12.0
    HL_pad = 9.27 * 12.0
    YL_pad = Y_MP - HL_pad * 0.60
    draw_rect(msp, XL_pad, YL_pad, WL_pad, HL_pad, layer="0")
    
    # Inside Pad L:
    # Cabinet L: 5.54' x 3.25' (66.48" x 39.0")
    WL_cab = 5.54 * 12.0
    HL_cab = 3.25 * 12.0
    XL_cab = XL_pad + (WL_pad - WL_cab) / 2.0
    YL_cab = YL_pad + HL_pad - HL_cab - 12.0
    draw_rect(msp, XL_cab, YL_cab, WL_cab, HL_cab, layer="0")
    draw_bubble(msp, XL_cab + WL_cab / 2.0, YL_cab + HL_cab / 2.0, "L", radius=9.0)
    
    # Power Box M: 1.40' x 0.50' (16.8" x 6.0")
    WM = 1.40 * 12.0
    HM = 0.50 * 12.0
    XM = XL_cab - WM - 4.0
    YM = YL_cab + (HL_cab - HM) / 2.0
    draw_rect(msp, XM, YM, WM, HM, layer="0")
    draw_bubble(msp, XM + WM / 2.0, YM - 12.0, "M", radius=7.0)
    
    # Power Box O: 1.98' x 1.23' (23.76" x 14.76")
    WO = 1.98 * 12.0
    HO = 1.23 * 12.0
    XO = XL_cab + WL_cab + 4.0
    YO = YL_cab + (HL_cab - HO) / 2.0
    draw_rect(msp, XO, YO, WO, HO, layer="0")
    draw_bubble(msp, XO + WO / 2.0, YO - 12.0, "O", radius=7.0)
    
    # ACU N (2 units): 1.90' x 0.70' (22.8" x 8.4")
    WN = 1.90 * 12.0
    HN = 0.70 * 12.0
    XN1 = XL_cab + 6.0
    XN2 = XL_cab + WL_cab - WN - 6.0
    YN = YL_pad + 12.0
    draw_rect(msp, XN1, YN, WN, HN, layer="0")
    draw_rect(msp, XN2, YN, WN, HN, layer="0")
    draw_bubble(msp, XN1 + WN / 2.0, YN + HN / 2.0, "N", radius=7.0)
    draw_bubble(msp, XN2 + WN / 2.0, YN + HN / 2.0, "N", radius=7.0)
    
    # Ground Well K near Pad L
    XK = XL_pad - 16.0
    YK = YL_pad - 12.0
    msp.add_circle((XK, YK), 5.0, dxfattribs={"layer": "0", "color": 7})
    draw_bubble(msp, XK - 14.0, YK, "K", radius=7.0)
    
    msp.add_text("EQUIPMENT PAD L", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((XL_pad + WL_pad / 2.0, YL_pad - 12.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("9.27' x 7.82'", dxfattribs={"layer": "TEXT", "height": 5.5, "style": "Standard"}).set_placement((XL_pad + WL_pad / 2.0, YL_pad - 22.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Meter Bank / Power Boxes I, J ---
    # South of Pad L
    XI_pad = XL_pad + 10.0
    YI_pad = YL_pad - 50.0
    # H-frame channel lines
    msp.add_line((XI_pad - 10.0, YI_pad), (XI_pad + 65.0, YI_pad), dxfattribs={"layer": "0", "color": 7})
    msp.add_circle((XI_pad, YI_pad), 3.0, dxfattribs={"layer": "0", "color": 7})
    msp.add_circle((XI_pad + 55.0, YI_pad), 3.0, dxfattribs={"layer": "0", "color": 7})
    # Power Box I: 0.97' x 0.35' (11.64" x 4.2")
    WI = 0.97 * 12.0
    HI = 0.35 * 12.0
    draw_rect(msp, XI_pad + 6.0, YI_pad + 4.0, WI, HI, layer="0")
    draw_bubble(msp, XI_pad + 6.0 + WI / 2.0, YI_pad + 20.0, "I", radius=7.0)
    # Power Box J: 2.46' x 0.89' (29.52" x 10.68")
    WJ = 2.46 * 12.0
    HJ = 0.89 * 12.0
    draw_rect(msp, XI_pad + 22.0, YI_pad + 4.0, WJ, HJ, layer="0")
    draw_bubble(msp, XI_pad + 22.0 + WJ / 2.0, YI_pad + 25.0, "J", radius=7.0)
    # Ground Well K circle
    XK2 = XI_pad + 58.0
    YK2 = YI_pad - 16.0
    msp.add_circle((XK2, YK2), 5.0, dxfattribs={"layer": "0", "color": 7})
    draw_bubble(msp, XK2, YK2 - 14.0, "K", radius=7.0)
    
    # --- Transformer Pad (Diamond) ---
    # Size 3.73' x 3.77' (44.76" x 45.24"), rotated 45 deg
    XT_pad = XL_pad + WL_pad + 45.0
    YT_pad = Y_MP - 10.0
    draw_rotated_rect(msp, XT_pad, YT_pad, 3.73 * 12.0, 3.77 * 12.0, angle_deg=45.0, layer="0")
    msp.add_text("TRANSFORMER PAD", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((XT_pad, YT_pad - 35.0), align=TextEntityAlignment.TOP_CENTER)
    msp.add_text("3.73' x 3.77'", dxfattribs={"layer": "TEXT", "height": 5.0, "style": "Standard"}).set_placement((XT_pad, YT_pad - 45.0), align=TextEntityAlignment.TOP_CENTER)
    
    # --- Generator / Aux Pad ---
    # Size 2.80' x 4.17' (33.6" x 50.04")
    XG2_pad = XT_pad - 15.0
    YG2_pad = Y_MP + 70.0
    draw_rect(msp, XG2_pad, YG2_pad, 2.80 * 12.0, 4.17 * 12.0, layer="0")
    msp.add_text("AUX PAD", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((XG2_pad + 16.8, YG2_pad + 68.0), align=TextEntityAlignment.BOTTOM_CENTER)
    msp.add_text("2.80' x 4.17'", dxfattribs={"layer": "TEXT", "height": 5.0, "style": "Standard"}).set_placement((XG2_pad + 16.8, YG2_pad + 58.0), align=TextEntityAlignment.BOTTOM_CENTER)
    
    # ---------------------------------------------------------
    # 3. Outer & Intermediate Dimensions (Strict Decimal Feet)
    # ---------------------------------------------------------
    dim_layer = "Dim Compound"
    
    # --- TOP DIMENSIONS ---
    # Overall top: 137.33'
    draw_tick_dim(msp, (X0, Y0 + H_in), (X0 + W_in, Y0 + H_in), offset=70.0, text="137.33'", layer=dim_layer)
    # Sub-segments along top:
    # 6.00', 32.80', 10.10', 9.80', 24.65', 7.80', 7.60', 2.80', 35.80'
    top_segs = [
        (0.0, 6.0, "6.00'"),
        (6.0, 6.0 + 32.8, "32.80'"),
        (38.8, 38.8 + 10.1, "10.10'"),
        (48.9, 48.9 + 9.8, "9.80'"),
        (58.7, 58.7 + 24.65, "24.65'"),
        (83.35, 83.35 + 7.8, "7.80'"),
        (91.15, 91.15 + 7.6, "7.60'"),
        (98.75, 98.75 + 2.8, "2.80'"),
        (101.55, 137.33, "35.80'")
    ]
    for s_x1, s_x2, s_txt in top_segs:
        draw_tick_dim(
            msp,
            (X0 + s_x1 * 12.0, Y0 + H_in),
            (X0 + s_x2 * 12.0, Y0 + H_in),
            offset=35.0,
            text=s_txt,
            layer=dim_layer,
            tick_len=4.5,
            text_h=5.5
        )
        
    # --- BOTTOM DIMENSIONS ---
    # Overall bottom: 137.33'
    draw_tick_dim(msp, (X0, Y0), (X0 + W_in, Y0), offset=-65.0, text="137.33'", layer=dim_layer)
    # Segments: 3.00', 8.50', 14.70', 15.70', 95.43'
    bot_segs = [
        (0.0, 3.0, "3.00'"),
        (3.0, 3.0 + 8.5, "8.50'"),
        (11.5, 11.5 + 14.7, "14.70'"),
        (26.2, 26.2 + 15.7, "15.70'"),
        (41.9, 137.33, "95.43'")
    ]
    for s_x1, s_x2, s_txt in bot_segs:
        draw_tick_dim(
            msp,
            (X0 + s_x1 * 12.0, Y0),
            (X0 + s_x2 * 12.0, Y0),
            offset=-32.0,
            text=s_txt,
            layer=dim_layer,
            tick_len=4.5,
            text_h=5.5
        )
        
    # --- LEFT (WEST) DIMENSIONS ---
    # Overall left: 73.68'
    draw_tick_dim(msp, (X0, Y0), (X0, Y0 + H_in), offset=70.0, text="73.68'", layer=dim_layer)
    # Segments: 5.50', 11.28', 4.00', 18.00', 2.10', 2.30', 1.60', 20.30', 8.60'
    left_segs = [
        (0.0, 5.5, "5.50'"),
        (5.5, 5.5 + 11.28, "11.28'"),
        (16.78, 16.78 + 4.0, "4.00'"),
        (20.78, 20.78 + 18.0, "18.00'"),
        (38.78, 38.78 + 2.1, "2.10'"),
        (40.88, 40.88 + 2.3, "2.30'"),
        (43.18, 43.18 + 1.6, "1.60'"),
        (44.78, 44.78 + 20.3, "20.30'"),
        (65.08, 73.68, "8.60'")
    ]
    for s_y1, s_y2, s_txt in left_segs:
        draw_tick_dim(
            msp,
            (X0, Y0 + s_y1 * 12.0),
            (X0, Y0 + s_y2 * 12.0),
            offset=35.0,
            text=s_txt,
            layer=dim_layer,
            tick_len=4.5,
            text_h=5.2
        )
        
    # --- RIGHT (EAST) DIMENSIONS ---
    # Overall right: 73.68'
    draw_tick_dim(msp, (X0 + W_in, Y0), (X0 + W_in, Y0 + H_in), offset=-65.0, text="73.68'", layer=dim_layer)
    # Segments: 24.14', 33.54', 5.00', 2.00', 4.00', 5.00'
    right_segs = [
        (0.0, 24.14, "24.14'"),
        (24.14, 24.14 + 33.54, "33.54'"),
        (57.68, 57.68 + 5.0, "5.00'"),
        (62.68, 62.68 + 2.0, "2.00'"),
        (64.68, 64.68 + 4.0, "4.00'"),
        (68.68, 73.68, "5.00'")
    ]
    for s_y1, s_y2, s_txt in right_segs:
        draw_tick_dim(
            msp,
            (X0 + W_in, Y0 + s_y1 * 12.0),
            (X0 + W_in, Y0 + s_y2 * 12.0),
            offset=-32.0,
            text=s_txt,
            layer=dim_layer,
            tick_len=4.5,
            text_h=5.2
        )
        
    # ---------------------------------------------------------
    # 4. Equipment & Foundation Legend Table (Left Side)
    # ---------------------------------------------------------
    # Table layout:
    # X: 20.0 to 360.0 (Width = 340.0")
    # Y: 100.0 to 920.0 (Height = 820.0")
    T_X0 = 20.0
    T_Y0 = 100.0
    T_W = 340.0
    T_H = 820.0
    
    # Outer box
    draw_rect(msp, T_X0, T_Y0, T_W, T_H, layer="0")
    
    # Header box
    hdr_h = 45.0
    draw_rect(msp, T_X0, T_Y0 + T_H - hdr_h, T_W, hdr_h, layer="0")
    msp.add_text(
        "EQUIPMENT & FOUNDATION LEGEND",
        dxfattribs={"layer": "TEXT", "height": 9.0, "style": "Standard"}
    ).set_placement((T_X0 + T_W / 2.0, T_Y0 + T_H - hdr_h / 2.0), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Column Header row
    col_hdr_h = 28.0
    draw_rect(msp, T_X0, T_Y0 + T_H - hdr_h - col_hdr_h, T_W, col_hdr_h, layer="0")
    c1_w = 45.0   # MARK
    c2_w = 165.0  # DESCRIPTION
    c3_w = 130.0  # DIMENSIONS
    
    # Column divider lines
    msp.add_line((T_X0 + c1_w, T_Y0), (T_X0 + c1_w, T_Y0 + T_H - hdr_h), dxfattribs={"layer": "0", "color": 7})
    msp.add_line((T_X0 + c1_w + c2_w, T_Y0), (T_X0 + c1_w + c2_w, T_Y0 + T_H - hdr_h), dxfattribs={"layer": "0", "color": 7})
    
    # Column header texts
    y_col_text = T_Y0 + T_H - hdr_h - col_hdr_h / 2.0
    msp.add_text("ITEM", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((T_X0 + c1_w / 2.0, y_col_text), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("EQUIPMENT DESCRIPTION", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((T_X0 + c1_w + c2_w / 2.0, y_col_text), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("DIMENSIONS", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((T_X0 + c1_w + c2_w + c3_w / 2.0, y_col_text), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Table rows
    legend_items = [
        ("A", "Shelter", "11.74' x 8.55'"),
        ("B", "Fuel Tank (Pad: 10.85' x 3.46')", "14.69' x 2.84'"),
        ("C", "Generator on Pad (7.16' x 3.90')", "4.90' x 2.37'"),
        ("D", "Equipment Shelter", "18.48' x 22.88'"),
        ("E", "Equipment Shelter", "17.71' x 10.54'"),
        ("F", "ACU (2 Units on Shelter D)", "2.60' x 1.20'"),
        ("G", "Outdoor Cabinet", "1.80' x 0.70'"),
        ("H", "ACU (Canopy Pad: 7.70' x 9.81')", "5.08' x 2.82'"),
        ("I", "Power Box (Meter Bank)", "0.97' x 0.35'"),
        ("J", "Power Box (Meter Bank)", "2.46' x 0.89'"),
        ("K", "Ground Well (2 Locations)", "%%C 0.70'"),
        ("L", "Outdoor Cabinet (Pad: 9.27' x 7.82')", "5.54' x 3.25'"),
        ("M", "Power Box", "1.40' x 0.50'"),
        ("N", "ACU (2 Units on Pad L)", "1.90' x 0.70'"),
        ("O", "Power Box", "1.98' x 1.23'"),
        ("T1", "Transformer Pad (Diamond)", "3.73' x 3.77'"),
        ("T2", "Auxiliary / Generator Pad", "2.80' x 4.17'"),
        ("MP", "Monopole Tower Base", "%%C 2.50' (Flange %%C 4.00')")
    ]
    
    row_h = (T_H - hdr_h - col_hdr_h) / len(legend_items)
    
    for idx, (mark, desc, dims) in enumerate(legend_items):
        r_top = T_Y0 + T_H - hdr_h - col_hdr_h - idx * row_h
        r_bot = r_top - row_h
        r_mid = (r_top + r_bot) / 2.0
        
        # Row divider
        msp.add_line((T_X0, r_bot), (T_X0 + T_W, r_bot), dxfattribs={"layer": "0", "color": 7})
        
        # Mark bubble or text
        if len(mark) <= 2:
            draw_bubble(msp, T_X0 + c1_w / 2.0, r_mid, mark, radius=8.0)
        else:
            msp.add_text(mark, dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((T_X0 + c1_w / 2.0, r_mid), align=TextEntityAlignment.MIDDLE_CENTER)
            
        # Description
        msp.add_text(desc, dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((T_X0 + c1_w + 8.0, r_mid), align=TextEntityAlignment.MIDDLE_LEFT)
        
        # Dimensions
        msp.add_text(dims, dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((T_X0 + c1_w + c2_w + 8.0, r_mid), align=TextEntityAlignment.MIDDLE_LEFT)
        
    # ---------------------------------------------------------
    # 5. North Arrow & Drawing Title / Scale
    # ---------------------------------------------------------
    NA_X = X0 + W_in + 120.0
    NA_Y = Y0 + H_in - 50.0
    # North Arrow symbol
    msp.add_circle((NA_X, NA_Y), 25.0, dxfattribs={"layer": "0", "color": 7})
    # Arrow head pointing UP
    pts_arrow_l = [(NA_X, NA_Y + 24.0), (NA_X - 10.0, NA_Y - 12.0), (NA_X, NA_Y - 4.0)]
    pts_arrow_r = [(NA_X, NA_Y + 24.0), (NA_X, NA_Y - 4.0), (NA_X + 10.0, NA_Y - 12.0)]
    msp.add_lwpolyline(pts_arrow_l, close=True, dxfattribs={"layer": "0", "color": 7})
    msp.add_lwpolyline(pts_arrow_r, close=True, dxfattribs={"layer": "0", "color": 7})
    # Solid hatch left side of arrow
    hatch_na = msp.add_hatch(dxfattribs={"layer": "0", "color": 7})
    hatch_na.set_pattern_fill("SOLID")
    hatch_na.paths.add_polyline_path(pts_arrow_l, is_closed=True)
    msp.add_text("N", dxfattribs={"layer": "TEXT", "height": 14.0, "style": "Standard"}).set_placement((NA_X, NA_Y + 32.0), align=TextEntityAlignment.BOTTOM_CENTER)
    msp.add_text("NORTH", dxfattribs={"layer": "TEXT", "height": 6.5, "style": "Standard"}).set_placement((NA_X, NA_Y - 32.0), align=TextEntityAlignment.TOP_CENTER)
    
    # Title & Notes block (No kop - clean drawing label)
    title_x = X0 + W_in / 2.0
    title_y = Y0 - 95.0
    msp.add_text("SITE NUMBER: US1051600", dxfattribs={"layer": "TEXT", "height": 9.0, "style": "Standard"}).set_placement((title_x, title_y), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("SITE NAME: QUEMADO", dxfattribs={"layer": "TEXT", "height": 8.0, "style": "Standard"}).set_placement((title_x, title_y - 15.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("COMPOUND PLAN - PAGE 04", dxfattribs={"layer": "TEXT", "height": 11.0, "style": "Standard"}).set_placement((title_x, title_y - 32.0), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("ALL DIMENSIONS IN DECIMAL FEET. SCALE: 1\" = 10'-0\" (N.T.S.)", dxfattribs={"layer": "TEXT", "height": 6.0, "style": "Standard"}).set_placement((title_x, title_y - 48.0), align=TextEntityAlignment.MIDDLE_CENTER)

    # Save final DXF
    out_dxf = OUT_BASE + ".dxf"
    doc.saveas(out_dxf)
    print(f"Saved DXF: {out_dxf}")
    return out_dxf

# -------------------------------------------------------------
# AutoCAD Core Console Plotting & Conversion
# -------------------------------------------------------------
def plot_dwg_pdf(dxf_path):
    out_dwg = OUT_BASE + ".dwg"
    out_pdf = OUT_BASE + ".pdf"
    out_png = OUT_BASE + ".png"
    
    scr_path = r"c:\Apps\cad\plot_p04.scr"
    
    # Model space plot bounds:
    # X: 0.0 to 2260.0
    # Y: -80.0 to 1080.0
    scr_lines = [
        '(setvar "EXPERT" 2)',
        '(setvar "CTAB" "Model")',
        f'DXFIN "{dxf_path}"',
        '-PLOT',
        'Y',
        'Model',
        'AutoCAD PDF (General Documentation).pc3',
        'ANSI B (17.00 x 11.00 Inches)',
        'I',
        'L',
        'N',
        'W',
        '0.0,-80.0',
        '2260.0,1080.0',
        'Fit',
        'Center',
        'Y',
        'acad.ctb',
        'N',
        'N',
        f'"{out_pdf}"',
        'N',
        'Y',
        f'SAVEAS 2018 "{out_dwg}"',
        'QUIT Y\n'
    ]
    with open(scr_path, "w") as f:
        f.write("\n".join(scr_lines))
        
    print("Running AutoCAD Core Console to plot DWG and PDF...")
    cmd = [ACCORECONSOLE, "/s", scr_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"AutoCAD return code: {res.returncode}")
    
    if not os.path.exists(out_pdf):
        print("ERROR: PDF was not generated. Log output:")
        print(res.stdout[-1500:])
        return False
        
    print(f"Successfully generated PDF: {out_pdf}")
    print(f"Successfully generated DWG: {out_dwg}")
    
    # Convert PDF to high-res crisp PNG (300 DPI)
    print("Converting PDF to 300 DPI crisp PNG...")
    pdf_doc = fitz.open(out_pdf)
    page = pdf_doc.load_page(0)
    zoom = 300.0 / 72.0  # 300 DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.save(out_png)
    pdf_doc.close()
    
    print(f"Successfully saved PNG: {out_png}")
    
    # Auto crop white margins
    im = Image.open(out_png)
    bbox = im.getbbox()
    if bbox:
        w, h = im.size
        pad = 25
        cb = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
        cropped = im.crop(cb)
        cropped.save(out_png)
        print(f"Tightly cropped PNG to: {cropped.size}")
        
    # Copy to artifacts directory for user viewing
    artifact_png = r"C:\Users\dgani\.gemini\antigravity\brain\57dd21c3-cde2-46cb-8770-9ac78d79704e\US1051600_Quemado_Page-04.png"
    im = Image.open(out_png)
    im.save(artifact_png)
    print(f"Copied preview to artifact: {artifact_png}")
    
    return True

if __name__ == "__main__":
    dxf = generate_page04()
    success = plot_dwg_pdf(dxf)
    if success:
        print("\n=== PAGE-04 GENERATION COMPLETE ===")
    else:
        print("\n=== PAGE-04 GENERATION FAILED ===")
        sys.exit(1)
