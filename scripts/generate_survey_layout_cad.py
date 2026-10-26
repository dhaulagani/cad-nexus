r"""
Telecom Site Survey to Precision 2D CAD Generator
Site: US1051671_Blue Diamond
Subject: Compound Layout & Equipment Plan
Generates:
  1. US1051671_Blue_Diamond_Compound_Layout.dxf (Professional Layered 2D CAD)
  2. US1051671_Blue_Diamond_Compound_Layout.png (High-Res 300 DPI Drawing)
  3. Compound_Layout_Comparison.png (Survey Sketch vs Clean CAD side-by-side)
"""

import os
import math
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment

OUTPUT_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\RAW\Layout"
SURVEY_SKETCH_PATH = os.path.join(OUTPUT_DIR, "Compound.jpeg")
DXF_PATH = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout.dxf")
PNG_PATH = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout.png")
PLOT_PATH = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout_Plot.png")
COMPARISON_PATH = os.path.join(OUTPUT_DIR, "Compound_Layout_Comparison.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# GEOMETRY & COORDINATES (All dimensions in Feet, US Survey)
# Origin (0,0) at South-West (Bottom-Left) corner of Compound Fence
# +X = East, +Y = North
# -------------------------------------------------------------

# Compound Dimensions
COMPOUND_W = 20.10  # East-West (X)
COMPOUND_H = 20.10  # North-South (Y)

# Gate at North Fence
GATE_OFFSET_X = 4.00    # from West fence
GATE_WIDTH = 12.12      # Double swing opening
GATE_END_X = GATE_OFFSET_X + GATE_WIDTH  # 16.12 ft
GATE_EAST_FENCE = COMPOUND_W - GATE_END_X  # 3.98 ft

# Tower & Foundation
TOWER_CX = 4.90   # from West fence
TOWER_CY = 4.30   # from South fence
PAD_OCT_SIZE = 5.00  # 5' x 5' octagonal pad
TOWER_POLE_DIA = 2.20  # Monopole base diameter

# Calculate 8 vertices of regular octagon inscribed in 5' x 5'
# Chamfer leg = S * (1 - 1/sqrt(2)) / ( ... wait: side = S / (1 + sqrt(2)) = 2.071068
# Chamfer leg d = side / sqrt(2) = 1.464466
OCT_S = PAD_OCT_SIZE
OCT_SIDE = OCT_S / (1.0 + math.sqrt(2.0))
OCT_D = OCT_SIDE / math.sqrt(2.0)  # ~1.4645 ft

oct_pts = [
    (TOWER_CX - OCT_S/2 + OCT_D, TOWER_CY - OCT_S/2),           # Bottom-left flat
    (TOWER_CX + OCT_S/2 - OCT_D, TOWER_CY - OCT_S/2),           # Bottom-right flat
    (TOWER_CX + OCT_S/2,         TOWER_CY - OCT_S/2 + OCT_D),   # Right-bottom flat
    (TOWER_CX + OCT_S/2,         TOWER_CY + OCT_S/2 - OCT_D),   # Right-top flat
    (TOWER_CX + OCT_S/2 - OCT_D, TOWER_CY + OCT_S/2),           # Top-right flat
    (TOWER_CX - OCT_S/2 + OCT_D, TOWER_CY + OCT_S/2),           # Top-left flat
    (TOWER_CX - OCT_S/2,         TOWER_CY + OCT_S/2 - OCT_D),   # Left-top flat
    (TOWER_CX - OCT_S/2,         TOWER_CY - OCT_S/2 + OCT_D),   # Left-bottom flat
]

# Equipment Concrete Pad
PAD_EQ_XMIN = TOWER_CX + 6.00  # 4.90 + 6.00 = 10.90 ft
PAD_EQ_W = 8.10
PAD_EQ_XMAX = PAD_EQ_XMIN + PAD_EQ_W  # 19.00 ft (20.10 - 19.00 = 1.10 ft from East fence)
PAD_EQ_YMIN = 3.00
PAD_EQ_H = 10.20
PAD_EQ_YMAX = PAD_EQ_YMIN + PAD_EQ_H  # 13.20 ft (20.10 - 13.20 = 6.90 ft from North fence)

# Equipment Cabinets on Pad
# A. Cabinet: 5.3' x 3.15' (Height x Width)
CAB_A_W = 3.15
CAB_A_H = 5.30
# Position A: Leave space on west for AC B (0.8'), center on pad
CAB_A_XMIN = 13.50
CAB_A_XMAX = CAB_A_XMIN + CAB_A_W  # 16.65 ft
CAB_A_YMIN = 6.30
CAB_A_YMAX = CAB_A_YMIN + CAB_A_H  # 11.60 ft

# B. Cabinet AC: 1.9' x 0.8' (Height x Width, attached to West side of A)
CAB_B_W = 0.80
CAB_B_H = 1.90
CAB_B_XMAX = CAB_A_XMIN           # 13.50 ft
CAB_B_XMIN = CAB_B_XMAX - CAB_B_W  # 12.70 ft
CAB_B_YMAX = CAB_A_YMAX - 0.30     # 11.30 ft
CAB_B_YMIN = CAB_B_YMAX - CAB_B_H  # 9.40 ft

# C. Cabinet: 2.2' x 1.6' (Width x Height, below A)
CAB_C_W = 2.20
CAB_C_H = 1.60
CAB_C_XMIN = 13.90
CAB_C_XMAX = CAB_C_XMIN + CAB_C_W  # 16.10 ft
CAB_C_YMIN = 4.00
CAB_C_YMAX = CAB_C_YMIN + CAB_C_H  # 5.60 ft

# D. Power Box: 1.9' x 0.5' (Height x Width/Depth, on West fence rack)
POW_RACK_X = 0.80   # rack centerline offset from West fence
POW_RACK_Y1 = 12.80
POW_RACK_Y2 = 17.50
POW_D_W = 0.50
POW_D_H = 1.90
POW_D_XMIN = POW_RACK_X
POW_D_XMAX = POW_D_XMIN + POW_D_W  # 1.30 ft
POW_D_YMIN = 14.20
POW_D_YMAX = POW_D_YMIN + POW_D_H  # 16.10 ft

# Cable Tray / Ice Bridge
# Connects Tower Northeast foundation shoulder to Equipment Pad East edge
TRAY_W = 1.20  # 14-inch to 18-inch typical telecom ice bridge width
TRAY_P1_TOP = (TOWER_CX + 0.40, TOWER_CY + OCT_S/2)  # (5.30, 6.80)
TRAY_P1_BOT = (TOWER_CX + 0.40, TOWER_CY + OCT_S/2 - TRAY_W)  # (5.30, 5.60)
TRAY_P2_TOP = (PAD_EQ_XMAX, 7.90)  # (19.00, 7.90)
TRAY_P2_BOT = (PAD_EQ_XMAX, 7.90 - TRAY_W)  # (19.00, 6.70)

# GPS Antennas
GPS_1 = (PAD_EQ_XMAX + 0.35, 7.70)
GPS_2 = (PAD_EQ_XMAX + 0.35, 6.90)
GPS_RAD = 0.18

print("Geometric model compiled successfully.")

# -------------------------------------------------------------
# 1. GENERATE DXF WITH EZDXF
# -------------------------------------------------------------
def build_dxf(filename):
    doc = ezdxf.new('R2018', setup=True)
    msp = doc.modelspace()

    # Define standard layers with distinct colors and lineweights
    layers_def = [
        ("C-FENC-BNDY", 4, 50, "CONTINUOUS"),     # Cyan, 0.50mm - Pagar
        ("C-GATE-LEAF", 4, 35, "CONTINUOUS"),     # Cyan, 0.35mm - Gerbang
        ("C-GATE-SWNG", 8, 18, "DASHED"),         # Gray, 0.18mm - Swing arc
        ("S-CONC-PADS", 5, 50, "CONTINUOUS"),     # Blue, 0.50mm - Pondasi & Pad
        ("S-TOWR-BASE", 6, 70, "CONTINUOUS"),     # Magenta, 0.70mm - Monopole
        ("S-TOWR-CLIN", 1, 18, "CENTER"),         # Red, 0.18mm - Centerlines
        ("E-EQPM-CABN", 3, 35, "CONTINUOUS"),     # Green, 0.35mm - Cabinets
        ("E-EQPM-POWR", 3, 35, "CONTINUOUS"),     # Green, 0.35mm - Power Box
        ("E-EQPM-TRAY", 7, 25, "CONTINUOUS"),     # White, 0.25mm - Cable Tray
        ("E-EQPM-ANTN", 3, 35, "CONTINUOUS"),     # Green, 0.35mm - GPS
        ("G-ANNO-DIMS", 1, 18, "CONTINUOUS"),     # Red, 0.18mm - Dimensions
        ("G-ANNO-TEXT", 7, 25, "CONTINUOUS"),     # White, 0.25mm - Text Notes
        ("G-TTLB-BLDR", 7, 50, "CONTINUOUS"),     # White, 0.50mm - Border
    ]

    for name, col, lw, lt in layers_def:
        if name not in doc.layers:
            doc.layers.add(name, color=col, lineweight=lw, linetype=lt)

    # 1. FENCE BOUNDARY
    # South fence: (0,0) to (20.10, 0)
    msp.add_line((0, 0), (COMPOUND_W, 0), dxfattribs={'layer': 'C-FENC-BNDY'})
    # East fence: (20.10, 0) to (20.10, 20.10)
    msp.add_line((COMPOUND_W, 0), (COMPOUND_W, COMPOUND_H), dxfattribs={'layer': 'C-FENC-BNDY'})
    # West fence: (0, 0) to (0, 20.10)
    msp.add_line((0, 0), (0, COMPOUND_H), dxfattribs={'layer': 'C-FENC-BNDY'})
    # North fence (West segment): (0, 20.10) to (4.00, 20.10)
    msp.add_line((0, COMPOUND_H), (GATE_OFFSET_X, COMPOUND_H), dxfattribs={'layer': 'C-FENC-BNDY'})
    # North fence (East segment): (16.12, 20.10) to (20.10, 20.10)
    msp.add_line((GATE_END_X, COMPOUND_H), (COMPOUND_W, COMPOUND_H), dxfattribs={'layer': 'C-FENC-BNDY'})

    # Gate Opening / Threshold (dashed line at boundary)
    msp.add_line((GATE_OFFSET_X, COMPOUND_H), (GATE_END_X, COMPOUND_H), 
                 dxfattribs={'layer': 'C-GATE-SWNG', 'linetype': 'DASHED'})

    # Double Swing Gate Leaves (Angled open outward as in survey sketch)
    # Left leaf: pivots at (4.0, 20.10), length = 6.06 ft, angle ~ 25 deg outward
    gate_leaf_len = GATE_WIDTH / 2.0
    gate_ang_rad = math.radians(25)
    g_left_tip = (GATE_OFFSET_X + gate_leaf_len * math.cos(gate_ang_rad),
                  COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    msp.add_line((GATE_OFFSET_X, COMPOUND_H), g_left_tip, dxfattribs={'layer': 'C-GATE-LEAF'})

    # Right leaf: pivots at (16.12, 20.10), length = 6.06 ft, angle ~ 155 deg outward
    g_right_tip = (GATE_END_X - gate_leaf_len * math.cos(gate_ang_rad),
                   COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    msp.add_line((GATE_END_X, COMPOUND_H), g_right_tip, dxfattribs={'layer': 'C-GATE-LEAF'})

    # Gate post markers
    msp.add_circle((GATE_OFFSET_X, COMPOUND_H), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})
    msp.add_circle((GATE_END_X, COMPOUND_H), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})
    msp.add_circle((0, 0), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})
    msp.add_circle((COMPOUND_W, 0), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})
    msp.add_circle((0, COMPOUND_H), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})
    msp.add_circle((COMPOUND_W, COMPOUND_H), 0.15, dxfattribs={'layer': 'C-FENC-BNDY'})

    # 2. TOWER & OCTAGONAL PAD
    # Add Octagon LWPolyline
    oct_pts_closed = oct_pts + [oct_pts[0]]
    msp.add_lwpolyline(oct_pts_closed, dxfattribs={'layer': 'S-CONC-PADS'})

    # Monopole Base Circle
    msp.add_circle((TOWER_CX, TOWER_CY), TOWER_POLE_DIA/2, dxfattribs={'layer': 'S-TOWR-BASE'})

    # Tower Centerlines
    cl_ext = 4.0
    msp.add_line((TOWER_CX - cl_ext, TOWER_CY), (TOWER_CX + cl_ext, TOWER_CY), 
                 dxfattribs={'layer': 'S-TOWR-CLIN', 'linetype': 'CENTER'})
    msp.add_line((TOWER_CX, TOWER_CY - cl_ext), (TOWER_CX, TOWER_CY + cl_ext), 
                 dxfattribs={'layer': 'S-TOWR-CLIN', 'linetype': 'CENTER'})

    # 3. EQUIPMENT CONCRETE PAD
    pad_eq_corners = [
        (PAD_EQ_XMIN, PAD_EQ_YMIN),
        (PAD_EQ_XMAX, PAD_EQ_YMIN),
        (PAD_EQ_XMAX, PAD_EQ_YMAX),
        (PAD_EQ_XMIN, PAD_EQ_YMAX),
        (PAD_EQ_XMIN, PAD_EQ_YMIN)
    ]
    msp.add_lwpolyline(pad_eq_corners, dxfattribs={'layer': 'S-CONC-PADS'})

    # 4. EQUIPMENT CABINETS
    # Cabinet A
    cab_a_corners = [
        (CAB_A_XMIN, CAB_A_YMIN),
        (CAB_A_XMAX, CAB_A_YMIN),
        (CAB_A_XMAX, CAB_A_YMAX),
        (CAB_A_XMIN, CAB_A_YMAX),
        (CAB_A_XMIN, CAB_A_YMIN)
    ]
    msp.add_lwpolyline(cab_a_corners, dxfattribs={'layer': 'E-EQPM-CABN'})

    # Cabinet B (AC)
    cab_b_corners = [
        (CAB_B_XMIN, CAB_B_YMIN),
        (CAB_B_XMAX, CAB_B_YMIN),
        (CAB_B_XMAX, CAB_B_YMAX),
        (CAB_B_XMIN, CAB_B_YMAX),
        (CAB_B_XMIN, CAB_B_YMIN)
    ]
    msp.add_lwpolyline(cab_b_corners, dxfattribs={'layer': 'E-EQPM-CABN'})

    # Cabinet C
    cab_c_corners = [
        (CAB_C_XMIN, CAB_C_YMIN),
        (CAB_C_XMAX, CAB_C_YMIN),
        (CAB_C_XMAX, CAB_C_YMAX),
        (CAB_C_XMIN, CAB_C_YMAX),
        (CAB_C_XMIN, CAB_C_YMIN)
    ]
    msp.add_lwpolyline(cab_c_corners, dxfattribs={'layer': 'E-EQPM-CABN'})

    # Power Rack & Box D
    msp.add_line((POW_RACK_X, POW_RACK_Y1), (POW_RACK_X, POW_RACK_Y2), dxfattribs={'layer': 'E-EQPM-POWR'})
    msp.add_circle((POW_RACK_X, POW_RACK_Y1), 0.12, dxfattribs={'layer': 'E-EQPM-POWR'})
    msp.add_circle((POW_RACK_X, POW_RACK_Y2), 0.12, dxfattribs={'layer': 'E-EQPM-POWR'})
    pow_d_corners = [
        (POW_D_XMIN, POW_D_YMIN),
        (POW_D_XMAX, POW_D_YMIN),
        (POW_D_XMAX, POW_D_YMAX),
        (POW_D_XMIN, POW_D_YMAX),
        (POW_D_XMIN, POW_D_YMIN)
    ]
    msp.add_lwpolyline(pow_d_corners, dxfattribs={'layer': 'E-EQPM-POWR'})

    # 5. CABLE TRAY / ICE BRIDGE (Rails & Rungs)
    msp.add_line(TRAY_P1_TOP, TRAY_P2_TOP, dxfattribs={'layer': 'E-EQPM-TRAY'})
    msp.add_line(TRAY_P1_BOT, TRAY_P2_BOT, dxfattribs={'layer': 'E-EQPM-TRAY'})
    # Add Rungs
    num_rungs = 18
    for i in range(num_rungs + 1):
        t = i / num_rungs
        rt_x = TRAY_P1_TOP[0] + t * (TRAY_P2_TOP[0] - TRAY_P1_TOP[0])
        rt_y = TRAY_P1_TOP[1] + t * (TRAY_P2_TOP[1] - TRAY_P1_TOP[1])
        rb_x = TRAY_P1_BOT[0] + t * (TRAY_P2_BOT[0] - TRAY_P1_BOT[0])
        rb_y = TRAY_P1_BOT[1] + t * (TRAY_P2_BOT[1] - TRAY_P1_BOT[1])
        msp.add_line((rt_x, rt_y), (rb_x, rb_y), dxfattribs={'layer': 'E-EQPM-TRAY'})

    # 6. GPS ANTENNAS
    msp.add_circle(GPS_1, GPS_RAD, dxfattribs={'layer': 'E-EQPM-ANTN'})
    msp.add_circle(GPS_2, GPS_RAD, dxfattribs={'layer': 'E-EQPM-ANTN'})

    # 7. LABELS & TEXT
    # Equipments A, B, C, D, GPS
    msp.add_text("A", height=0.45, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        ((CAB_A_XMIN + CAB_A_XMAX)/2, (CAB_A_YMIN + CAB_A_YMAX)/2), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("B", height=0.35, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        ((CAB_B_XMIN + CAB_B_XMAX)/2, (CAB_B_YMIN + CAB_B_YMAX)/2), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("C", height=0.35, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        ((CAB_C_XMIN + CAB_C_XMAX)/2, (CAB_C_YMIN + CAB_C_YMAX)/2), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("D", height=0.35, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        (POW_D_XMAX + 0.35, (POW_D_YMIN + POW_D_YMAX)/2), align=TextEntityAlignment.MIDDLE_LEFT)
    msp.add_text("GPS", height=0.25, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        (GPS_1[0] - 0.45, GPS_1[1] + 0.35), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("GPS", height=0.25, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
        (GPS_2[0] - 0.25, GPS_2[1] - 0.35), align=TextEntityAlignment.MIDDLE_CENTER)

    # 8. COMPLETE DIMENSIONS (As drawn on Survey Sheet)
    def add_dim_h(x1, x2, y, text):
        msp.add_line((x1, y), (x2, y), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_line((x1, y - 0.25), (x1, y + 0.25), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_line((x2, y - 0.25), (x2, y + 0.25), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_text(text, height=0.35, dxfattribs={'layer': 'G-ANNO-TEXT'}).set_placement(
            ((x1 + x2)/2, y + 0.20), align=TextEntityAlignment.BOTTOM_CENTER)

    def add_dim_v(x, y1, y2, text):
        msp.add_line((x, y1), (x, y2), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_line((x - 0.25, y1), (x + 0.25, y1), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_line((x - 0.25, y2), (x + 0.25, y2), dxfattribs={'layer': 'G-ANNO-DIMS'})
        msp.add_text(text, height=0.35, dxfattribs={'layer': 'G-ANNO-TEXT', 'rotation': 90}).set_placement(
            (x - 0.20, (y1 + y2)/2), align=TextEntityAlignment.BOTTOM_CENTER)

    # Bottom Dimensions:
    # 4.9' (West to Tower CL)
    add_dim_h(0, TOWER_CX, -1.2, "4.9'")
    # 6' (Tower CL to Pad West edge)
    add_dim_h(TOWER_CX, PAD_EQ_XMIN, -1.2, "6'")
    # 8.1' (Pad Width)
    add_dim_h(PAD_EQ_XMIN, PAD_EQ_XMAX, -1.2, "8.1'")
    # 1.1' (Pad East edge to East fence)
    add_dim_h(PAD_EQ_XMAX, COMPOUND_W, -1.2, "1.1'")
    # Total Bottom: 20.10'
    add_dim_h(0, COMPOUND_W, -2.4, "20.10'")

    # Left Dimensions:
    # 4.3' (South to Tower CL)
    add_dim_v(-1.2, 0, TOWER_CY, "4.3'")
    # 15.8' (Tower CL to North fence)
    add_dim_v(-1.2, TOWER_CY, COMPOUND_H, "15.8'")
    # Total Left: 20.10'
    add_dim_v(-2.4, 0, COMPOUND_H, "20.10'")

    # Right Dimensions:
    # 3' (South to Pad South edge)
    add_dim_v(COMPOUND_W + 1.2, 0, PAD_EQ_YMIN, "3'")
    # 10.2' (Pad Height)
    add_dim_v(COMPOUND_W + 1.2, PAD_EQ_YMIN, PAD_EQ_YMAX, "10.2'")
    # 6.9' (Pad North edge to North fence)
    add_dim_v(COMPOUND_W + 1.2, PAD_EQ_YMAX, COMPOUND_H, "6.9'")
    # Total Right: 20.10'
    add_dim_v(COMPOUND_W + 2.4, 0, COMPOUND_H, "20.10'")

    # Top Dimensions:
    # 4' (West to Gate)
    add_dim_h(0, GATE_OFFSET_X, COMPOUND_H + 3.2, "4'")
    # 12.12' (Gate Opening)
    add_dim_h(GATE_OFFSET_X, GATE_END_X, COMPOUND_H + 3.2, "12.12'")
    # 3.98' (Gate to East fence)
    add_dim_h(GATE_END_X, COMPOUND_W, COMPOUND_H + 3.2, "3.98'")

    # Tower Octagon dimensions: 5' x 5'
    add_dim_h(TOWER_CX - OCT_S/2, TOWER_CX + OCT_S/2, TOWER_CY + OCT_S/2 + 0.8, "5'")
    add_dim_v(TOWER_CX + OCT_S/2 + 0.8, TOWER_CY - OCT_S/2, TOWER_CY + OCT_S/2, "5'")

    # Save DXF
    doc.saveas(filename)
    print(f"DXF saved to: {filename}")


# -------------------------------------------------------------
# 2. GENERATE HIGH-RES CAD DRAWING (PNG)
# -------------------------------------------------------------
def render_cad_png(filename):
    fig, ax = plt.subplots(figsize=(14, 16), dpi=300)
    fig.patch.set_facecolor('#0f141d')  # Modern dark engineering CAD theme
    ax.set_facecolor('#131a26')

    # Grid & Axes
    ax.set_xlim(-6.5, 27.5)
    ax.set_ylim(-6.5, 29.5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', color='#263248', alpha=0.6, linewidth=0.7)

    # 1. Compound Fence
    fence_box = patches.Rectangle((0, 0), COMPOUND_W, COMPOUND_H, 
                                  fill=False, edgecolor='#00e5ff', linewidth=2.4, zorder=3)
    ax.add_patch(fence_box)

    # Gate Opening on North
    gate_clear = patches.Rectangle((GATE_OFFSET_X, COMPOUND_H - 0.1), GATE_WIDTH, 0.2, 
                                   facecolor='#131a26', edgecolor='none', zorder=4)
    ax.add_patch(gate_clear)

    # Gate threshold dashed line
    ax.plot([GATE_OFFSET_X, GATE_END_X], [COMPOUND_H, COMPOUND_H], 
            color='#5c7080', linestyle='--', linewidth=1.5, zorder=5)

    # Open Gate Leaves
    gate_leaf_len = GATE_WIDTH / 2.0
    gate_ang_rad = math.radians(25)
    g_left_tip = (GATE_OFFSET_X + gate_leaf_len * math.cos(gate_ang_rad),
                  COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    g_right_tip = (GATE_END_X - gate_leaf_len * math.cos(gate_ang_rad),
                   COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    ax.plot([GATE_OFFSET_X, g_left_tip[0]], [COMPOUND_H, g_left_tip[1]], 
            color='#00e5ff', linewidth=2.2, zorder=6)
    ax.plot([GATE_END_X, g_right_tip[0]], [COMPOUND_H, g_right_tip[1]], 
            color='#00e5ff', linewidth=2.2, zorder=6)

    # Gate swing arcs
    arc_left = patches.Arc((GATE_OFFSET_X, COMPOUND_H), gate_leaf_len*2, gate_leaf_len*2, 
                           angle=0, theta1=0, theta2=25, color='#3a4d6b', linestyle=':', linewidth=1.2)
    arc_right = patches.Arc((GATE_END_X, COMPOUND_H), gate_leaf_len*2, gate_leaf_len*2, 
                            angle=0, theta1=155, theta2=180, color='#3a4d6b', linestyle=':', linewidth=1.2)
    ax.add_patch(arc_left)
    ax.add_patch(arc_right)

    # Corner Posts
    for px, py in [(0,0), (COMPOUND_W,0), (0,COMPOUND_H), (COMPOUND_W,COMPOUND_H), 
                   (GATE_OFFSET_X, COMPOUND_H), (GATE_END_X, COMPOUND_H)]:
        ax.plot(px, py, marker='s', markersize=6, color='#00e5ff', zorder=7)

    # 2. Tower Foundation (Octagon)
    oct_poly = patches.Polygon(oct_pts, closed=True, 
                               facecolor='#1e2c45', edgecolor='#4182e4', linewidth=2.2, hatch='///', zorder=3)
    ax.add_patch(oct_poly)

    # Monopole Pole Circle
    pole_circ = patches.Circle((TOWER_CX, TOWER_CY), TOWER_POLE_DIA/2, 
                               facecolor='#49275a', edgecolor='#d946ef', linewidth=2.5, zorder=5)
    ax.add_patch(pole_circ)

    # Tower Centerlines
    ax.axhline(TOWER_CY, xmin=0.18, xmax=0.45, color='#ef4444', linestyle='-.', linewidth=1.1, alpha=0.8)
    ax.axvline(TOWER_CX, ymin=0.18, ymax=0.45, color='#ef4444', linestyle='-.', linewidth=1.1, alpha=0.8)

    # Centerline projection to dimensions
    ax.plot([TOWER_CX, TOWER_CX], [0, -1.2], color='#ef4444', linestyle=':', linewidth=1.0)
    ax.plot([0, -1.2], [TOWER_CY, TOWER_CY], color='#ef4444', linestyle=':', linewidth=1.0)

    # 3. Equipment Concrete Pad
    eq_pad = patches.Rectangle((PAD_EQ_XMIN, PAD_EQ_YMIN), PAD_EQ_W, PAD_EQ_H, 
                               facecolor='#1e2c45', edgecolor='#4182e4', linewidth=2.2, hatch='...', zorder=2)
    ax.add_patch(eq_pad)

    # Pad dimension projections
    ax.plot([PAD_EQ_XMIN, PAD_EQ_XMIN], [PAD_EQ_YMIN, -1.2], color='#4182e4', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, PAD_EQ_XMAX], [PAD_EQ_YMIN, -1.2], color='#4182e4', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, COMPOUND_W + 1.2], [PAD_EQ_YMIN, PAD_EQ_YMIN], color='#4182e4', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, COMPOUND_W + 1.2], [PAD_EQ_YMAX, PAD_EQ_YMAX], color='#4182e4', linestyle=':', linewidth=0.8)

    # 4. Equipment on Pad
    # Cabinet A
    cab_a = patches.Rectangle((CAB_A_XMIN, CAB_A_YMIN), CAB_A_W, CAB_A_H, 
                              facecolor='#133827', edgecolor='#10b981', linewidth=2.0, zorder=6)
    ax.add_patch(cab_a)
    ax.text((CAB_A_XMIN + CAB_A_XMAX)/2, (CAB_A_YMIN + CAB_A_YMAX)/2, "A", 
            color='#f87171', fontsize=14, fontweight='bold', ha='center', va='center', zorder=8)

    # Cabinet AC B
    cab_b = patches.Rectangle((CAB_B_XMIN, CAB_B_YMIN), CAB_B_W, CAB_B_H, 
                              facecolor='#133827', edgecolor='#10b981', linewidth=1.8, zorder=6)
    ax.add_patch(cab_b)
    ax.text((CAB_B_XMIN + CAB_B_XMAX)/2, (CAB_B_YMIN + CAB_B_YMAX)/2, "B", 
            color='#f87171', fontsize=11, fontweight='bold', ha='center', va='center', zorder=8)

    # Cabinet C
    cab_c = patches.Rectangle((CAB_C_XMIN, CAB_C_YMIN), CAB_C_W, CAB_C_H, 
                              facecolor='#133827', edgecolor='#10b981', linewidth=1.8, zorder=6)
    ax.add_patch(cab_c)
    ax.text((CAB_C_XMIN + CAB_C_XMAX)/2, (CAB_C_YMIN + CAB_C_YMAX)/2, "C", 
            color='#f87171', fontsize=12, fontweight='bold', ha='center', va='center', zorder=8)

    # Power Rack & Box D
    ax.plot([POW_RACK_X, POW_RACK_X], [POW_RACK_Y1, POW_RACK_Y2], color='#00e5ff', linewidth=1.6, zorder=5)
    ax.plot(POW_RACK_X, POW_RACK_Y1, marker='o', markersize=4, color='#00e5ff', zorder=6)
    ax.plot(POW_RACK_X, POW_RACK_Y2, marker='o', markersize=4, color='#00e5ff', zorder=6)
    pow_d = patches.Rectangle((POW_D_XMIN, POW_D_YMIN), POW_D_W, POW_D_H, 
                              facecolor='#133827', edgecolor='#10b981', linewidth=1.8, zorder=6)
    ax.add_patch(pow_d)
    ax.text(POW_D_XMAX + 0.35, (POW_D_YMIN + POW_D_YMAX)/2, "D", 
            color='#f87171', fontsize=13, fontweight='bold', ha='left', va='center', zorder=8)

    # 5. Cable Tray / Ice Bridge
    ax.plot([TRAY_P1_TOP[0], TRAY_P2_TOP[0]], [TRAY_P1_TOP[1], TRAY_P2_TOP[1]], 
            color='#e2e8f0', linewidth=2.0, zorder=7)
    ax.plot([TRAY_P1_BOT[0], TRAY_P2_BOT[0]], [TRAY_P1_BOT[1], TRAY_P2_BOT[1]], 
            color='#e2e8f0', linewidth=2.0, zorder=7)
    # Rungs
    num_rungs = 18
    for i in range(num_rungs + 1):
        t = i / num_rungs
        rt_x = TRAY_P1_TOP[0] + t * (TRAY_P2_TOP[0] - TRAY_P1_TOP[0])
        rt_y = TRAY_P1_TOP[1] + t * (TRAY_P2_TOP[1] - TRAY_P1_TOP[1])
        rb_x = TRAY_P1_BOT[0] + t * (TRAY_P2_BOT[0] - TRAY_P1_BOT[0])
        rb_y = TRAY_P1_BOT[1] + t * (TRAY_P2_BOT[1] - TRAY_P1_BOT[1])
        ax.plot([rt_x, rb_x], [rt_y, rb_y], color='#cbd5e1', linewidth=1.2, zorder=7)

    # 6. GPS Antennas
    for gps_pt in [GPS_1, GPS_2]:
        circ = patches.Circle(gps_pt, GPS_RAD, facecolor='#10b981', edgecolor='#34d399', linewidth=1.5, zorder=8)
        ax.add_patch(circ)
    ax.text(GPS_1[0] + 0.45, GPS_1[1] + 0.15, "GPS", color='#10b981', fontsize=10, fontweight='bold', ha='left', va='center')
    ax.text(GPS_2[0] + 0.45, GPS_2[1] - 0.15, "GPS", color='#10b981', fontsize=10, fontweight='bold', ha='left', va='center')

    # 7. DIMENSIONS WITH ARROWS
    def draw_dim_line_h(x1, x2, y, text, offset_text=0.35, color='#38bdf8'):
        ax.annotate('', xy=(x1, y), xytext=(x2, y),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2, shrinkA=0, shrinkB=0))
        ax.plot([x1, x1], [y - 0.25, y + 0.25], color=color, lw=1.2)
        ax.plot([x2, x2], [y - 0.25, y + 0.25], color=color, lw=1.2)
        ax.text((x1 + x2)/2, y + offset_text, text, color=color, fontsize=11, fontweight='bold',
                ha='center', va='bottom', bbox=dict(facecolor='#0f141d', edgecolor='none', pad=1.5))

    def draw_dim_line_v(x, y1, y2, text, offset_text=0.35, color='#38bdf8'):
        ax.annotate('', xy=(x, y1), xytext=(x, y2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2, shrinkA=0, shrinkB=0))
        ax.plot([x - 0.25, x + 0.25], [y1, y1], color=color, lw=1.2)
        ax.plot([x - 0.25, x + 0.25], [y2, y2], color=color, lw=1.2)
        ax.text(x - offset_text, (y1 + y2)/2, text, color=color, fontsize=11, fontweight='bold',
                ha='right', va='center', rotation=90, bbox=dict(facecolor='#0f141d', edgecolor='none', pad=1.5))

    # Bottom Dimensions:
    draw_dim_line_h(0, TOWER_CX, -1.2, "4.9'")
    draw_dim_line_h(TOWER_CX, PAD_EQ_XMIN, -1.2, "6'")
    draw_dim_line_h(PAD_EQ_XMIN, PAD_EQ_XMAX, -1.2, "8.1'")
    draw_dim_line_h(PAD_EQ_XMAX, COMPOUND_W, -1.2, "1.1'")
    draw_dim_line_h(0, COMPOUND_W, -2.6, "20.10'", color='#facc15')

    # Left Dimensions:
    draw_dim_line_v(-1.2, 0, TOWER_CY, "4.3'")
    draw_dim_line_v(-1.2, TOWER_CY, COMPOUND_H, "15.8'")
    draw_dim_line_v(-2.6, 0, COMPOUND_H, "20.10'", color='#facc15')

    # Right Dimensions:
    draw_dim_line_v(COMPOUND_W + 1.2, 0, PAD_EQ_YMIN, "3'")
    draw_dim_line_v(COMPOUND_W + 1.2, PAD_EQ_YMIN, PAD_EQ_YMAX, "10.2'")
    draw_dim_line_v(COMPOUND_W + 1.2, PAD_EQ_YMAX, COMPOUND_H, "6.9'")
    draw_dim_line_v(COMPOUND_W + 2.6, 0, COMPOUND_H, "20.10'", color='#facc15')

    # Top Dimensions:
    draw_dim_line_h(0, GATE_OFFSET_X, COMPOUND_H + 3.2, "4'")
    draw_dim_line_h(GATE_OFFSET_X, GATE_END_X, COMPOUND_H + 3.2, "12.12'")
    draw_dim_line_h(GATE_END_X, COMPOUND_W, COMPOUND_H + 3.2, "3.98'")

    # Tower Octagon 5' x 5' Dimensions
    draw_dim_line_h(TOWER_CX - OCT_S/2, TOWER_CX + OCT_S/2, TOWER_CY + OCT_S/2 + 0.8, "5'", color='#ef4444')
    draw_dim_line_v(TOWER_CX + OCT_S/2 + 0.8, TOWER_CY - OCT_S/2, TOWER_CY + OCT_S/2, "5'", color='#ef4444')

    # 8. NORTH ARROW
    na_x, na_y = 21.0, 25.0
    ax.annotate('', xy=(na_x, na_y + 2.8), xytext=(na_x, na_y),
                arrowprops=dict(facecolor='#10b981', edgecolor='#ffffff', width=2.5, headwidth=9, headlength=11))
    ax.text(na_x, na_y + 3.2, "N", color='#ef4444', fontsize=18, fontweight='bold', ha='center', va='bottom')

    # 9. TITLE & HEADER
    ax.text(COMPOUND_W/2, COMPOUND_H + 5.2, "US1051671_ Blue Diamond", 
            color='#ef4444', fontsize=18, fontweight='bold', ha='center', va='center')
    ax.text(COMPOUND_W/2, COMPOUND_H + 4.2, "COMPOUND & EQUIPMENT LAYOUT PLAN", 
            color='#94a3b8', fontsize=12, fontweight='bold', ha='center', va='center')

    # 10. EQUIPMENT SCHEDULE / LEGEND TABLE (Bottom-Left)
    table_x, table_y = -5.0, -5.2
    schedule_text = (
        "EQUIPMENT SCHEDULE / NOTES:\n"
        "  A.  Cabinet       :  5.3' X 3.15'\n"
        "  B.  Cabinet AC    :  1.9' X 0.8'\n"
        "  C.  Cabinet       :  2.2' X 1.6'\n"
        "  D.  Power Box     :  1.9' X 0.5'\n"
        "  -   GPS Antennas  :  2 Units on East Edge\n"
        "  -   Ice Bridge    :  Connecting Tower to Pad\n"
        "  -   Compound Gate :  12.12' Double Swing Gate"
    )
    ax.text(table_x, table_y, schedule_text, color='#f87171', fontsize=10, fontfamily='monospace',
            va='top', ha='left', bbox=dict(boxstyle='square,pad=0.8', facecolor='#162032', edgecolor='#ef4444', alpha=0.9))

    # Scale and metadata box (Bottom-Right)
    meta_text = (
        "SITE ID: US1051671\n"
        "SITE NAME: Blue Diamond\n"
        "DRAWING: COMPOUND LAYOUT\n"
        "UNITS: US Survey Feet (')\n"
        "SCALE: 1\" = 2'-0\" (approx)\n"
        "SOURCE: Field Survey Sketch"
    )
    ax.text(COMPOUND_W + 3.5, table_y, meta_text, color='#94a3b8', fontsize=9.5, fontfamily='monospace',
            va='top', ha='right', bbox=dict(boxstyle='square,pad=0.8', facecolor='#162032', edgecolor='#3b82f6', alpha=0.9))

    # Turn off default axis box ticks for clean presentation
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#263248')

    plt.tight_layout()
    plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300)
    plt.close()
    print(f"CAD PNG rendered to: {filename}")


def render_plot_png(filename):
    fig, ax = plt.subplots(figsize=(14, 16), dpi=300)
    fig.patch.set_facecolor('#ffffff')  # White engineering paper
    ax.set_facecolor('#ffffff')

    ax.set_xlim(-6.5, 27.5)
    ax.set_ylim(-6.5, 29.5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', color='#e2e8f0', alpha=0.8, linewidth=0.7)

    # 1. Compound Fence
    fence_box = patches.Rectangle((0, 0), COMPOUND_W, COMPOUND_H, 
                                  fill=False, edgecolor='#000000', linewidth=2.4, zorder=3)
    ax.add_patch(fence_box)

    # Gate Opening on North
    gate_clear = patches.Rectangle((GATE_OFFSET_X, COMPOUND_H - 0.1), GATE_WIDTH, 0.2, 
                                   facecolor='#ffffff', edgecolor='none', zorder=4)
    ax.add_patch(gate_clear)

    # Gate threshold dashed line
    ax.plot([GATE_OFFSET_X, GATE_END_X], [COMPOUND_H, COMPOUND_H], 
            color='#64748b', linestyle='--', linewidth=1.5, zorder=5)

    # Open Gate Leaves
    gate_leaf_len = GATE_WIDTH / 2.0
    gate_ang_rad = math.radians(25)
    g_left_tip = (GATE_OFFSET_X + gate_leaf_len * math.cos(gate_ang_rad),
                  COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    g_right_tip = (GATE_END_X - gate_leaf_len * math.cos(gate_ang_rad),
                   COMPOUND_H + gate_leaf_len * math.sin(gate_ang_rad))
    ax.plot([GATE_OFFSET_X, g_left_tip[0]], [COMPOUND_H, g_left_tip[1]], 
            color='#000000', linewidth=2.2, zorder=6)
    ax.plot([GATE_END_X, g_right_tip[0]], [COMPOUND_H, g_right_tip[1]], 
            color='#000000', linewidth=2.2, zorder=6)

    # Gate swing arcs
    arc_left = patches.Arc((GATE_OFFSET_X, COMPOUND_H), gate_leaf_len*2, gate_leaf_len*2, 
                           angle=0, theta1=0, theta2=25, color='#94a3b8', linestyle=':', linewidth=1.2)
    arc_right = patches.Arc((GATE_END_X, COMPOUND_H), gate_leaf_len*2, gate_leaf_len*2, 
                            angle=0, theta1=155, theta2=180, color='#94a3b8', linestyle=':', linewidth=1.2)
    ax.add_patch(arc_left)
    ax.add_patch(arc_right)

    # Corner Posts
    for px, py in [(0,0), (COMPOUND_W,0), (0,COMPOUND_H), (COMPOUND_W,COMPOUND_H), 
                   (GATE_OFFSET_X, COMPOUND_H), (GATE_END_X, COMPOUND_H)]:
        ax.plot(px, py, marker='s', markersize=6, color='#000000', zorder=7)

    # 2. Tower Foundation (Octagon)
    oct_poly = patches.Polygon(oct_pts, closed=True, 
                               facecolor='#f1f5f9', edgecolor='#1e3a8a', linewidth=2.2, hatch='///', zorder=3)
    ax.add_patch(oct_poly)

    # Monopole Pole Circle
    pole_circ = patches.Circle((TOWER_CX, TOWER_CY), TOWER_POLE_DIA/2, 
                               facecolor='#e2e8f0', edgecolor='#7e22ce', linewidth=2.5, zorder=5)
    ax.add_patch(pole_circ)

    # Tower Centerlines
    ax.axhline(TOWER_CY, xmin=0.18, xmax=0.45, color='#dc2626', linestyle='-.', linewidth=1.1, alpha=0.8)
    ax.axvline(TOWER_CX, ymin=0.18, ymax=0.45, color='#dc2626', linestyle='-.', linewidth=1.1, alpha=0.8)

    ax.plot([TOWER_CX, TOWER_CX], [0, -1.2], color='#dc2626', linestyle=':', linewidth=1.0)
    ax.plot([0, -1.2], [TOWER_CY, TOWER_CY], color='#dc2626', linestyle=':', linewidth=1.0)

    # 3. Equipment Concrete Pad
    eq_pad = patches.Rectangle((PAD_EQ_XMIN, PAD_EQ_YMIN), PAD_EQ_W, PAD_EQ_H, 
                               facecolor='#f1f5f9', edgecolor='#1e3a8a', linewidth=2.2, hatch='...', zorder=2)
    ax.add_patch(eq_pad)

    # Pad dimension projections
    ax.plot([PAD_EQ_XMIN, PAD_EQ_XMIN], [PAD_EQ_YMIN, -1.2], color='#64748b', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, PAD_EQ_XMAX], [PAD_EQ_YMIN, -1.2], color='#64748b', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, COMPOUND_W + 1.2], [PAD_EQ_YMIN, PAD_EQ_YMIN], color='#64748b', linestyle=':', linewidth=0.8)
    ax.plot([PAD_EQ_XMAX, COMPOUND_W + 1.2], [PAD_EQ_YMAX, PAD_EQ_YMAX], color='#64748b', linestyle=':', linewidth=0.8)

    # 4. Equipment on Pad
    # Cabinet A
    cab_a = patches.Rectangle((CAB_A_XMIN, CAB_A_YMIN), CAB_A_W, CAB_A_H, 
                              facecolor='#ecfdf5', edgecolor='#047857', linewidth=2.0, zorder=6)
    ax.add_patch(cab_a)
    ax.text((CAB_A_XMIN + CAB_A_XMAX)/2, (CAB_A_YMIN + CAB_A_YMAX)/2, "A", 
            color='#b91c1c', fontsize=14, fontweight='bold', ha='center', va='center', zorder=8)

    # Cabinet AC B
    cab_b = patches.Rectangle((CAB_B_XMIN, CAB_B_YMIN), CAB_B_W, CAB_B_H, 
                              facecolor='#ecfdf5', edgecolor='#047857', linewidth=1.8, zorder=6)
    ax.add_patch(cab_b)
    ax.text((CAB_B_XMIN + CAB_B_XMAX)/2, (CAB_B_YMIN + CAB_B_YMAX)/2, "B", 
            color='#b91c1c', fontsize=11, fontweight='bold', ha='center', va='center', zorder=8)

    # Cabinet C
    cab_c = patches.Rectangle((CAB_C_XMIN, CAB_C_YMIN), CAB_C_W, CAB_C_H, 
                              facecolor='#ecfdf5', edgecolor='#047857', linewidth=1.8, zorder=6)
    ax.add_patch(cab_c)
    ax.text((CAB_C_XMIN + CAB_C_XMAX)/2, (CAB_C_YMIN + CAB_C_YMAX)/2, "C", 
            color='#b91c1c', fontsize=12, fontweight='bold', ha='center', va='center', zorder=8)

    # Power Rack & Box D
    ax.plot([POW_RACK_X, POW_RACK_X], [POW_RACK_Y1, POW_RACK_Y2], color='#000000', linewidth=1.6, zorder=5)
    ax.plot(POW_RACK_X, POW_RACK_Y1, marker='o', markersize=4, color='#000000', zorder=6)
    ax.plot(POW_RACK_X, POW_RACK_Y2, marker='o', markersize=4, color='#000000', zorder=6)
    pow_d = patches.Rectangle((POW_D_XMIN, POW_D_YMIN), POW_D_W, POW_D_H, 
                              facecolor='#ecfdf5', edgecolor='#047857', linewidth=1.8, zorder=6)
    ax.add_patch(pow_d)
    ax.text(POW_D_XMAX + 0.35, (POW_D_YMIN + POW_D_YMAX)/2, "D", 
            color='#b91c1c', fontsize=13, fontweight='bold', ha='left', va='center', zorder=8)

    # 5. Cable Tray / Ice Bridge
    ax.plot([TRAY_P1_TOP[0], TRAY_P2_TOP[0]], [TRAY_P1_TOP[1], TRAY_P2_TOP[1]], 
            color='#1e293b', linewidth=2.0, zorder=7)
    ax.plot([TRAY_P1_BOT[0], TRAY_P2_BOT[0]], [TRAY_P1_BOT[1], TRAY_P2_BOT[1]], 
            color='#1e293b', linewidth=2.0, zorder=7)
    for i in range(18 + 1):
        t = i / 18.0
        rt_x = TRAY_P1_TOP[0] + t * (TRAY_P2_TOP[0] - TRAY_P1_TOP[0])
        rt_y = TRAY_P1_TOP[1] + t * (TRAY_P2_TOP[1] - TRAY_P1_TOP[1])
        rb_x = TRAY_P1_BOT[0] + t * (TRAY_P2_BOT[0] - TRAY_P1_BOT[0])
        rb_y = TRAY_P1_BOT[1] + t * (TRAY_P2_BOT[1] - TRAY_P1_BOT[1])
        ax.plot([rt_x, rb_x], [rt_y, rb_y], color='#475569', linewidth=1.2, zorder=7)

    # 6. GPS Antennas
    for gps_pt in [GPS_1, GPS_2]:
        circ = patches.Circle(gps_pt, GPS_RAD, facecolor='#047857', edgecolor='#065f46', linewidth=1.5, zorder=8)
        ax.add_patch(circ)
    ax.text(GPS_1[0] + 0.45, GPS_1[1] + 0.15, "GPS", color='#047857', fontsize=10, fontweight='bold', ha='left', va='center')
    ax.text(GPS_2[0] + 0.45, GPS_2[1] - 0.15, "GPS", color='#047857', fontsize=10, fontweight='bold', ha='left', va='center')

    # 7. Dimensions
    def draw_plot_dim_h(x1, x2, y, text, offset_text=0.35, color='#0284c7'):
        ax.annotate('', xy=(x1, y), xytext=(x2, y),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2, shrinkA=0, shrinkB=0))
        ax.plot([x1, x1], [y - 0.25, y + 0.25], color=color, lw=1.2)
        ax.plot([x2, x2], [y - 0.25, y + 0.25], color=color, lw=1.2)
        ax.text((x1 + x2)/2, y + offset_text, text, color=color, fontsize=11, fontweight='bold',
                ha='center', va='bottom', bbox=dict(facecolor='#ffffff', edgecolor='none', pad=1.5))

    def draw_plot_dim_v(x, y1, y2, text, offset_text=0.35, color='#0284c7'):
        ax.annotate('', xy=(x, y1), xytext=(x, y2),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=1.2, shrinkA=0, shrinkB=0))
        ax.plot([x - 0.25, x + 0.25], [y1, y1], color=color, lw=1.2)
        ax.plot([x - 0.25, x + 0.25], [y2, y2], color=color, lw=1.2)
        ax.text(x - offset_text, (y1 + y2)/2, text, color=color, fontsize=11, fontweight='bold',
                ha='right', va='center', rotation=90, bbox=dict(facecolor='#ffffff', edgecolor='none', pad=1.5))

    # Bottom
    draw_plot_dim_h(0, TOWER_CX, -1.2, "4.9'")
    draw_plot_dim_h(TOWER_CX, PAD_EQ_XMIN, -1.2, "6'")
    draw_plot_dim_h(PAD_EQ_XMIN, PAD_EQ_XMAX, -1.2, "8.1'")
    draw_plot_dim_h(PAD_EQ_XMAX, COMPOUND_W, -1.2, "1.1'")
    draw_plot_dim_h(0, COMPOUND_W, -2.6, "20.10'", color='#b45309')

    # Left
    draw_plot_dim_v(-1.2, 0, TOWER_CY, "4.3'")
    draw_plot_dim_v(-1.2, TOWER_CY, COMPOUND_H, "15.8'")
    draw_plot_dim_v(-2.6, 0, COMPOUND_H, "20.10'", color='#b45309')

    # Right
    draw_plot_dim_v(COMPOUND_W + 1.2, 0, PAD_EQ_YMIN, "3'")
    draw_plot_dim_v(COMPOUND_W + 1.2, PAD_EQ_YMIN, PAD_EQ_YMAX, "10.2'")
    draw_plot_dim_v(COMPOUND_W + 1.2, PAD_EQ_YMAX, COMPOUND_H, "6.9'")
    draw_plot_dim_v(COMPOUND_W + 2.6, 0, COMPOUND_H, "20.10'", color='#b45309')

    # Top
    draw_plot_dim_h(0, GATE_OFFSET_X, COMPOUND_H + 3.2, "4'")
    draw_plot_dim_h(GATE_OFFSET_X, GATE_END_X, COMPOUND_H + 3.2, "12.12'")
    draw_plot_dim_h(GATE_END_X, COMPOUND_W, COMPOUND_H + 3.2, "3.98'")

    # Tower 5' x 5'
    draw_plot_dim_h(TOWER_CX - OCT_S/2, TOWER_CX + OCT_S/2, TOWER_CY + OCT_S/2 + 0.8, "5'", color='#dc2626')
    draw_plot_dim_v(TOWER_CX + OCT_S/2 + 0.8, TOWER_CY - OCT_S/2, TOWER_CY + OCT_S/2, "5'", color='#dc2626')

    # North Arrow
    na_x, na_y = 21.0, 25.0
    ax.annotate('', xy=(na_x, na_y + 2.8), xytext=(na_x, na_y),
                arrowprops=dict(facecolor='#047857', edgecolor='#000000', width=2.5, headwidth=9, headlength=11))
    ax.text(na_x, na_y + 3.2, "N", color='#dc2626', fontsize=18, fontweight='bold', ha='center', va='bottom')

    # Title
    ax.text(COMPOUND_W/2, COMPOUND_H + 5.2, "US1051671_ Blue Diamond", 
            color='#b91c1c', fontsize=18, fontweight='bold', ha='center', va='center')
    ax.text(COMPOUND_W/2, COMPOUND_H + 4.2, "COMPOUND & EQUIPMENT LAYOUT PLAN", 
            color='#475569', fontsize=12, fontweight='bold', ha='center', va='center')

    # Legend / Schedule
    table_x, table_y = -5.0, -5.2
    schedule_text = (
        "EQUIPMENT SCHEDULE / NOTES:\n"
        "  A.  Cabinet       :  5.3' X 3.15'\n"
        "  B.  Cabinet AC    :  1.9' X 0.8'\n"
        "  C.  Cabinet       :  2.2' X 1.6'\n"
        "  D.  Power Box     :  1.9' X 0.5'\n"
        "  -   GPS Antennas  :  2 Units on East Edge\n"
        "  -   Ice Bridge    :  Connecting Tower to Pad\n"
        "  -   Compound Gate :  12.12' Double Swing Gate"
    )
    ax.text(table_x, table_y, schedule_text, color='#991b1b', fontsize=10, fontfamily='monospace',
            va='top', ha='left', bbox=dict(boxstyle='square,pad=0.8', facecolor='#f8fafc', edgecolor='#dc2626', alpha=0.9))

    meta_text = (
        "SITE ID: US1051671\n"
        "SITE NAME: Blue Diamond\n"
        "DRAWING: COMPOUND LAYOUT\n"
        "UNITS: US Survey Feet (')\n"
        "SCALE: 1\" = 2'-0\" (approx)\n"
        "SOURCE: Field Survey Sketch"
    )
    ax.text(COMPOUND_W + 3.5, table_y, meta_text, color='#334155', fontsize=9.5, fontfamily='monospace',
            va='top', ha='right', bbox=dict(boxstyle='square,pad=0.8', facecolor='#f8fafc', edgecolor='#0284c7', alpha=0.9))

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')

    plt.tight_layout()
    plt.savefig(filename, facecolor='#ffffff', edgecolor='none', dpi=300)
    plt.close()
    print(f"CAD Plot PNG rendered to: {filename}")


# -------------------------------------------------------------
# 3. GENERATE SIDE-BY-SIDE COMPARISON
# -------------------------------------------------------------
def render_comparison(sketch_path, cad_path, comp_path):
    if not os.path.exists(sketch_path) or not os.path.exists(cad_path):
        print("Comparison skipped: missing files.")
        return

    im_sketch = Image.open(sketch_path)
    im_cad = Image.open(cad_path)

    target_h = 1600
    w_sketch = int(im_sketch.width * (target_h / im_sketch.height))
    im_sketch_resized = im_sketch.resize((w_sketch, target_h), Image.Resampling.LANCZOS)

    w_cad = int(im_cad.width * (target_h / im_cad.height))
    im_cad_resized = im_cad.resize((w_cad, target_h), Image.Resampling.LANCZOS)

    total_w = w_sketch + w_cad + 40
    comp_img = Image.new('RGB', (total_w, target_h + 100), color=(15, 20, 29))

    comp_img.paste(im_sketch_resized, (15, 80))
    comp_img.paste(im_cad_resized, (w_sketch + 25, 80))

    fig, ax = plt.subplots(figsize=(total_w/100, (target_h+100)/100), dpi=100)
    ax.imshow(comp_img)
    ax.axis('off')

    ax.text(w_sketch/2 + 15, 45, "ORIGINAL FIELD SURVEY SKETCH", color='#f87171', 
            fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(w_sketch + 25 + w_cad/2, 45, "CONVERTED PRECISION 2D CAD DRAWING", color='#38bdf8', 
            fontsize=16, fontweight='bold', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(comp_path, dpi=100, facecolor='#0f141d')
    plt.close()
    print(f"Comparison image saved to: {comp_path}")


if __name__ == "__main__":
    print("Executing CAD Generation Pipeline...")
    build_dxf(DXF_PATH)
    render_cad_png(PNG_PATH)
    render_plot_png(PLOT_PATH)
    render_comparison(SURVEY_SKETCH_PATH, PNG_PATH, COMPARISON_PATH)
    print("Pipeline completed successfully!")

