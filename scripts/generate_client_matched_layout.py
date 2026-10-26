r"""
Client-Grade Precision Telecom CAD & Drawing Generator
Site: US1051671_Blue Diamond
Style: Exact match to Everest / Visual Intelligence / Uirtus client-accepted standards
(Ref: media_1791978201395_38bb1ca7.png & forest_lakes_p2.png)
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

OUTPUT_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\RAW\Layout"
RAW_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051534\Raw"
EVEREST_LOGO_PATH = os.path.join(RAW_DIR, "Everest Logo.jpeg")
VI_LOGO_PATH = os.path.join(RAW_DIR, "VI Logo.jpg")

DXF_OUT = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout.dxf")
CLIENT_STYLE_PNG = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout_ClientStyle.png")
FULL_SHEET_PNG = os.path.join(OUTPUT_DIR, "US1051671_Blue_Diamond_Compound_Layout_Sheet.png")

# -------------------------------------------------------------
# FIELD SURVEY METRIC TO FEET/INCHES CONVERSION
# Survey recorded values in Decimal Feet:
# Compound: 20.10' x 20.10'
# -------------------------------------------------------------
COMPOUND_W = 20.10
COMPOUND_H = 20.10

# Gate on North fence
GATE_X1 = 4.00
GATE_W = 12.12
GATE_X2 = GATE_X1 + GATE_W  # 16.12
GATE_EAST = COMPOUND_W - GATE_X2  # 3.98

# Tower & Foundation
TOWER_CX = 4.90
TOWER_CY = 4.30
PAD_OCT_SIZE = 5.00
TOWER_POLE_DIA = 2.20

# Octagon vertices
OCT_S = PAD_OCT_SIZE
OCT_SIDE = OCT_S / (1.0 + math.sqrt(2.0))
OCT_D = OCT_SIDE / math.sqrt(2.0)

oct_pts = [
    (TOWER_CX - OCT_S/2 + OCT_D, TOWER_CY - OCT_S/2),
    (TOWER_CX + OCT_S/2 - OCT_D, TOWER_CY - OCT_S/2),
    (TOWER_CX + OCT_S/2,         TOWER_CY - OCT_S/2 + OCT_D),
    (TOWER_CX + OCT_S/2,         TOWER_CY + OCT_S/2 - OCT_D),
    (TOWER_CX + OCT_S/2 - OCT_D, TOWER_CY + OCT_S/2),
    (TOWER_CX - OCT_S/2 + OCT_D, TOWER_CY + OCT_S/2),
    (TOWER_CX - OCT_S/2,         TOWER_CY + OCT_S/2 - OCT_D),
    (TOWER_CX - OCT_S/2,         TOWER_CY - OCT_S/2 + OCT_D),
]

# Equipment Concrete Pad & Lease Area
PAD_XMIN = TOWER_CX + 6.00  # 10.90
PAD_W = 8.10
PAD_XMAX = PAD_XMIN + PAD_W  # 19.00
PAD_YMIN = 3.00
PAD_H = 10.20
PAD_YMAX = PAD_YMIN + PAD_H  # 13.20

# Blue Lease Area (surrounds equipment pad with 4" / 0.33' clearance)
LEASE_CLR = 0.35
LEASE_XMIN = PAD_XMIN - LEASE_CLR
LEASE_XMAX = PAD_XMAX + LEASE_CLR
LEASE_YMIN = PAD_YMIN - LEASE_CLR
LEASE_YMAX = PAD_YMAX + LEASE_CLR

# Cabinets
CAB_A_W = 3.15
CAB_A_H = 5.30
CAB_A_XMIN = 13.50
CAB_A_XMAX = CAB_A_XMIN + CAB_A_W  # 16.65
CAB_A_YMIN = 6.30
CAB_A_YMAX = CAB_A_YMIN + CAB_A_H  # 11.60

CAB_B_W = 0.80
CAB_B_H = 1.90
CAB_B_XMAX = CAB_A_XMIN
CAB_B_XMIN = CAB_B_XMAX - CAB_B_W  # 12.70
CAB_B_YMAX = CAB_A_YMAX - 0.30     # 11.30
CAB_B_YMIN = CAB_B_YMAX - CAB_B_H  # 9.40

CAB_C_W = 2.20
CAB_C_H = 1.60
CAB_C_XMIN = 13.90
CAB_C_XMAX = CAB_C_XMIN + CAB_C_W  # 16.10
CAB_C_YMIN = 4.00
CAB_C_YMAX = CAB_C_YMIN + CAB_C_H  # 5.60

# Power Box D on West fence
POW_RACK_X = 0.80
POW_RACK_Y1 = 12.80
POW_RACK_Y2 = 17.50
POW_D_W = 0.50
POW_D_H = 1.90
POW_D_XMIN = POW_RACK_X
POW_D_XMAX = POW_D_XMIN + POW_D_W  # 1.30
POW_D_YMIN = 14.20
POW_D_YMAX = POW_D_YMIN + POW_D_H  # 16.10

# Cable Tray / Ice Bridge
TRAY_W = 1.20
TRAY_P1_TOP = (TOWER_CX + 0.40, TOWER_CY + OCT_S/2)  # (5.30, 6.80)
TRAY_P1_BOT = (TOWER_CX + 0.40, TOWER_CY + OCT_S/2 - TRAY_W)  # (5.30, 5.60)
TRAY_P2_TOP = (PAD_XMAX, 7.90)  # (19.00, 7.90)
TRAY_P2_BOT = (PAD_XMAX, 7.90 - TRAY_W)  # (19.00, 6.70)

# GPS Antennas
GPS_1 = (PAD_XMAX + 0.35, 7.70)
GPS_2 = (PAD_XMAX + 0.35, 6.90)
GPS_RAD = 0.16

# Helper for decimal feet to architectural feet-inches string
def ft_to_arch(ft_val):
    sign = "-" if ft_val < 0 else ""
    val = abs(ft_val)
    feet = int(val)
    inches_dec = (val - feet) * 12.0
    inches = int(round(inches_dec))
    if inches == 12:
        feet += 1
        inches = 0
    return f'{sign}{feet}\'-{inches}"'


# -------------------------------------------------------------
# 1. GENERATE CLIENT-MATCHED VIEWPORT DRAWING (Exact match to media_1791978201395_38bb1ca7.png)
# -------------------------------------------------------------
def render_client_style_viewport(filename):
    fig, ax = plt.subplots(figsize=(13, 16), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Viewport Bounds with generous margin for dimensions and leader lines
    ax.set_xlim(-8.5, 29.5)
    ax.set_ylim(-8.5, 30.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # 1. OUTER LEASED AREA (Dash-dot-dot light gray line offset 1.5' outside fence)
    LEASE_BOUND_CLR = 1.50
    lb_xmin = -LEASE_BOUND_CLR
    lb_xmax = COMPOUND_W + LEASE_BOUND_CLR
    lb_ymin = -LEASE_BOUND_CLR
    lb_ymax = COMPOUND_H + LEASE_BOUND_CLR

    leased_boundary = patches.Rectangle(
        (lb_xmin, lb_ymin), lb_xmax - lb_xmin, lb_ymax - lb_ymin,
        fill=False, edgecolor='#a0aec0', linestyle=(0, (8, 3, 2, 3, 2, 3)), linewidth=1.2, zorder=1
    )
    ax.add_patch(leased_boundary)

    # Leader to Leased Area
    ax.annotate(
        "Existing 23' x 23' Leased Area",
        xy=(COMPOUND_W * 0.35, lb_ymax),
        xytext=(lb_xmin - 2.5, lb_ymax + 3.0),
        fontsize=8.5, fontfamily='sans-serif', color='#000000',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(1.0, 0.5))
    )

    # 2. FENCE BOUNDARY WITH 'X' CHAINLINK / PALISADE POSTS
    # Draw solid black boundary
    ax.plot([0, COMPOUND_W], [0, 0], color='#000000', lw=1.2, zorder=3)
    ax.plot([COMPOUND_W, COMPOUND_W], [0, COMPOUND_H], color='#000000', lw=1.2, zorder=3)
    ax.plot([0, 0], [0, COMPOUND_H], color='#000000', lw=1.2, zorder=3)
    # North fence segments
    ax.plot([0, GATE_X1], [COMPOUND_H, COMPOUND_H], color='#000000', lw=1.2, zorder=3)
    ax.plot([GATE_X2, COMPOUND_W], [COMPOUND_H, COMPOUND_H], color='#000000', lw=1.2, zorder=3)

    # Place 'x' posts along fence lines (spaced approx 4-5 feet)
    post_marker_kwargs = dict(marker='x', markersize=5.5, markeredgewidth=1.1, color='#000000', zorder=5)

    # Corners
    for cx, cy in [(0, 0), (COMPOUND_W, 0), (0, COMPOUND_H), (COMPOUND_W, COMPOUND_H), (GATE_X1, COMPOUND_H), (GATE_X2, COMPOUND_H)]:
        ax.plot(cx, cy, **post_marker_kwargs)

    # South fence posts
    for x in np.linspace(0, COMPOUND_W, 6)[1:-1]:
        ax.plot(x, 0, **post_marker_kwargs)
    # North fence posts
    ax.plot(GATE_X1/2, COMPOUND_H, **post_marker_kwargs)
    ax.plot((GATE_X2 + COMPOUND_W)/2, COMPOUND_H, **post_marker_kwargs)
    # East fence posts
    for y in np.linspace(0, COMPOUND_H, 6)[1:-1]:
        ax.plot(COMPOUND_W, y, **post_marker_kwargs)
    # West fence posts
    for y in np.linspace(0, COMPOUND_H, 6)[1:-1]:
        ax.plot(0, y, **post_marker_kwargs)

    # Leader to Palisade Fence
    ax.annotate(
        "Existing Palisade Fence",
        xy=(COMPOUND_W, COMPOUND_H - 1.5),
        xytext=(COMPOUND_W - 8.0, COMPOUND_H - 2.8),
        fontsize=8.5, fontfamily='sans-serif', color='#000000',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(1.0, 0.5))
    )

    # 3. DOUBLE SWING GATE & RED ENTRANCE ARROW
    # Gate Swing Arcs (dashed)
    gate_rad = GATE_W / 2.0  # 6.06'
    # Swing outward (towards north)
    # Left leaf swing arc
    arc_l = patches.Arc((GATE_X1, COMPOUND_H), gate_rad*2, gate_rad*2,
                        angle=0, theta1=0, theta2=35, color='#000000', linestyle='--', linewidth=1.1, zorder=4)
    # Right leaf swing arc
    arc_r = patches.Arc((GATE_X2, COMPOUND_H), gate_rad*2, gate_rad*2,
                        angle=0, theta1=145, theta2=180, color='#000000', linestyle='--', linewidth=1.1, zorder=4)
    ax.add_patch(arc_l)
    ax.add_patch(arc_r)

    # Open Gate Leaves
    g_ang = math.radians(35)
    g_lx = GATE_X1 + gate_rad * math.cos(g_ang)
    g_ly = COMPOUND_H + gate_rad * math.sin(g_ang)
    g_rx = GATE_X2 - gate_rad * math.cos(g_ang)
    g_ry = COMPOUND_H + gate_rad * math.sin(g_ang)
    ax.plot([GATE_X1, g_lx], [COMPOUND_H, g_ly], color='#000000', lw=1.2, zorder=4)
    ax.plot([GATE_X2, g_rx], [COMPOUND_H, g_ry], color='#000000', lw=1.2, zorder=4)

    # RED SOLID ARROWHEAD & ENTRANCE TEXT
    # Red Arrow pointing INTO the gate (southward)
    arrow_tip_x = (GATE_X1 + GATE_X2) / 2.0
    arrow_tip_y = COMPOUND_H + 1.2
    arrow_w = 1.4
    arrow_len = 2.4

    red_arrow_poly = patches.Polygon(
        [
            (arrow_tip_x, arrow_tip_y),
            (arrow_tip_x - arrow_w/2, arrow_tip_y + arrow_len),
            (arrow_tip_x, arrow_tip_y + arrow_len * 0.75),
            (arrow_tip_x + arrow_w/2, arrow_tip_y + arrow_len),
        ],
        closed=True, facecolor='#e53e3e', edgecolor='none', zorder=7
    )
    ax.add_patch(red_arrow_poly)

    # "ENTRANCE" text vertically oriented or horizontal next to arrow
    ax.text(
        arrow_tip_x + 1.2, arrow_tip_y + arrow_len/2,
        "ENTRANCE",
        rotation=90, fontsize=8.0, fontweight='bold', fontfamily='sans-serif',
        color='#000000', ha='center', va='center', zorder=8
    )

    # 4. TOWER & BASE PLATE / MONOPOLE FOUNDATION
    # Octagonal concrete foundation with stipple hatch
    oct_poly = patches.Polygon(
        oct_pts, closed=True,
        facecolor='#f7fafc', edgecolor='#000000', linewidth=1.5,
        hatch='....', zorder=3
    )
    ax.add_patch(oct_poly)

    # Anchor Bolt Circle (bolt ring)
    BOLT_RING_R = 1.85
    bolt_circle = patches.Circle(
        (TOWER_CX, TOWER_CY), BOLT_RING_R,
        fill=False, edgecolor='#000000', linewidth=0.9, linestyle='-', zorder=4
    )
    ax.add_patch(bolt_circle)

    # Anchor Bolt Dots (16 bolts around the ring)
    num_bolts = 16
    for i in range(num_bolts):
        ang = 2 * math.pi * i / num_bolts
        bx = TOWER_CX + BOLT_RING_R * math.cos(ang)
        by = TOWER_CY + BOLT_RING_R * math.sin(ang)
        b_circ = patches.Circle((bx, by), 0.08, facecolor='#000000', edgecolor='#000000', zorder=5)
        ax.add_patch(b_circ)

    # Central Monopole Pole Circle
    pole_circ = patches.Circle(
        (TOWER_CX, TOWER_CY), TOWER_POLE_DIA/2,
        facecolor='#ffffff', edgecolor='#000000', linewidth=1.8, zorder=6
    )
    ax.add_patch(pole_circ)

    # Radial stiffener / gusset lines radiating from pole to bolt ring / foundation
    for i in range(12):
        ang = 2 * math.pi * i / 12
        p_in_x = TOWER_CX + (TOWER_POLE_DIA/2) * math.cos(ang)
        p_in_y = TOWER_CY + (TOWER_POLE_DIA/2) * math.sin(ang)
        p_out_x = TOWER_CX + (BOLT_RING_R + 0.35) * math.cos(ang)
        p_out_y = TOWER_CY + (BOLT_RING_R + 0.35) * math.sin(ang)
        ax.plot([p_in_x, p_out_x], [p_in_y, p_out_y], color='#000000', lw=0.9, zorder=5)

    # Leader to Monopole
    ax.annotate(
        "Monopole\n65.50'",
        xy=(TOWER_CX + 1.2, TOWER_CY + 1.2),
        xytext=(TOWER_CX + 3.8, TOWER_CY + 4.8),
        fontsize=8.5, fontfamily='sans-serif', color='#000000', ha='left',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(0.0, 0.5))
    )

    # 5. EQUIPMENT CONCRETE PAD & LEASE AREA
    # Equipment Pad with concrete stipple hatch
    eq_pad = patches.Rectangle(
        (PAD_XMIN, PAD_YMIN), PAD_W, PAD_H,
        facecolor='#f7fafc', edgecolor='#000000', linewidth=1.4,
        hatch='....', zorder=2
    )
    ax.add_patch(eq_pad)

    # Blue Lease Area boundary (distinctive client blue border)
    lease_rect = patches.Rectangle(
        (LEASE_XMIN, LEASE_YMIN), LEASE_XMAX - LEASE_XMIN, LEASE_YMAX - LEASE_YMIN,
        fill=False, edgecolor='#0033cc', linewidth=1.6, zorder=3
    )
    ax.add_patch(lease_rect)

    # Leaders to Equipment Pad & Lease Area
    ax.annotate(
        f'Equipment Pad 8\'-1" x 10\'-2"',
        xy=(PAD_XMAX, (PAD_YMIN + PAD_YMAX)/2),
        xytext=(PAD_XMAX + 3.2, (PAD_YMIN + PAD_YMAX)/2 + 1.2),
        fontsize=8.0, fontfamily='sans-serif', color='#000000', ha='left',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(0.0, 0.5))
    )
    ax.annotate(
        f'Equipment Lease Area 8\'-1" x 10\'-2"',
        xy=(PAD_XMAX, PAD_YMIN + 0.5),
        xytext=(PAD_XMAX + 3.2, PAD_YMIN - 1.2),
        fontsize=8.0, fontfamily='sans-serif', color='#000000', ha='left',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(0.0, 0.5))
    )

    # 6. CABINETS (Outdoor Cabinets)
    # Cabinet A
    cab_a = patches.Rectangle(
        (CAB_A_XMIN, CAB_A_YMIN), CAB_A_W, CAB_A_H,
        facecolor='#ffffff', edgecolor='#000000', linewidth=1.3, zorder=6
    )
    ax.add_patch(cab_a)
    ax.text(
        (CAB_A_XMIN + CAB_A_XMAX)/2, (CAB_A_YMIN + CAB_A_YMAX)/2,
        "Outdoor\nCabinet",
        fontsize=7.5, fontfamily='sans-serif', color='#000000', ha='center', va='center', zorder=7
    )

    # Cabinet AC B
    cab_b = patches.Rectangle(
        (CAB_B_XMIN, CAB_B_YMIN), CAB_B_W, CAB_B_H,
        facecolor='#ffffff', edgecolor='#000000', linewidth=1.2, zorder=6
    )
    ax.add_patch(cab_b)
    ax.text(
        (CAB_B_XMIN + CAB_B_XMAX)/2, (CAB_B_YMIN + CAB_B_YMAX)/2,
        "AC",
        fontsize=6.5, fontfamily='sans-serif', color='#000000', ha='center', va='center', zorder=7
    )

    # Cabinet C
    cab_c = patches.Rectangle(
        (CAB_C_XMIN, CAB_C_YMIN), CAB_C_W, CAB_C_H,
        facecolor='#ffffff', edgecolor='#000000', linewidth=1.2, zorder=6
    )
    ax.add_patch(cab_c)
    ax.text(
        (CAB_C_XMIN + CAB_C_XMAX)/2, (CAB_C_YMIN + CAB_C_YMAX)/2,
        "Outdoor\nCabinet",
        fontsize=7.0, fontfamily='sans-serif', color='#000000', ha='center', va='center', zorder=7
    )

    # 7. GPS ANTENNAS (Blue circle dots as in client sample)
    for gps_pt in [GPS_1, GPS_2]:
        gps_dot = patches.Circle(gps_pt, GPS_RAD, facecolor='#0033cc', edgecolor='#000000', lw=0.6, zorder=8)
        ax.add_patch(gps_dot)

    ax.annotate(
        "GPS",
        xy=(GPS_1[0], GPS_1[1]),
        xytext=(GPS_1[0] + 1.2, GPS_1[1] - 0.5),
        fontsize=8.0, fontfamily='sans-serif', color='#000000', ha='left',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.8, relpos=(0.0, 0.5))
    )

    # 8. ICE BRIDGE / CABLE TRAY (Dense 45-deg Hatching)
    tray_poly_pts = [TRAY_P1_TOP, TRAY_P2_TOP, TRAY_P2_BOT, TRAY_P1_BOT]
    tray_patch = patches.Polygon(
        tray_poly_pts, closed=True,
        facecolor='#ffffff', edgecolor='#000000', linewidth=1.3,
        hatch='//////', zorder=5
    )
    ax.add_patch(tray_patch)

    # Leader to ICE Bridge
    tray_mid_x = (TRAY_P1_TOP[0] + TRAY_P2_TOP[0]) / 2.0
    tray_mid_y = (TRAY_P1_TOP[1] + TRAY_P2_TOP[1]) / 2.0
    ax.annotate(
        "Existing ICE bridge",
        xy=(tray_mid_x, tray_mid_y),
        xytext=(tray_mid_x - 3.5, tray_mid_y + 4.5),
        fontsize=8.5, fontfamily='sans-serif', color='#000000', ha='right',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(1.0, 0.5))
    )

    # 9. POWER BOX / METER BANK ON WEST FENCE
    # Slanted or straight rack with boxes
    ax.plot([POW_RACK_X, POW_RACK_X], [POW_RACK_Y1, POW_RACK_Y2], color='#000000', lw=1.5, zorder=5)
    pow_box = patches.Rectangle(
        (POW_D_XMIN, POW_D_YMIN), POW_D_W, POW_D_H,
        facecolor='#ffffff', edgecolor='#000000', lw=1.2, zorder=6
    )
    ax.add_patch(pow_box)

    # Leader to Meter Bank / Power Box
    ax.annotate(
        "Meter Bank & Power Box",
        xy=(POW_D_XMAX, (POW_D_YMIN + POW_D_YMAX)/2),
        xytext=(POW_D_XMAX + 2.5, POW_D_YMAX + 2.5),
        fontsize=8.5, fontfamily='sans-serif', color='#000000', ha='left',
        arrowprops=dict(arrowstyle='->', color='#000000', lw=0.9, relpos=(0.0, 0.5))
    )

    # 10. CLIENT STANDARD DIMENSIONS (Architectural Ticks '/' at 45 deg)
    TICK_LEN = 0.35

    def draw_arch_dim_h(x1, x2, y, text_str):
        # Dimension line
        ax.plot([x1, x2], [y, y], color='#000000', lw=0.8, zorder=9)
        # 45 deg architectural ticks (slope = 1.0)
        ax.plot([x1 - TICK_LEN/2, x1 + TICK_LEN/2], [y - TICK_LEN/2, y + TICK_LEN/2], color='#000000', lw=1.4, zorder=10)
        ax.plot([x2 - TICK_LEN/2, x2 + TICK_LEN/2], [y - TICK_LEN/2, y + TICK_LEN/2], color='#000000', lw=1.4, zorder=10)
        # Witness / extension lines
        # Text
        ax.text((x1 + x2)/2, y + 0.35, text_str, color='#000000', fontsize=8.0,
                fontfamily='sans-serif', ha='center', va='bottom', zorder=11,
                bbox=dict(facecolor='#ffffff', edgecolor='none', pad=1.0))

    def draw_arch_dim_v(x, y1, y2, text_str):
        ax.plot([x, x], [y1, y2], color='#000000', lw=0.8, zorder=9)
        ax.plot([x - TICK_LEN/2, x + TICK_LEN/2], [y1 - TICK_LEN/2, y1 + TICK_LEN/2], color='#000000', lw=1.4, zorder=10)
        ax.plot([x - TICK_LEN/2, x + TICK_LEN/2], [y2 - TICK_LEN/2, y2 + TICK_LEN/2], color='#000000', lw=1.4, zorder=10)
        ax.text(x - 0.35, (y1 + y2)/2, text_str, color='#000000', fontsize=8.0,
                fontfamily='sans-serif', ha='right', va='center', rotation=90, zorder=11,
                bbox=dict(facecolor='#ffffff', edgecolor='none', pad=1.0))

    # Extension lines
    def draw_ext_line(p1, p2):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#718096', lw=0.6, linestyle='-', zorder=2)

    # Bottom Tier 1 (Segments)
    Y_DIM_B1 = -2.2
    draw_arch_dim_h(0, TOWER_CX, Y_DIM_B1, ft_to_arch(TOWER_CX))  # 4'-11" (4.9')
    draw_arch_dim_h(TOWER_CX, PAD_XMIN, Y_DIM_B1, ft_to_arch(PAD_XMIN - TOWER_CX))  # 6'-0"
    draw_arch_dim_h(PAD_XMIN, PAD_XMAX, Y_DIM_B1, ft_to_arch(PAD_W))  # 8'-1"
    draw_arch_dim_h(PAD_XMAX, COMPOUND_W, Y_DIM_B1, ft_to_arch(COMPOUND_W - PAD_XMAX))  # 1'-1"

    # Extension lines for bottom
    draw_ext_line((0, 0), (0, Y_DIM_B1 - 1.8))
    draw_ext_line((TOWER_CX, TOWER_CY), (TOWER_CX, Y_DIM_B1 - 0.5))
    draw_ext_line((PAD_XMIN, PAD_YMIN), (PAD_XMIN, Y_DIM_B1 - 0.5))
    draw_ext_line((PAD_XMAX, PAD_YMIN), (PAD_XMAX, Y_DIM_B1 - 0.5))
    draw_ext_line((COMPOUND_W, 0), (COMPOUND_W, Y_DIM_B1 - 1.8))

    # Bottom Tier 2 (Overall 20'-1")
    Y_DIM_B2 = -4.0
    draw_arch_dim_h(0, COMPOUND_W, Y_DIM_B2, ft_to_arch(COMPOUND_W))

    # Left Tier 1 (Segments)
    X_DIM_L1 = -2.2
    draw_arch_dim_v(X_DIM_L1, 0, TOWER_CY, ft_to_arch(TOWER_CY))  # 4'-4" (4.3')
    draw_arch_dim_v(X_DIM_L1, TOWER_CY, COMPOUND_H, ft_to_arch(COMPOUND_H - TOWER_CY))  # 15'-9" (15.8')

    draw_ext_line((0, 0), (X_DIM_L1 - 1.8, 0))
    draw_ext_line((TOWER_CX, TOWER_CY), (X_DIM_L1 - 0.5, TOWER_CY))
    draw_ext_line((0, COMPOUND_H), (X_DIM_L1 - 1.8, COMPOUND_H))

    # Left Tier 2 (Overall 20'-1")
    X_DIM_L2 = -4.0
    draw_arch_dim_v(X_DIM_L2, 0, COMPOUND_H, ft_to_arch(COMPOUND_H))

    # Right Tier 1 (Segments)
    X_DIM_R1 = COMPOUND_W + 2.2
    draw_arch_dim_v(X_DIM_R1, 0, PAD_YMIN, ft_to_arch(PAD_YMIN))  # 3'-0"
    draw_arch_dim_v(X_DIM_R1, PAD_YMIN, PAD_YMAX, ft_to_arch(PAD_H))  # 10'-2"
    draw_arch_dim_v(X_DIM_R1, PAD_YMAX, COMPOUND_H, ft_to_arch(COMPOUND_H - PAD_YMAX))  # 6'-11" (6.9')

    draw_ext_line((COMPOUND_W, 0), (X_DIM_R1 + 1.8, 0))
    draw_ext_line((PAD_XMAX, PAD_YMIN), (X_DIM_R1 + 0.5, PAD_YMIN))
    draw_ext_line((PAD_XMAX, PAD_YMAX), (X_DIM_R1 + 0.5, PAD_YMAX))
    draw_ext_line((COMPOUND_W, COMPOUND_H), (X_DIM_R1 + 1.8, COMPOUND_H))

    # Right Tier 2 (Overall 20'-1")
    X_DIM_R2 = COMPOUND_W + 4.0
    draw_arch_dim_v(X_DIM_R2, 0, COMPOUND_H, ft_to_arch(COMPOUND_H))

    # Top Tier 1 (Gate segments)
    Y_DIM_T1 = COMPOUND_H + 4.2
    draw_arch_dim_h(0, GATE_X1, Y_DIM_T1, ft_to_arch(GATE_X1))  # 4'-0"
    draw_arch_dim_h(GATE_X1, GATE_X2, Y_DIM_T1, ft_to_arch(GATE_W))  # 12'-1" (12.12')
    draw_arch_dim_h(GATE_X2, COMPOUND_W, Y_DIM_T1, ft_to_arch(GATE_EAST))  # 4'-0" (3.98')

    draw_ext_line((0, COMPOUND_H), (0, Y_DIM_T1 + 0.5))
    draw_ext_line((GATE_X1, COMPOUND_H), (GATE_X1, Y_DIM_T1 + 0.5))
    draw_ext_line((GATE_X2, COMPOUND_H), (GATE_X2, Y_DIM_T1 + 0.5))
    draw_ext_line((COMPOUND_W, COMPOUND_H), (COMPOUND_W, Y_DIM_T1 + 0.5))

    # Leased area margin dimensions (1'-6" as in client sample)
    draw_arch_dim_v(lb_xmin - 0.8, -LEASE_BOUND_CLR, 0, "1'-6\"")
    draw_arch_dim_v(lb_xmax + 0.8, -LEASE_BOUND_CLR, 0, "1'-6\"")
    draw_arch_dim_v(lb_xmin - 0.8, COMPOUND_H, lb_ymax, "1'-6\"")
    draw_arch_dim_v(lb_xmax + 0.8, COMPOUND_H, lb_ymax, "1'-6\"")

    # 11. CLIENT NORTH ARROW (Top Right)
    na_x, na_y = COMPOUND_W + 2.0, COMPOUND_H + 3.0
    # Split needle arrow (left side black, right side red)
    arrow_h = 3.2
    arrow_hw = 0.55
    needle_left = patches.Polygon(
        [(na_x, na_y + arrow_h), (na_x - arrow_hw, na_y), (na_x, na_y + arrow_h * 0.25)],
        closed=True, facecolor='#000000', edgecolor='#000000', lw=0.5, zorder=8
    )
    needle_right = patches.Polygon(
        [(na_x, na_y + arrow_h), (na_x + arrow_hw, na_y), (na_x, na_y + arrow_h * 0.25)],
        closed=True, facecolor='#e53e3e', edgecolor='#e53e3e', lw=0.5, zorder=8
    )
    ax.add_patch(needle_left)
    ax.add_patch(needle_right)
    ax.text(na_x, na_y + arrow_h + 0.4, "N", fontsize=14, fontweight='bold',
            fontfamily='serif', color='#000000', ha='center', va='bottom', zorder=9)

    plt.tight_layout()
    plt.savefig(filename, facecolor='#ffffff', edgecolor='none', dpi=300)
    plt.close()
    print(f"Client-Style Viewport Drawing saved to: {filename}")


# -------------------------------------------------------------
# 2. GENERATE FULL SHEET DRAWING (Exact match to forest_lakes_p2.png)
# -------------------------------------------------------------
def render_full_sheet(viewport_png_path, filename):
    # Sheet dimensions: A3 / Tabloid Landscape (ratio ~ 1.414 or 1191 x 842 pt -> 3573 x 2526 px at 300 DPI)
    sheet_w, sheet_h = 3573, 2526
    fig = plt.figure(figsize=(sheet_w / 300.0, sheet_h / 300.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#ffffff')
    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.axis('off')

    # Sheet Outer Border & Inner Margins
    MARGIN = 40
    TB_WIDTH = 620  # Title block column on right
    DRAW_XMAX = sheet_w - MARGIN - TB_WIDTH

    # Outer Thick Border
    outer_border = patches.Rectangle(
        (MARGIN, MARGIN), sheet_w - 2*MARGIN, sheet_h - 2*MARGIN,
        fill=False, edgecolor='#000000', linewidth=2.5, zorder=20
    )
    ax.add_patch(outer_border)

    # Inner Border
    inner_border = patches.Rectangle(
        (MARGIN + 6, MARGIN + 6), sheet_w - 2*MARGIN - 12, sheet_h - 2*MARGIN - 12,
        fill=False, edgecolor='#000000', linewidth=1.0, zorder=20
    )
    ax.add_patch(inner_border)

    # Vertical Divider Line between Drawing Viewport and Title Block
    ax.plot([DRAW_XMAX, DRAW_XMAX], [MARGIN, sheet_h - MARGIN], color='#000000', lw=1.8, zorder=20)

    # 1. PLACE COMPILED VIEWPORT DRAWING
    if os.path.exists(viewport_png_path):
        vp_img = Image.open(viewport_png_path)
        # Target area for viewport:
        vp_w = DRAW_XMAX - MARGIN - 40
        vp_h = sheet_h - 2*MARGIN - 40
        # Preserve aspect ratio
        vp_ratio = vp_img.width / vp_img.height
        target_ratio = vp_w / vp_h
        if vp_ratio > target_ratio:
            place_w = vp_w
            place_h = vp_w / vp_ratio
        else:
            place_h = vp_h
            place_w = vp_h * vp_ratio
        place_x = MARGIN + 20 + (vp_w - place_w)/2
        place_y = MARGIN + 20 + (vp_h - place_h)/2
        ax.imshow(vp_img, extent=[place_x, place_x + place_w, place_y, place_y + place_h], zorder=5)

    # 2. DRAW OFFICIAL TITLE BLOCK (RIGHT COLUMN)
    tb_x0 = DRAW_XMAX
    tb_x1 = sheet_w - MARGIN

    def tb_line_h(y, lw=1.2):
        ax.plot([tb_x0, tb_x1], [y, y], color='#000000', lw=lw, zorder=21)

    # LOGO 1: Everest Infrastructure Partners
    y_logo1_top = sheet_h - MARGIN
    y_logo1_bot = y_logo1_top - 180
    tb_line_h(y_logo1_bot)
    if os.path.exists(EVEREST_LOGO_PATH):
        ev_img = Image.open(EVEREST_LOGO_PATH)
        ev_w, ev_h = ev_img.size
        target_h = 140
        target_w = ev_w * (target_h / ev_h)
        if target_w > (TB_WIDTH - 40):
            target_w = TB_WIDTH - 40
            target_h = ev_h * (target_w / ev_w)
        lx = tb_x0 + (TB_WIDTH - target_w)/2
        ly = y_logo1_bot + (180 - target_h)/2
        ax.imshow(ev_img, extent=[lx, lx + target_w, ly, ly + target_h], zorder=22)

    # LOGO 2: Visual Intelligence
    y_logo2_top = y_logo1_bot
    y_logo2_bot = y_logo2_top - 130
    tb_line_h(y_logo2_bot)
    if os.path.exists(VI_LOGO_PATH):
        vi_img = Image.open(VI_LOGO_PATH)
        vi_w, vi_h = vi_img.size
        target_h = 90
        target_w = vi_w * (target_h / vi_h)
        if target_w > (TB_WIDTH - 40):
            target_w = TB_WIDTH - 40
            target_h = vi_h * (target_w / vi_w)
        lx = tb_x0 + (TB_WIDTH - target_w)/2
        ly = y_logo2_bot + (130 - target_h)/2
        ax.imshow(vi_img, extent=[lx, lx + target_w, ly, ly + target_h], zorder=22)

    # SECTION 3: General Notes
    y_notes_top = y_logo2_bot
    y_notes_bot = y_notes_top - 170
    tb_line_h(y_notes_bot)
    ax.text(tb_x0 + 15, y_notes_top - 24, "General Notes", fontsize=8.5, fontweight='bold', fontfamily='sans-serif', zorder=22)
    notes_body = (
        "1.  Information in this report is based on data\n"
        "     captured by drone flight\n"
        "2.  A physical tower climb was not completed\n"
        "3.  This is not a condition assessment of the tower"
    )
    ax.text(tb_x0 + 15, y_notes_top - 55, notes_body, fontsize=7.5, fontfamily='sans-serif', va='top', zorder=22)

    # SECTION 4: Submittals Table
    y_sub_top = y_notes_bot
    y_sub_bot = y_sub_top - 130
    tb_line_h(y_sub_bot)
    ax.text(tb_x0 + (TB_WIDTH)/2, y_sub_top - 20, "Submittals", fontsize=8.0, fontweight='bold', fontfamily='sans-serif', ha='center', zorder=22)
    tb_line_h(y_sub_top - 32, lw=0.8)
    # Header cols
    c1, c2, c3 = tb_x0 + 55, tb_x0 + 185, tb_x0 + 380
    ax.plot([tb_x0 + 75, tb_x0 + 75], [y_sub_top - 32, y_sub_bot], color='#000000', lw=0.8, zorder=21)
    ax.plot([tb_x0 + 200, tb_x0 + 200], [y_sub_top - 32, y_sub_bot], color='#000000', lw=0.8, zorder=21)
    ax.text(tb_x0 + 38, y_sub_top - 48, "Rev", fontsize=7.5, ha='center', zorder=22)
    ax.text(tb_x0 + 138, y_sub_top - 48, "Date", fontsize=7.5, ha='center', zorder=22)
    ax.text(tb_x0 + 380, y_sub_top - 48, "Description", fontsize=7.5, ha='center', zorder=22)
    tb_line_h(y_sub_top - 62, lw=0.8)
    # Row A
    ax.text(tb_x0 + 38, y_sub_top - 85, "A", fontsize=7.5, ha='center', zorder=22)
    ax.text(tb_x0 + 138, y_sub_top - 85, "10/14/26", fontsize=7.5, ha='center', zorder=22)
    ax.text(tb_x0 + 380, y_sub_top - 85, "Issue for review", fontsize=7.5, ha='center', zorder=22)

    # SECTION 5: Site Information
    y_site_top = y_sub_bot
    y_site_bot = y_site_top - 260
    tb_line_h(y_site_bot)
    line_y = y_site_top - 28
    site_info_rows = [
        ("Lat", ":  39.196442"),
        ("Long", ":  -114.855244"),
        ("Site ID", ":  US1051671"),
        ("Site name", ":  Blue Diamond"),
        ("Site address", ":  185 224th S St, Ely, NV"),
    ]
    for lbl, val in site_info_rows:
        ax.text(tb_x0 + 15, line_y, lbl, fontsize=8.0, fontfamily='sans-serif', zorder=22)
        ax.text(tb_x0 + 130, line_y, val, fontsize=8.0, fontfamily='sans-serif', zorder=22)
        line_y -= 28
        tb_line_h(line_y + 12, lw=0.6)

    # SECTION 6: Schematic Drawings Title
    y_sch_top = y_site_bot
    y_sch_bot = y_sch_top - 180
    tb_line_h(y_sch_bot)
    ax.text(tb_x0 + 15, y_sch_top - 25, "Schematic drawings", fontsize=8.0, fontfamily='sans-serif', zorder=22)
    ax.text(tb_x0 + TB_WIDTH/2, y_sch_top - 100, "Compound Line Diagram 1", fontsize=9.5, fontweight='bold', fontfamily='sans-serif', ha='center', zorder=22)

    # SECTION 7: Elevation Table
    y_elev_top = y_sch_bot
    y_elev_bot = y_elev_top - 260
    tb_line_h(y_elev_bot)
    elev_rows = [
        ("Overall Height AGL (Ft)", "70.60'"),
        ("Structure Height + Appurtenances (Ft)", "70.05'"),
        ("Structure Height (Ft)", "65.50'"),
        ("Foundation Height (Ft)", "0'"),
        ("Ground Level (Ft)", "-0.55'"),
        ("AMSL (Ground Elevation)", "6778.52'"),
    ]
    col_div = tb_x0 + TB_WIDTH - 150
    ax.plot([col_div, col_div], [y_elev_top, y_elev_bot], color='#000000', lw=0.8, zorder=21)

    cur_ey = y_elev_top - 24
    for desc, val in elev_rows:
        ax.text(tb_x0 + 15, cur_ey, desc, fontsize=7.5, fontfamily='sans-serif', zorder=22)
        ax.text(tb_x1 - 20, cur_ey, val, fontsize=7.5, fontfamily='sans-serif', ha='right', zorder=22)
        cur_ey -= 25
        tb_line_h(cur_ey + 10, lw=0.6)

    # SECTION 8: Flight Date & Drawing Created By (Uirtus)
    y_date_top = y_elev_bot
    y_date_bot = y_date_top - 60
    tb_line_h(y_date_bot)
    ax.text(tb_x0 + 15, y_date_top - 35, "Drone flight date :  07/28/2026", fontsize=8.0, fontfamily='sans-serif', zorder=22)

    # Final Box: Drawing Created by Uirtus
    ax.text(tb_x0 + 15, y_date_bot - 45, "Drawing created by :", fontsize=8.0, fontfamily='sans-serif', zorder=22)
    ax.text(tb_x1 - 25, y_date_bot - 45, "Uirtus", fontsize=15.0, fontweight='bold', fontfamily='sans-serif', color='#000000', ha='right', zorder=22)

    plt.savefig(filename, facecolor='#ffffff', edgecolor='none', dpi=300)
    plt.close()
    print(f"Full Sheet Drawing saved to: {filename}")


# -------------------------------------------------------------
# 3. GENERATE CLIENT-MATCHED AUTOCAD DXF
# -------------------------------------------------------------
def build_client_dxf(filename):
    doc = ezdxf.new('R2018', setup=True)
    msp = doc.modelspace()

    # Standard Client Layers
    layers = [
        ("0", 7, "CONTINUOUS"),
        ("Compound Line", 7, "CONTINUOUS"),     # Palisade fence boundary
        ("broken line", 8, "DASHED"),           # Swing arcs & leased area
        ("Concrete", 5, "CONTINUOUS"),          # Pads & foundation
        ("Complound Layout", 1, "CONTINUOUS"),  # Red arrow, equipment, tray
        ("Dim Compound", 7, "CONTINUOUS"),      # Dimensions
        ("TEXT", 7, "CONTINUOUS"),              # Notes and callouts
        ("LEAST_AREA", 5, "CONTINUOUS"),        # Blue lease area
    ]
    for l_name, l_col, l_lt in layers:
        if l_name not in doc.layers:
            doc.layers.add(l_name, color=l_col, linetype=l_lt)

    # 1. Outer Leased Area (dashed)
    CLR = 1.5
    msp.add_lwpolyline(
        [(-CLR, -CLR), (COMPOUND_W + CLR, -CLR), (COMPOUND_W + CLR, COMPOUND_H + CLR), (-CLR, COMPOUND_H + CLR), (-CLR, -CLR)],
        dxfattribs={'layer': 'broken line', 'color': 8}
    )

    # 2. Fence Boundary
    msp.add_line((0, 0), (COMPOUND_W, 0), dxfattribs={'layer': 'Compound Line'})
    msp.add_line((COMPOUND_W, 0), (COMPOUND_W, COMPOUND_H), dxfattribs={'layer': 'Compound Line'})
    msp.add_line((0, 0), (0, COMPOUND_H), dxfattribs={'layer': 'Compound Line'})
    msp.add_line((0, COMPOUND_H), (GATE_X1, COMPOUND_H), dxfattribs={'layer': 'Compound Line'})
    msp.add_line((GATE_X2, COMPOUND_H), (COMPOUND_W, COMPOUND_H), dxfattribs={'layer': 'Compound Line'})

    # Gate Opening
    msp.add_line((GATE_X1, COMPOUND_H), (GATE_X2, COMPOUND_H), dxfattribs={'layer': 'broken line', 'color': 8})

    # Gate leaves
    gate_rad = GATE_W / 2.0
    g_ang = math.radians(35)
    g_lx = GATE_X1 + gate_rad * math.cos(g_ang)
    g_ly = COMPOUND_H + gate_rad * math.sin(g_ang)
    g_rx = GATE_X2 - gate_rad * math.cos(g_ang)
    g_ry = COMPOUND_H + gate_rad * math.sin(g_ang)
    msp.add_line((GATE_X1, COMPOUND_H), (g_lx, g_ly), dxfattribs={'layer': 'Compound Line'})
    msp.add_line((GATE_X2, COMPOUND_H), (g_rx, g_ry), dxfattribs={'layer': 'Compound Line'})

    # Post markers 'X'
    def add_x_mark(px, py):
        d = 0.25
        msp.add_line((px - d, py - d), (px + d, py + d), dxfattribs={'layer': 'Compound Line'})
        msp.add_line((px - d, py + d), (px + d, py - d), dxfattribs={'layer': 'Compound Line'})

    for cx, cy in [(0, 0), (COMPOUND_W, 0), (0, COMPOUND_H), (COMPOUND_W, COMPOUND_H), (GATE_X1, COMPOUND_H), (GATE_X2, COMPOUND_H)]:
        add_x_mark(cx, cy)
    for x in np.linspace(0, COMPOUND_W, 6)[1:-1]:
        add_x_mark(x, 0)
    add_x_mark(GATE_X1/2, COMPOUND_H)
    add_x_mark((GATE_X2 + COMPOUND_W)/2, COMPOUND_H)
    for y in np.linspace(0, COMPOUND_H, 6)[1:-1]:
        add_x_mark(COMPOUND_W, y)
    for y in np.linspace(0, COMPOUND_H, 6)[1:-1]:
        add_x_mark(0, y)

    # 3. RED ENTRANCE ARROW
    arrow_tip_x = (GATE_X1 + GATE_X2) / 2.0
    arrow_tip_y = COMPOUND_H + 1.2
    arrow_w = 1.4
    arrow_len = 2.4
    arrow_pts = [
        (arrow_tip_x, arrow_tip_y),
        (arrow_tip_x - arrow_w/2, arrow_tip_y + arrow_len),
        (arrow_tip_x, arrow_tip_y + arrow_len * 0.75),
        (arrow_tip_x + arrow_w/2, arrow_tip_y + arrow_len),
        (arrow_tip_x, arrow_tip_y)
    ]
    hatch_arrow = msp.add_hatch(color=1, dxfattribs={'layer': 'Complound Layout'})
    hatch_arrow.paths.add_polyline_path(arrow_pts, is_closed=True)
    msp.add_text("ENTRANCE", height=0.45, dxfattribs={'layer': 'Complound Layout', 'color': 1, 'rotation': 90}).set_placement(
        (arrow_tip_x + 1.1, arrow_tip_y + arrow_len/2))

    # 4. TOWER & FOUNDATION
    oct_pts_closed = oct_pts + [oct_pts[0]]
    msp.add_lwpolyline(oct_pts_closed, dxfattribs={'layer': 'Concrete', 'color': 7})
    # Monopole Pole
    msp.add_circle((TOWER_CX, TOWER_CY), TOWER_POLE_DIA/2, dxfattribs={'layer': 'Concrete', 'color': 7})
    # Bolt Circle
    BOLT_RING_R = 1.85
    msp.add_circle((TOWER_CX, TOWER_CY), BOLT_RING_R, dxfattribs={'layer': 'broken line', 'color': 8})
    for i in range(16):
        ang = 2 * math.pi * i / 16
        bx = TOWER_CX + BOLT_RING_R * math.cos(ang)
        by = TOWER_CY + BOLT_RING_R * math.sin(ang)
        msp.add_circle((bx, by), 0.08, dxfattribs={'layer': 'Concrete', 'color': 7})
    for i in range(12):
        ang = 2 * math.pi * i / 12
        p_in_x = TOWER_CX + (TOWER_POLE_DIA/2) * math.cos(ang)
        p_in_y = TOWER_CY + (TOWER_POLE_DIA/2) * math.sin(ang)
        p_out_x = TOWER_CX + (BOLT_RING_R + 0.35) * math.cos(ang)
        p_out_y = TOWER_CY + (BOLT_RING_R + 0.35) * math.sin(ang)
        msp.add_line((p_in_x, p_in_y), (p_out_x, p_out_y), dxfattribs={'layer': 'Concrete', 'color': 7})

    # 5. EQUIPMENT PAD & LEASE AREA
    pad_corners = [(PAD_XMIN, PAD_YMIN), (PAD_XMAX, PAD_YMIN), (PAD_XMAX, PAD_YMAX), (PAD_XMIN, PAD_YMAX), (PAD_XMIN, PAD_YMIN)]
    msp.add_lwpolyline(pad_corners, dxfattribs={'layer': 'Concrete', 'color': 7})
    lease_corners = [(LEASE_XMIN, LEASE_YMIN), (LEASE_XMAX, LEASE_YMIN), (LEASE_XMAX, LEASE_YMAX), (LEASE_XMIN, LEASE_YMAX), (LEASE_XMIN, LEASE_YMIN)]
    msp.add_lwpolyline(lease_corners, dxfattribs={'layer': 'LEAST_AREA', 'color': 5})

    # Cabinets
    cab_a_corners = [(CAB_A_XMIN, CAB_A_YMIN), (CAB_A_XMAX, CAB_A_YMIN), (CAB_A_XMAX, CAB_A_YMAX), (CAB_A_XMIN, CAB_A_YMAX), (CAB_A_XMIN, CAB_A_YMIN)]
    msp.add_lwpolyline(cab_a_corners, dxfattribs={'layer': 'Complound Layout', 'color': 7})
    cab_b_corners = [(CAB_B_XMIN, CAB_B_YMIN), (CAB_B_XMAX, CAB_B_YMIN), (CAB_B_XMAX, CAB_B_YMAX), (CAB_B_XMIN, CAB_B_YMAX), (CAB_B_XMIN, CAB_B_YMIN)]
    msp.add_lwpolyline(cab_b_corners, dxfattribs={'layer': 'Complound Layout', 'color': 7})
    cab_c_corners = [(CAB_C_XMIN, CAB_C_YMIN), (CAB_C_XMAX, CAB_C_YMIN), (CAB_C_XMAX, CAB_C_YMAX), (CAB_C_XMIN, CAB_C_YMAX), (CAB_C_XMIN, CAB_C_YMIN)]
    msp.add_lwpolyline(cab_c_corners, dxfattribs={'layer': 'Complound Layout', 'color': 7})

    # GPS
    msp.add_circle(GPS_1, GPS_RAD, dxfattribs={'layer': 'Complound Layout', 'color': 5})
    msp.add_circle(GPS_2, GPS_RAD, dxfattribs={'layer': 'Complound Layout', 'color': 5})

    # Cable Tray / Ice Bridge
    msp.add_line(TRAY_P1_TOP, TRAY_P2_TOP, dxfattribs={'layer': 'Complound Layout', 'color': 7})
    msp.add_line(TRAY_P1_BOT, TRAY_P2_BOT, dxfattribs={'layer': 'Complound Layout', 'color': 7})
    num_rungs = 24
    for i in range(num_rungs + 1):
        t = i / num_rungs
        rt_x = TRAY_P1_TOP[0] + t * (TRAY_P2_TOP[0] - TRAY_P1_TOP[0])
        rt_y = TRAY_P1_TOP[1] + t * (TRAY_P2_TOP[1] - TRAY_P1_TOP[1])
        rb_x = TRAY_P1_BOT[0] + t * (TRAY_P2_BOT[0] - TRAY_P1_BOT[0])
        rb_y = TRAY_P1_BOT[1] + t * (TRAY_P2_BOT[1] - TRAY_P1_BOT[1])
        msp.add_line((rt_x, rt_y), (rb_x, rb_y), dxfattribs={'layer': 'Complound Layout', 'color': 7})

    # Power Box
    msp.add_line((POW_RACK_X, POW_RACK_Y1), (POW_RACK_X, POW_RACK_Y2), dxfattribs={'layer': 'Complound Layout', 'color': 7})
    pow_corners = [(POW_D_XMIN, POW_D_YMIN), (POW_D_XMAX, POW_D_YMIN), (POW_D_XMAX, POW_D_YMAX), (POW_D_XMIN, POW_D_YMAX), (POW_D_XMIN, POW_D_YMIN)]
    msp.add_lwpolyline(pow_corners, dxfattribs={'layer': 'Complound Layout', 'color': 7})

    # 6. ARCHITECTURAL TICK DIMENSIONS
    TICK_D = 0.25
    def add_arch_dim_h_dxf(x1, x2, y, val_str):
        msp.add_line((x1, y), (x2, y), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_line((x1 - TICK_D/2, y - TICK_D/2), (x1 + TICK_D/2, y + TICK_D/2), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_line((x2 - TICK_D/2, y - TICK_D/2), (x2 + TICK_D/2, y + TICK_D/2), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_text(val_str, height=0.35, dxfattribs={'layer': 'Dim Compound', 'color': 7}).set_placement(
            ((x1 + x2)/2, y + 0.15))

    def add_arch_dim_v_dxf(x, y1, y2, val_str):
        msp.add_line((x, y1), (x, y2), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_line((x - TICK_D/2, y1 - TICK_D/2), (x + TICK_D/2, y1 + TICK_D/2), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_line((x - TICK_D/2, y2 - TICK_D/2), (x + TICK_D/2, y2 + TICK_D/2), dxfattribs={'layer': 'Dim Compound', 'color': 7})
        msp.add_text(val_str, height=0.35, dxfattribs={'layer': 'Dim Compound', 'color': 7, 'rotation': 90}).set_placement(
            (x - 0.15, (y1 + y2)/2))

    # Bottom
    add_arch_dim_h_dxf(0, TOWER_CX, -2.2, ft_to_arch(TOWER_CX))
    add_arch_dim_h_dxf(TOWER_CX, PAD_XMIN, -2.2, ft_to_arch(PAD_XMIN - TOWER_CX))
    add_arch_dim_h_dxf(PAD_XMIN, PAD_XMAX, -2.2, ft_to_arch(PAD_W))
    add_arch_dim_h_dxf(PAD_XMAX, COMPOUND_W, -2.2, ft_to_arch(COMPOUND_W - PAD_XMAX))
    add_arch_dim_h_dxf(0, COMPOUND_W, -4.0, ft_to_arch(COMPOUND_W))

    # Left
    add_arch_dim_v_dxf(-2.2, 0, TOWER_CY, ft_to_arch(TOWER_CY))
    add_arch_dim_v_dxf(-2.2, TOWER_CY, COMPOUND_H, ft_to_arch(COMPOUND_H - TOWER_CY))
    add_arch_dim_v_dxf(-4.0, 0, COMPOUND_H, ft_to_arch(COMPOUND_H))

    # Right
    add_arch_dim_v_dxf(COMPOUND_W + 2.2, 0, PAD_YMIN, ft_to_arch(PAD_YMIN))
    add_arch_dim_v_dxf(COMPOUND_W + 2.2, PAD_YMIN, PAD_YMAX, ft_to_arch(PAD_H))
    add_arch_dim_v_dxf(COMPOUND_W + 2.2, PAD_YMAX, COMPOUND_H, ft_to_arch(COMPOUND_H - PAD_YMAX))
    add_arch_dim_v_dxf(COMPOUND_W + 4.0, 0, COMPOUND_H, ft_to_arch(COMPOUND_H))

    # Top
    add_arch_dim_h_dxf(0, GATE_X1, COMPOUND_H + 4.2, ft_to_arch(GATE_X1))
    add_arch_dim_h_dxf(GATE_X1, GATE_X2, COMPOUND_H + 4.2, ft_to_arch(GATE_W))
    add_arch_dim_h_dxf(GATE_X2, COMPOUND_W, COMPOUND_H + 4.2, ft_to_arch(GATE_EAST))

    # 7. CALLOUT ANNOTATIONS
    msp.add_text("Monopole\n65.50'", height=0.40, dxfattribs={'layer': 'TEXT', 'color': 7}).set_placement((TOWER_CX + 3.8, TOWER_CY + 4.8))
    msp.add_text("Existing ICE bridge", height=0.35, dxfattribs={'layer': 'TEXT', 'color': 7}).set_placement((TRAY_P1_TOP[0] + 1.5, TRAY_P1_TOP[1] + 4.5))
    msp.add_text("Existing Palisade Fence", height=0.35, dxfattribs={'layer': 'TEXT', 'color': 7}).set_placement((COMPOUND_W - 8.0, COMPOUND_H - 2.8))
    msp.add_text("Meter Bank & Power Box", height=0.35, dxfattribs={'layer': 'TEXT', 'color': 7}).set_placement((POW_D_XMAX + 2.5, POW_D_YMAX + 2.5))
    msp.add_text("GPS", height=0.30, dxfattribs={'layer': 'TEXT', 'color': 7}).set_placement((GPS_1[0] + 1.2, GPS_1[1] - 0.5))

    doc.saveas(filename)
    print(f"Client-Style DXF saved to: {filename}")


if __name__ == "__main__":
    print("Starting Client-Style CAD Generation Pipeline...")
    render_client_style_viewport(CLIENT_STYLE_PNG)
    render_full_sheet(CLIENT_STYLE_PNG, FULL_SHEET_PNG)
    build_client_dxf(DXF_OUT)
    print("All client deliverables compiled successfully!")
