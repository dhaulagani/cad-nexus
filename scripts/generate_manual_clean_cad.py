r"""
Professional Manual-Style 2D CAD Site Map & Existing Tower Detail Generator
Clean CAD Drafting Engine (Replacing rough auto-trace with crisp geometric primitives & multi-color layers)

Site: US1051671_Blue Diamond
Coordinates: 39.196442 N, -114.855244 W (Existing Tower)
Registered to 2K Reference Image: Map_Location.png_2K_20261009192633.jpg

Key Features:
- True CAD Primitives: Smooth Lines, Arcs, Orthogonal Rectangles, True Circles
- Dedicated Layering with Distinct Colors for each Object Type (AIA/NCS Standard)
- Clear Differentiation: MAIN ROAD (Asphalt Highway) vs STREET ROAD (Off-Road / Dirt Road)
- Detailed Existing Monopole Tower & Compound Layout (Detail A Focus View)
- Architecture-Grade Surrounding Buildings & Outbuildings
- Environmental Landscape Vegetation (Riparian Stands & Individual Tree Canopies)
- Official Sheet Border, Title Block, Legend Table, North Arrow & Dual Scale Bars
"""

import os
import math
import numpy as np
from PIL import Image
import ezdxf
from ezdxf import colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# Paths
INPUT_2K_PATH = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\RAW\Map_Location.png_2K_20261009192633.jpg"
OUTPUT_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final"
DXF_PATH = os.path.join(OUTPUT_DIR, "Map_Location_2D.dxf")
PREVIEW_PATH = os.path.join(OUTPUT_DIR, "Map_Location_CAD_2D.png")
DETAIL_PATH = os.path.join(OUTPUT_DIR, "Tower_Site_Detail_CAD.png")
COMPARISON_PATH = os.path.join(OUTPUT_DIR, "Map_Location_Comparison.png")

print(f"Loading reference 2K image: {INPUT_2K_PATH}")
im_ref = Image.open(INPUT_2K_PATH)
w_px, h_px = im_ref.size
print(f"Reference Image Size: {w_px} x {h_px}")

# Georeferencing & Scale
# Tower center in 2K image reference: (294.0, 1025.0)
PIN_X, PIN_Y = 294.0, 1025.0
LAT_DEG = 39.196442
LONG_DEG = -114.855244

# 1 CAD unit = 1 foot (US Survey Feet)
# In 2K image: 1 px = ~1.460 ft = 0.445 m
FT_PER_PX = 1.4598
SCALE_FT = FT_PER_PX

def to_cad(px_x, px_y):
    """Origin (0,0) at Existing Tower Center. +X=East, +Y=North."""
    x = (px_x - PIN_X) * SCALE_FT
    y = (PIN_Y - px_y) * SCALE_FT
    return (float(x), float(y))

def to_cad_list(pts_px):
    return [to_cad(p[0], p[1]) for p in pts_px]

def offset_line(pts_cad, dist):
    res = []
    n = len(pts_cad)
    for i in range(n):
        if i == 0:
            dx = pts_cad[1][0] - pts_cad[0][0]
            dy = pts_cad[1][1] - pts_cad[0][1]
        elif i == n - 1:
            dx = pts_cad[n-1][0] - pts_cad[n-2][0]
            dy = pts_cad[n-1][1] - pts_cad[n-2][1]
        else:
            dx = pts_cad[i+1][0] - pts_cad[i-1][0]
            dy = pts_cad[i+1][1] - pts_cad[i-1][1]
        L = math.hypot(dx, dy)
        if L < 1e-4:
            continue
        nx = -dy / L
        ny = dx / L
        res.append((pts_cad[i][0] + nx * dist, pts_cad[i][1] + ny * dist))
    return res

# ==================== 1. GEOMETRIC ROAD SYSTEM ====================
# A. MAIN ROAD (State Route / Highway US-93 - Paved Asphalt)
# Smooth spline-fitted centerline
hw_cl_px = [
    (2028, 0), (2045, 80), (2075, 160), (2110, 240), (2148, 320),
    (2188, 400), (2230, 480), (2275, 560), (2322, 640), (2370, 720),
    (2420, 800), (2472, 880),
    (2490, 930), # Turnout Intersection to Access Street
    (2525, 960), (2580, 1040), (2635, 1120), (2688, 1200), (2735, 1280),
    (2752, 1315)
]
HW_WIDTH_FT = 30.0 # Standard Two-Lane 12' lanes + 3' paved shoulders = 30'
hw_cl_cad = to_cad_list(hw_cl_px)
hw_left_cad = offset_line(hw_cl_cad, HW_WIDTH_FT / 2.0)
hw_right_cad = offset_line(hw_cl_cad, -HW_WIDTH_FT / 2.0)
hw_shld_l_cad = offset_line(hw_cl_cad, HW_WIDTH_FT / 2.0 + 6.0) # 6' gravel shoulder
hw_shld_r_cad = offset_line(hw_cl_cad, -(HW_WIDTH_FT / 2.0 + 6.0))

# B. STREET ROAD (Off-Road / Dirt Road - Graded Unpaved Roads)
DIRT_WIDTH_FT = 16.0 # Standard 16 ft wide unpaved access corridor

# 1. Primary Access Street (From Highway Turnout to Existing Tower)
dirt_main_cl_px = [
    (2490, 930), # Turnout intersection with Highway US-93
    (2340, 935),
    (2115, 932),
    (1885, 922),
    (1635, 915),
    (1395, 908), # Junction with North-South residential loop
    (1165, 902),
    (968, 912),
    (750, 926),
    (520, 942),
    (345, 950),
    (305, 960),  # Turn South towards existing tower
    (296, 995),
    (294, 1025)  # Existing Tower Compound Gate
]
dirt_main_cl_cad = to_cad_list(dirt_main_cl_px)
dirt_main_l_cad = offset_line(dirt_main_cl_cad, DIRT_WIDTH_FT / 2.0)
dirt_main_r_cad = offset_line(dirt_main_cl_cad, -DIRT_WIDTH_FT / 2.0)

# 2. Western Dirt Street (North-South street passing directly in front of Tower Gate)
dirt_west_cl_px = [
    (305, 280), (300, 465), (298, 650), (298, 835),
    (305, 960),
    (294, 1025), # Passing Existing Tower Gate
    (288, 1170), (280, 1340)
]
dirt_west_cl_cad = to_cad_list(dirt_west_cl_px)
dirt_west_l_cad = offset_line(dirt_west_cl_cad, DIRT_WIDTH_FT / 2.0)
dirt_west_r_cad = offset_line(dirt_west_cl_cad, -DIRT_WIDTH_FT / 2.0)

# 3. North Residential Street Loop
dirt_north_cl_px = [
    (1395, 908), (1385, 765), (1365, 615), (1310, 465),
    (1215, 365), (1070, 300), (895, 310), (790, 390),
    (812, 520), (865, 670), (925, 800), (968, 912)
]
dirt_north_cl_cad = to_cad_list(dirt_north_cl_px)
dirt_north_l_cad = offset_line(dirt_north_cl_cad, 7.0)
dirt_north_r_cad = offset_line(dirt_north_cl_cad, -7.0)

# 4. South Residential Street Loop
dirt_south_cl_px = [
    (1395, 908), (1405, 1025), (1375, 1155), (1270, 1250),
    (1100, 1260), (955, 1175), (895, 1045), (750, 926)
]
dirt_south_cl_cad = to_cad_list(dirt_south_cl_px)

# 5. Highway Frontage Dirt Track
dirt_front_cl_px = [
    (2100, 75), (2165, 300), (2250, 560), (2345, 785),
    (2490, 930), (2560, 1100), (2630, 1310)
]
dirt_front_cl_cad = to_cad_list(dirt_front_cl_px)

# 6. Private Residential Driveways
driveways_2k_px = [
    [(1310, 465), (1290, 428), (1275, 410)], # North Residence
    [(895, 310), (885, 355), (865, 400)],    # West Residence
    [(1365, 615), (1385, 570), (1405, 525)], # Trailer
    [(1165, 902), (1165, 850), (1165, 800)], # South Residence
    [(305, 960), (315, 955), (335, 950)]     # Neighbor structure north of tower
]
driveways_cad = [to_cad_list(dw) for dw in driveways_2k_px]

# Total Access Distance
total_dist_ft = 0.0
for i in range(len(dirt_main_cl_cad) - 1):
    total_dist_ft += math.hypot(dirt_main_cl_cad[i+1][0] - dirt_main_cl_cad[i][0], dirt_main_cl_cad[i+1][1] - dirt_main_cl_cad[i][1])

# ==================== 2. SURROUNDING BUILDINGS (CRISP ORTHOGONAL POLYGONS) ====================
buildings_data = [
    {
        "name": "EXISTING NORTH RESIDENCE",
        "pts": [(1270, 405), (1350, 405), (1350, 510), (1270, 510), (1270, 405)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING WORKSHOP / BARN",
        "pts": [(1075, 437), (1120, 437), (1120, 517), (1075, 517), (1075, 437)],
        "type": "BARN / WORKSHOP"
    },
    {
        "name": "EXISTING WEST RESIDENCE",
        "pts": [(855, 400), (938, 400), (938, 458), (855, 458), (855, 400)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING MOBILE HOME / TRAILER",
        "pts": [(1400, 525), (1432, 525), (1432, 627), (1400, 627), (1400, 525)],
        "type": "MOBILE HOME"
    },
    {
        "name": "OUTBUILDING / SHED",
        "pts": [(853, 506), (886, 506), (886, 565), (853, 565), (853, 506)],
        "type": "SHED"
    },
    {
        "name": "EXISTING RESIDENCE / GARAGE",
        "pts": [(1223, 584), (1256, 584), (1256, 640), (1223, 640), (1223, 584)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING SOUTH RESIDENCE",
        "pts": [(1165, 798), (1208, 798), (1208, 832), (1165, 832), (1165, 798)],
        "type": "RESIDENCE"
    },
    {
        "name": "SOUTH OUTBUILDING",
        "pts": [(1283, 1152), (1318, 1152), (1318, 1180), (1283, 1180), (1283, 1152)],
        "type": "SHED"
    },
    {
        "name": "SOUTH SHED",
        "pts": [(1177, 1178), (1216, 1178), (1216, 1196), (1177, 1196), (1177, 1178)],
        "type": "SHED"
    },
    {
        "name": "NEIGHBOR STRUCTURE",
        "pts": [(320, 948), (358, 948), (358, 992), (320, 992), (320, 948)],
        "type": "SHED"
    },
    {
        "name": "NEIGHBOR OUTBUILDING",
        "pts": [(350, 822), (388, 822), (388, 854), (350, 854), (350, 822)],
        "type": "SHED"
    }
]

# ==================== 3. ENVIRONMENTAL VEGETATION & TERRAIN ====================
veg_stands_2k_px = [
    # 1. Lowry Canyon Wash Dense Riparian Stand (NW)
    [(60, 75), (250, 112), (460, 140), (665, 168), (875, 205), (935, 298), (790, 372), (580, 335), (330, 260), (165, 186), (60, 75)],
    # 2. North Residential Yard Tree Cluster
    [(1250, 372), (1375, 372), (1500, 447), (1540, 595), (1455, 670), (1330, 632), (1205, 558), (1205, 447), (1250, 372)],
    # 3. East Property Boundary Tree & Shrub Line
    [(1580, 484), (1725, 521), (1745, 670), (1600, 632), (1580, 484)],
    # 4. South Property Dense Shrub Area
    [(1685, 1210), (1975, 1190), (2120, 1302), (1915, 1395), (1705, 1376), (1685, 1210)],
    # 5. Southeast Hill Shrub Stand
    [(2455, 1265), (2705, 1284), (2725, 1450), (2500, 1432), (2455, 1265)],
    # 6. Southwest Canyon Rim Stand
    [(125, 595), (230, 632), (240, 781), (145, 818), (125, 595)]
]
veg_stands_cad = [to_cad_list(v) for v in veg_stands_2k_px]

# Landscape Trees
tree_centroids_cad = []
for px_t, py_t, r_t in [
    (1230, 380, 9.5), (1280, 360, 11.0), (1350, 350, 8.5), (1420, 380, 10.0),
    (1460, 450, 12.0), (1480, 530, 9.0), (1450, 600, 10.5), (1380, 650, 8.0),
    (1300, 640, 11.5), (1220, 610, 9.5), (1190, 520, 8.5), (1210, 440, 10.0),
    (830, 380, 8.0), (870, 360, 9.5), (940, 370, 10.5), (960, 440, 9.0),
    (920, 480, 8.5), (850, 480, 11.0), (810, 430, 9.0),
    (1140, 770, 8.5), (1190, 760, 10.0), (1240, 780, 9.0), (1230, 850, 11.0),
    (1150, 850, 9.5), (1120, 810, 8.0),
    (1620, 500, 12.0), (1670, 520, 10.5), (1720, 550, 9.0), (1700, 620, 11.0),
    (720, 360, 9.5), (650, 320, 11.0), (550, 300, 10.0), (450, 270, 8.5),
    (380, 240, 12.0), (280, 200, 10.5), (180, 150, 9.0), (100, 100, 11.5),
    (240, 900, 8.0), (260, 930, 9.0), (360, 920, 10.0), (380, 960, 8.5),
    (260, 1080, 9.5), (240, 1130, 10.5), (320, 1120, 8.5), (350, 1060, 9.0)
]:
    cx_cad, cy_cad = to_cad(px_t, py_t)
    tree_centroids_cad.append((cx_cad, cy_cad, r_t))

# Natural Drainage Wash
canyon_wash_2k_px = [
    [(20, 55), (165, 120), (350, 168), (560, 195), (770, 215), (980, 225)],
    [(250, 28), (435, 84), (645, 120), (855, 140), (1060, 158)]
]
canyon_wash_cad = [to_cad_list(w) for w in canyon_wash_2k_px]

# ==================== 4. EXISTING TOWER & COMPOUND (PRECISE PARAMETRIC CAD) ====================
POLE_BASE_DIA_FT = 4.0
POLE_TOP_DIA_FT = 2.0
CAISSON_DIA_FT = 8.0
FENCE_WIDTH_FT = 40.0
FENCE_DEPTH_FT = 40.0

comp_x0, comp_y0 = -15.0, -20.0
comp_x1, comp_y1 = comp_x0 + FENCE_WIDTH_FT, comp_y0 + FENCE_DEPTH_FT
compound_fence_cad = [
    (comp_x0, comp_y0), (comp_x1, comp_y0), (comp_x1, comp_y1),
    (comp_x0, comp_y1), (comp_x0, comp_y0)
]

pad_x0, pad_y0 = 6.0, -14.0
equip_pad_cad = [
    (pad_x0, pad_y0), (pad_x0 + 14.0, pad_y0),
    (pad_x0 + 14.0, pad_y0 + 22.0), (pad_x0, pad_y0 + 22.0), (pad_x0, pad_y0)
]
cab1_cad = [(pad_x0 + 1.5, pad_y0 + 2.0), (pad_x0 + 6.0, pad_y0 + 2.0), (pad_x0 + 6.0, pad_y0 + 7.0), (pad_x0 + 1.5, pad_y0 + 7.0), (pad_x0 + 1.5, pad_y0 + 2.0)]
cab2_cad = [(pad_x0 + 7.5, pad_y0 + 2.0), (pad_x0 + 12.0, pad_y0 + 2.0), (pad_x0 + 12.0, pad_y0 + 7.0), (pad_x0 + 7.5, pad_y0 + 7.0), (pad_x0 + 7.5, pad_y0 + 2.0)]
telco_rack_cad = [(pad_x0 + 2.0, pad_y0 + 11.0), (pad_x0 + 12.0, pad_y0 + 11.0), (pad_x0 + 12.0, pad_y0 + 14.0), (pad_x0 + 2.0, pad_y0 + 14.0), (pad_x0 + 2.0, pad_y0 + 11.0)]
ice_bridge_cad = [(0.0, 0.0), (pad_x0 + 3.0, 0.0)]
gate_p1 = (comp_x0, comp_y0 + 14.0)
gate_p2 = (comp_x0, comp_y0 + 26.0)

apron_cad = [
    (comp_x0, comp_y0 + 8.0), (comp_x0 - 25.0, comp_y0 + 5.0),
    (comp_x0 - 25.0, comp_y0 + 35.0), (comp_x0, comp_y0 + 32.0), (comp_x0, comp_y0 + 8.0)
]

# ==================== 5. GENERATE PROFESSIONAL CAD DXF (MULTI-COLOR LAYERING) ====================
doc = ezdxf.new(dxfversion="R2018")
doc.header["$INSUNITS"] = 2 # US Survey Feet

# Professional Multi-Color Layering Schema (Distinct Color per Object Type)
layer_specs = [
    # Layer Name, ACI Color, Lineweight (mm*100), Linetype, Description
    ("C-ROAD-MAIN-ASPH", colors.RED, 50, "Continuous", "MAIN ROAD Pavement Edge (Asphalt Highway)"),
    ("C-ROAD-MAIN-CL", colors.YELLOW, 35, "DASHED", "MAIN ROAD Centerline Striping"),
    ("C-ROAD-MAIN-SHLD", colors.GRAY, 25, "DASHED", "MAIN ROAD Paved Shoulder"),
    ("C-ROAD-DIRT-EDGE", colors.CYAN, 40, "Continuous", "STREET ROAD (Dirt / Off-Road) Edges"),
    ("C-ROAD-DIRT-CL", colors.CYAN, 30, "DASHDOT", "STREET ROAD (Dirt / Off-Road) Centerline"),
    ("C-ROAD-DIRT-TRCK", colors.LIGHT_GRAY, 20, "Continuous", "Local Residential Dirt Tracks"),
    ("C-ROAD-DRIV-WAY", colors.LIGHT_GRAY, 20, "DASHED", "Private Residential Driveways"),
    ("C-BLDG-EXST", colors.BLUE, 35, "Continuous", "Existing Surrounding Buildings Footprints"),
    ("C-BLDG-TEXT", colors.CYAN, 20, "Continuous", "Building Function Labels"),
    ("C-TOWR-POLE", colors.MAGENTA, 60, "Continuous", "Existing Monopole Tower Steel Pole"),
    ("C-TOWR-FNDN", colors.WHITE, 40, "Continuous", "Existing Concrete Foundation & Pad"),
    ("C-TOWR-EQUP", colors.BLUE, 30, "Continuous", "Existing BTS Cabinets & Telco Rack"),
    ("C-TOWR-FENC", colors.RED, 40, "Continuous", "Existing Compound Chain-Link Fence & Gate"),
    ("C-TOWR-APRN", colors.GREEN, 25, "DASHED", "Existing Gravel Turnaround Apron"),
    ("C-TOPO-VEGT", colors.GREEN, 25, "Continuous", "Dense Shrub & Brush Stands Boundary"),
    ("C-TOPO-TREE", colors.GREEN, 25, "Continuous", "Individual Landscape Tree Canopies"),
    ("C-TOPO-WASH", colors.CYAN, 25, "DASHED", "Lowry Canyon Natural Drainage Wash"),
    ("C-ANNO-TEXT", colors.WHITE, 25, "Continuous", "General Notes & Callouts"),
    ("C-ANNO-DIMS", colors.CYAN, 20, "Continuous", "Dimension Lines & Leaders"),
    ("C-ANNO-LEGD", colors.WHITE, 25, "Continuous", "Road Classification Legend"),
    ("C-ANNO-NORT", colors.YELLOW, 35, "Continuous", "North Arrow & Graphic Scales"),
    ("C-TTLB-BORR", colors.WHITE, 50, "Continuous", "Sheet Border & Title Block")
]

for l_name, l_col, l_lw, l_type, l_desc in layer_specs:
    lyr = doc.layers.add(l_name, color=l_col)
    lyr.lineweight = l_lw
    lyr.linetype = l_type

msp = doc.modelspace()

# Add Main Road
msp.add_lwpolyline(hw_cl_cad, dxfattribs={"layer": "C-ROAD-MAIN-CL", "linetype": "DASHED"})
msp.add_lwpolyline(hw_left_cad, dxfattribs={"layer": "C-ROAD-MAIN-ASPH"})
msp.add_lwpolyline(hw_right_cad, dxfattribs={"layer": "C-ROAD-MAIN-ASPH"})
msp.add_lwpolyline(hw_shld_l_cad, dxfattribs={"layer": "C-ROAD-MAIN-SHLD", "linetype": "DASHED"})
msp.add_lwpolyline(hw_shld_r_cad, dxfattribs={"layer": "C-ROAD-MAIN-SHLD", "linetype": "DASHED"})

# Add Street Road (Dirt / Off-Road)
msp.add_lwpolyline(dirt_main_cl_cad, dxfattribs={"layer": "C-ROAD-DIRT-CL", "linetype": "DASHDOT"})
msp.add_lwpolyline(dirt_main_l_cad, dxfattribs={"layer": "C-ROAD-DIRT-EDGE"})
msp.add_lwpolyline(dirt_main_r_cad, dxfattribs={"layer": "C-ROAD-DIRT-EDGE"})

msp.add_lwpolyline(dirt_west_cl_cad, dxfattribs={"layer": "C-ROAD-DIRT-CL", "linetype": "DASHDOT"})
msp.add_lwpolyline(dirt_west_l_cad, dxfattribs={"layer": "C-ROAD-DIRT-EDGE"})
msp.add_lwpolyline(dirt_west_r_cad, dxfattribs={"layer": "C-ROAD-DIRT-EDGE"})

for seg in [dirt_north_cl_cad, dirt_south_cl_cad, dirt_front_cl_cad]:
    msp.add_lwpolyline(seg, dxfattribs={"layer": "C-ROAD-DIRT-TRCK"})

for dw in driveways_cad:
    msp.add_lwpolyline(dw, dxfattribs={"layer": "C-ROAD-DRIV-WAY", "linetype": "DASHED"})

# Add Surrounding Buildings
for b in buildings_data:
    b_cad = to_cad_list(b["pts"])
    msp.add_lwpolyline(b_cad, close=True, dxfattribs={"layer": "C-BLDG-EXST"})
    cx = sum(p[0] for p in b_cad[:-1]) / (len(b_cad) - 1)
    cy = sum(p[1] for p in b_cad[:-1]) / (len(b_cad) - 1)
    msp.add_text(b["type"], dxfattribs={"layer": "C-BLDG-TEXT", "height": 11.0, "insert": (cx - 30.0, cy - 5.0)})

# Add Vegetation & Trees
for v in veg_stands_cad:
    msp.add_lwpolyline(v, close=True, dxfattribs={"layer": "C-TOPO-VEGT"})

for tx, ty, tr in tree_centroids_cad:
    msp.add_circle((tx, ty), radius=tr, dxfattribs={"layer": "C-TOPO-TREE"})
    msp.add_circle((tx, ty), radius=tr * 0.4, dxfattribs={"layer": "C-TOPO-TREE"})

for w in canyon_wash_cad:
    msp.add_lwpolyline(w, dxfattribs={"layer": "C-TOPO-WASH", "linetype": "DASHED"})

# Add Existing Tower & Compound (True Geometric Entities)
msp.add_circle((0.0, 0.0), radius=CAISSON_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-FNDN"})
msp.add_circle((0.0, 0.0), radius=POLE_BASE_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_circle((0.0, 0.0), radius=POLE_TOP_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_line((-8.0, 0.0), (8.0, 0.0), dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_line((0.0, -8.0), (0.0, 8.0), dxfattribs={"layer": "C-TOWR-POLE"})

msp.add_lwpolyline(compound_fence_cad, close=True, dxfattribs={"layer": "C-TOWR-FENC"})
msp.add_lwpolyline(equip_pad_cad, close=True, dxfattribs={"layer": "C-TOWR-FNDN"})
msp.add_lwpolyline(cab1_cad, close=True, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(cab2_cad, close=True, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(telco_rack_cad, close=True, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_line(ice_bridge_cad[0], ice_bridge_cad[1], dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(apron_cad, close=True, dxfattribs={"layer": "C-TOWR-APRN", "linetype": "DASHED"})

# Gate Representation
msp.add_line(gate_p1, (gate_p1[0] - 10.0, gate_p1[1]), dxfattribs={"layer": "C-TOWR-FENC", "linetype": "DASHED"})
msp.add_line(gate_p2, (gate_p2[0] - 10.0, gate_p2[1]), dxfattribs={"layer": "C-TOWR-FENC", "linetype": "DASHED"})

# Annotations & Text
msp.add_text("EXISTING CONSTRUCTED MONOPOLE TOWER (120' AGL)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 18.0, "insert": (-160.0, 40.0)})
msp.add_text("COORDINATES: 39 11'47.2\"N, 114 51'18.9\"W", dxfattribs={"layer": "C-ANNO-TEXT", "height": 14.0, "insert": (-160.0, 18.0)})
msp.add_text("LAT: 39.196442 N | LONG: -114.855244 W", dxfattribs={"layer": "C-ANNO-TEXT", "height": 14.0, "insert": (-160.0, -4.0)})
msp.add_text("STATE ROUTE / HIGHWAY US-93 (MAIN ROAD - PAVED ASPHALT)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 22.0, "insert": (3300.0, 200.0), "rotation": -67.0})
msp.add_text(f"STREET ROAD (OFF-ROAD / DIRT ROAD) - ACCESS ROUTE: {total_dist_ft:.0f} FT ({total_dist_ft*0.3048:.0f} M)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 16.0, "insert": (800.0, 210.0), "rotation": -5.0})

# Save DXF
doc.saveas(DXF_PATH)
print(f"Master Clean DXF saved to: {DXF_PATH}")

# ==================== 6. GENERATE HIGH-END ARCHITECTURAL PRESENTATION SHEET (PNG) ====================
fig = plt.figure(figsize=(26, 16), dpi=200, facecolor="#14171c")

ax_main = fig.add_axes([0.035, 0.05, 0.63, 0.90], facecolor="#0e1117")
ax_detail = fig.add_axes([0.685, 0.47, 0.285, 0.48], facecolor="#0e1117")
ax_legend = fig.add_axes([0.685, 0.23, 0.285, 0.22], facecolor="#161b22")
ax_title = fig.add_axes([0.685, 0.05, 0.285, 0.16], facecolor="#161b22")

# ==================== VIEWPORT 1: MAIN SITE LOCATION MAP ====================
ax_main.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.6, alpha=0.8)

# 1. Environmental Vegetation Stands
for idx, v in enumerate(veg_stands_cad):
    poly_veg = patches.Polygon(v, facecolor="#14532d", edgecolor="#22c55e", lw=1.4, ls="--", alpha=0.35, zorder=1)
    ax_main.add_patch(poly_veg)
    if idx == 0:
        ax_main.text(v[3][0], v[3][1] + 20, "DENSE BRUSH / WASH VEGETATION", color="#22c55e", fontsize=8.5, weight="bold", zorder=2)

# Individual Landscape Tree Canopies
for tx, ty, tr in tree_centroids_cad:
    circ_outer = plt.Circle((tx, ty), tr, facecolor="#15803d", edgecolor="#4ade80", lw=0.8, alpha=0.55, zorder=2)
    circ_inner = plt.Circle((tx, ty), tr * 0.4, facecolor="#22c55e", edgecolor="#ffffff", lw=0.5, alpha=0.8, zorder=3)
    ax_main.add_patch(circ_outer)
    ax_main.add_patch(circ_inner)

# Lowry Canyon Wash drainage lines
for w in canyon_wash_cad:
    ax_main.plot([p[0] for p in w], [p[1] for p in w], color="#06b6d4", lw=2.0, ls=":", zorder=2, label="Lowry Canyon Natural Wash" if w==canyon_wash_cad[0] else None)

# 2. Surrounding Buildings (Crisp Blue Rectangles with White Edges)
for b in buildings_data:
    b_cad = to_cad_list(b["pts"])
    xs = [p[0] for p in b_cad]
    ys = [p[1] for p in b_cad]
    ax_main.fill(xs, ys, color="#1d4ed8", alpha=0.55, zorder=4)
    ax_main.plot(xs, ys, color="#60a5fa", lw=2.0, zorder=5)
    cx = sum(xs[:-1]) / (len(xs) - 1)
    cy = sum(ys[:-1]) / (len(ys) - 1)
    ax_main.text(cx, cy + 18, b["type"], color="#93c5fd", fontsize=8, weight="bold", ha="center", zorder=6)

# Private Driveways
for dw in driveways_cad:
    ax_main.plot([p[0] for p in dw], [p[1] for p in dw], color="#94a3b8", lw=1.6, ls="--", zorder=3, label="Private Driveway" if dw==driveways_cad[0] else None)

# 3. Roads
# MAIN ROAD (Highway US-93 - Asphalt)
ax_main.fill(
    [p[0] for p in hw_left_cad] + [p[0] for p in reversed(hw_right_cad)],
    [p[1] for p in hw_left_cad] + [p[1] for p in reversed(hw_right_cad)],
    color="#334155", alpha=0.95, zorder=3
)
ax_main.plot([p[0] for p in hw_cl_cad], [p[1] for p in hw_cl_cad], color="#f59e0b", lw=2.8, ls="--", zorder=4, label="MAIN ROAD Centerline (Highway US-93)")
ax_main.plot([p[0] for p in hw_left_cad], [p[1] for p in hw_left_cad], color="#e2e8f0", lw=2.4, zorder=4, label="MAIN ROAD Pavement Edge (Asphalt)")
ax_main.plot([p[0] for p in hw_right_cad], [p[1] for p in hw_right_cad], color="#e2e8f0", lw=2.4, zorder=4)
ax_main.plot([p[0] for p in hw_shld_l_cad], [p[1] for p in hw_shld_l_cad], color="#94a3b8", lw=1.3, ls=":", zorder=3, label="MAIN ROAD Paved Shoulder")
ax_main.plot([p[0] for p in hw_shld_r_cad], [p[1] for p in hw_shld_r_cad], color="#94a3b8", lw=1.3, ls=":", zorder=3)

# STREET ROAD (Off-Road / Dirt Road)
# Main Access Dirt Road
ax_main.fill(
    [p[0] for p in dirt_main_l_cad] + [p[0] for p in reversed(dirt_main_r_cad)],
    [p[1] for p in dirt_main_l_cad] + [p[1] for p in reversed(dirt_main_r_cad)],
    color="#78350f", alpha=0.40, zorder=3
)
ax_main.plot([p[0] for p in dirt_main_cl_cad], [p[1] for p in dirt_main_cl_cad], color="#38bdf8", lw=2.4, ls="-.", zorder=4, label="STREET ROAD Centerline (Dirt/Off-Road)")
ax_main.plot([p[0] for p in dirt_main_l_cad], [p[1] for p in dirt_main_l_cad], color="#38bdf8", lw=1.8, ls="-", zorder=4, label="STREET ROAD Limits (16' Width)")
ax_main.plot([p[0] for p in dirt_main_r_cad], [p[1] for p in dirt_main_r_cad], color="#38bdf8", lw=1.8, ls="-", zorder=4)

# Western Dirt Street
ax_main.fill(
    [p[0] for p in dirt_west_l_cad] + [p[0] for p in reversed(dirt_west_r_cad)],
    [p[1] for p in dirt_west_l_cad] + [p[1] for p in reversed(dirt_west_r_cad)],
    color="#78350f", alpha=0.40, zorder=3
)
ax_main.plot([p[0] for p in dirt_west_cl_cad], [p[1] for p in dirt_west_cl_cad], color="#38bdf8", lw=2.4, ls="-.", zorder=4)
ax_main.plot([p[0] for p in dirt_west_l_cad], [p[1] for p in dirt_west_l_cad], color="#38bdf8", lw=1.8, ls="-", zorder=4)
ax_main.plot([p[0] for p in dirt_west_r_cad], [p[1] for p in dirt_west_r_cad], color="#38bdf8", lw=1.8, ls="-", zorder=4)

# Other Dirt Tracks
for seg in [dirt_north_cl_cad, dirt_south_cl_cad, dirt_front_cl_cad]:
    ax_main.plot([p[0] for p in seg], [p[1] for p in seg], color="#64748b", lw=1.5, ls="-", zorder=3, label="Local Dirt Track" if seg==dirt_north_cl_cad else None)

# 4. Existing Tower Compound Marker & Detail Callout
comp_rect = patches.Rectangle((comp_x0, comp_y0), FENCE_WIDTH_FT, FENCE_DEPTH_FT, facecolor="#ef4444", edgecolor="#ef4444", alpha=0.45, zorder=6)
ax_main.add_patch(comp_rect)
ax_main.plot([p[0] for p in compound_fence_cad], [p[1] for p in compound_fence_cad], color="#ef4444", lw=2.4, zorder=7, label="Existing Compound Fence (40'x40')")
ax_main.plot(0, 0, marker="o", markersize=10, color="#ec4899", markeredgecolor="#ffffff", markeredgewidth=2.0, zorder=8, label="Existing Monopole Tower")

# Focus Box for Detail A
f_margin = 90.0
ax_main.add_patch(patches.Rectangle((-f_margin, -f_margin), 2*f_margin, 2*f_margin, edgecolor="#ec4899", facecolor="none", lw=2.2, ls="--", zorder=9))
ax_main.text(-f_margin + 5, f_margin + 12, "SEE DETAIL A (ENLARGEMENT)", color="#ec4899", fontsize=10, weight="bold", zorder=10)

ax_main.annotate(
    "EXISTING MONOPOLE TOWER SITE\n"
    "39°11'47.2\"N, 114°51'18.9\"W\n"
    "(SEE DETAIL A ON RIGHT)",
    xy=(0, 0), xytext=(-270, 160),
    arrowprops=dict(facecolor="#ec4899", edgecolor="#ec4899", width=2.2, headwidth=8),
    fontsize=10.5, color="#ffffff", weight="bold",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", edgecolor="#ec4899", lw=1.8),
    zorder=10
)

# Text Callouts
ax_main.text(3280.0, 180.0, "STATE ROUTE / HIGHWAY US-93\n[MAIN ROAD - PAVED ASPHALT]", rotation=-67,
             fontsize=12, color="#f59e0b", weight="bold", ha="center", va="center")
ax_main.text(780.0, 185.0, f"STREET ROAD (OFF-ROAD / DIRT ROAD)\nROUTE: {total_dist_ft:.0f} FT ({total_dist_ft*0.3048:.0f} M) TO EXISTING TOWER",
             rotation=-5, fontsize=10.5, color="#38bdf8", weight="bold", ha="center", va="bottom",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#0f172a", edgecolor="#38bdf8", lw=1.2))
ax_main.text(-25.0, 480.0, "WESTERN STREET ROAD\n(DIRT ROAD / OFF-ROAD)", rotation=88,
             fontsize=10, color="#38bdf8", weight="bold", ha="center")

# North Arrow & Scale Bar
ax_main.annotate("N", xy=(150, 1650), xytext=(150, 1500),
                 arrowprops=dict(facecolor="#eab308", edgecolor="#eab308", width=3.5, headwidth=14),
                 fontsize=18, color="#eab308", weight="heavy", ha="center", va="top")
ax_main.plot([50, 550], [1400, 1400], color="#eab308", lw=3.0)
for d in [0, 100, 250, 500]:
    ax_main.plot([50 + d, 50 + d], [1380, 1420], color="#eab308", lw=1.5)
    ax_main.text(50 + d, 1340, f"{d}'", color="#eab308", fontsize=8.5, ha="center")
ax_main.text(300, 1435, "OVERALL SCALE: 1\" = 250'", color="#eab308", fontsize=9.5, ha="center", weight="bold")

ax_main.set_xlim(-400, 3800)
ax_main.set_ylim(-850, 1750)
ax_main.set_aspect("equal", adjustable="box")
ax_main.set_title("SITE VICINITY MAP (ROADS, STRUCTURES & ENVIRONMENTAL VEGETATION)", color="#ffffff", fontsize=13, weight="bold", pad=12)
ax_main.tick_params(colors="#64748b", labelsize=8.5)
ax_main.set_xlabel("East Offset (Feet, Center at Tower)", color="#64748b", fontsize=9)
ax_main.set_ylabel("North Offset (Feet, Center at Tower)", color="#64748b", fontsize=9)
ax_main.legend(loc="lower left", facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0", fontsize=8.5, framealpha=0.95)

# ==================== VIEWPORT 2: DETAIL A (TOWER SITE FOCUS) ====================
ax_detail.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.6, alpha=0.8)

# Compound Gravel Surface
ax_detail.add_patch(patches.Rectangle((comp_x0, comp_y0), FENCE_WIDTH_FT, FENCE_DEPTH_FT, facecolor="#334155", edgecolor="#ef4444", lw=2.8, zorder=2))
# Apron
ax_detail.add_patch(patches.Polygon(apron_cad, facecolor="#475569", edgecolor="#38bdf8", lw=1.6, ls="--", alpha=0.6, zorder=2))
ax_detail.text(comp_x0 - 14, comp_y0 + 20, "EXISTING GRAVEL\nAPRON & DRIVE", color="#38bdf8", fontsize=8, ha="center", weight="bold")

# Surrounding native shrubs
for dx_s, dy_s in [(-38, -25), (-35, 25), (32, 28), (30, -30), (25, -5)]:
    ax_detail.add_patch(plt.Circle((dx_s, dy_s), 4.5, facecolor="#15803d", edgecolor="#4ade80", lw=0.7, alpha=0.6, zorder=2))

# Western Dirt Street
ax_detail.plot([-25, -25], [-35, 45], color="#38bdf8", lw=2.8, ls="-", zorder=3)
ax_detail.plot([-41, -41], [-35, 45], color="#38bdf8", lw=2.8, ls="-", zorder=3)
ax_detail.plot([-33, -33], [-35, 45], color="#38bdf8", lw=2.0, ls="-.", zorder=3)
ax_detail.text(-33, 38, "WESTERN STREET ROAD\n(DIRT ROAD - 16' WIDE)", color="#38bdf8", fontsize=8.5, weight="bold", ha="center")

# Concrete Pad & Cabinets
ax_detail.add_patch(patches.Rectangle((pad_x0, pad_y0), 14.0, 22.0, facecolor="#94a3b8", edgecolor="#ffffff", lw=2.2, zorder=4))
ax_detail.text(pad_x0 + 7.0, pad_y0 + 18.0, "CONCRETE PAD\n14' x 22'", color="#0f172a", fontsize=7.5, ha="center", weight="bold", zorder=5)

ax_detail.add_patch(patches.Rectangle((pad_x0 + 1.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.3, zorder=5))
ax_detail.add_patch(patches.Rectangle((pad_x0 + 7.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.3, zorder=5))
ax_detail.text(pad_x0 + 3.75, pad_y0 + 4.5, "BTS", color="#ffffff", fontsize=7, ha="center", va="center", weight="bold", zorder=6)
ax_detail.text(pad_x0 + 9.75, pad_y0 + 4.5, "BATT", color="#ffffff", fontsize=7, ha="center", va="center", weight="bold", zorder=6)

ax_detail.add_patch(patches.Rectangle((pad_x0 + 2.0, pad_y0 + 11.0), 10.0, 3.0, facecolor="#0284c7", edgecolor="#ffffff", lw=1.3, zorder=5))
ax_detail.text(pad_x0 + 7.0, pad_y0 + 12.5, "TELCO / POWER RACK", color="#ffffff", fontsize=6.5, ha="center", va="center", weight="bold", zorder=6)

# Ice Bridge
ax_detail.plot([0.0, pad_x0 + 3.0], [0.0, 0.0], color="#f59e0b", lw=3.2, zorder=6)
ax_detail.text(pad_x0 / 2.0, 2.5, "ICE BRIDGE", color="#f59e0b", fontsize=7, ha="center", weight="bold")

# Monopole Tower Foundation & Pole (True Circles)
ax_detail.add_patch(plt.Circle((0, 0), CAISSON_DIA_FT / 2.0, facecolor="#cbd5e1", edgecolor="#ffffff", lw=2.2, zorder=5))
ax_detail.add_patch(plt.Circle((0, 0), POLE_BASE_DIA_FT / 2.0, facecolor="#475569", edgecolor="#ec4899", lw=2.2, zorder=6))
ax_detail.add_patch(plt.Circle((0, 0), POLE_TOP_DIA_FT / 2.0, facecolor="#ec4899", edgecolor="#ffffff", lw=1.6, zorder=7))
ax_detail.plot([-5, 5], [0, 0], color="#ffffff", lw=1.3, zorder=8)
ax_detail.plot([0, 0], [-5, 5], color="#ffffff", lw=1.3, zorder=8)

# Gate
ax_detail.plot([comp_x0, comp_x0 - 8.0], [gate_p1[1], gate_p1[1]], color="#ef4444", lw=2.4, ls="--", zorder=6)
ax_detail.plot([comp_x0, comp_x0 - 8.0], [gate_p2[1], gate_p2[1]], color="#ef4444", lw=2.4, ls="--", zorder=6)
ax_detail.text(comp_x0 - 2.0, (gate_p1[1] + gate_p2[1])/2.0, "12' SWING GATE", color="#ef4444", fontsize=7.5, weight="bold", rotation=90, va="center")

# Dimensions
ax_detail.annotate("", xy=(comp_x0, comp_y1 + 4), xytext=(comp_x1, comp_y1 + 4), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.3))
ax_detail.text((comp_x0 + comp_x1)/2.0, comp_y1 + 6.0, "40'-0\" COMPOUND WIDTH", color="#e2e8f0", fontsize=8, ha="center", weight="bold")

ax_detail.annotate("", xy=(comp_x1 + 4, comp_y0), xytext=(comp_x1 + 4, comp_y1), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.3))
ax_detail.text(comp_x1 + 6.0, (comp_y0 + comp_y1)/2.0, "40'-0\" DEPTH", color="#e2e8f0", fontsize=8, va="center", rotation=-90, weight="bold")

ax_detail.annotate(
    "EXISTING MONOPOLE TOWER\n"
    "- 120'-0\" AGL HEIGHT\n"
    "- 4'-0\" BASE DIA.\n"
    "- 8'-0\" CONC. CAISSON",
    xy=(0, 0), xytext=(-35, -28),
    arrowprops=dict(facecolor="#ec4899", edgecolor="#ec4899", width=1.5, headwidth=6),
    fontsize=8, color="#ffffff", weight="bold",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#ec4899", lw=1.2)
)

ax_detail.set_xlim(-48, 38)
ax_detail.set_ylim(-38, 38)
ax_detail.set_aspect("equal", adjustable="box")
ax_detail.set_title("DETAIL A: EXISTING TOWER LOCATION & COMPOUND (FOCUS PLAN)", color="#ffffff", fontsize=11, weight="bold", pad=8)
ax_detail.tick_params(colors="#64748b", labelsize=8)
ax_detail.set_xlabel("Feet (Center at Existing Tower)", color="#64748b", fontsize=8)

# Detail Scale Bar
ax_detail.plot([-35, 5], [-34, -34], color="#eab308", lw=2.5)
for d in [0, 10, 20, 40]:
    ax_detail.plot([-35 + d, -35 + d], [-35.5, -32.5], color="#eab308", lw=1.2)
    ax_detail.text(-35 + d, -37.5, f"{d}'", color="#eab308", fontsize=7.5, ha="center")
ax_detail.text(-15, -31.5, "DETAIL SCALE: 1\" = 20'", color="#eab308", fontsize=8, ha="center", weight="bold")

# ==================== VIEWPORT 3: LEGEND & CLASSIFICATION ====================
ax_legend.axis("off")
ax_legend.set_xlim(0, 100)
ax_legend.set_ylim(0, 100)

ax_legend.text(4, 90, "MAP SYMBOL LEGEND & CLASSIFICATION", color="#ffffff", fontsize=11, weight="bold")
ax_legend.plot([4, 96], [85, 85], color="#475569", lw=1.2)

# Row 1: MAIN ROAD
ax_legend.plot([5, 18], [72, 72], color="#f59e0b", lw=3.0, ls="--")
ax_legend.plot([5, 18], [75, 75], color="#e2e8f0", lw=2.0)
ax_legend.plot([5, 18], [69, 69], color="#e2e8f0", lw=2.0)
ax_legend.text(22, 72, "MAIN ROAD (HIGHWAY US-93 / STATE ROUTE)", color="#f59e0b", fontsize=8.5, weight="bold", va="center")
ax_legend.text(22, 63, "Paved Asphalt | Width: 30'-0\" | Two-Lane with Paved Shoulders", color="#94a3b8", fontsize=7.5, va="center")

# Row 2: STREET ROAD
ax_legend.plot([5, 18], [50, 50], color="#38bdf8", lw=2.4, ls="-.")
ax_legend.plot([5, 18], [53, 53], color="#38bdf8", lw=1.6)
ax_legend.plot([5, 18], [47, 47], color="#38bdf8", lw=1.6)
ax_legend.text(22, 50, "STREET ROAD (OFF-ROAD / DIRT ROAD)", color="#38bdf8", fontsize=8.5, weight="bold", va="center")
ax_legend.text(22, 41, "Graded Gravel/Dirt | Width: 16'-0\" | Primary Site Access", color="#94a3b8", fontsize=7.5, va="center")

# Row 3: STRUCTURES & VEGETATION
r_bldg = patches.Rectangle((5, 23), 13, 8, facecolor="#1d4ed8", edgecolor="#60a5fa", lw=1.4)
ax_legend.add_patch(r_bldg)
ax_legend.text(22, 27, "EXISTING SURROUNDING BUILDINGS / STRUCTURES", color="#60a5fa", fontsize=8.5, weight="bold", va="center")

# Tree Symbol in Legend
c_veg = plt.Circle((11, 10), 4.5, facecolor="#15803d", edgecolor="#4ade80", lw=1.2)
ax_legend.add_patch(c_veg)
ax_legend.text(22, 10, "ENVIRONMENTAL VEGETATION / TREE CANOPIES", color="#4ade80", fontsize=8.5, weight="bold", va="center")

# ==================== VIEWPORT 4: TITLE BLOCK ====================
ax_title.axis("off")
ax_title.set_xlim(0, 100)
ax_title.set_ylim(0, 100)

ax_title.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], color="#475569", lw=1.5)
ax_title.plot([0, 100], [68, 68], color="#475569", lw=1.0)
ax_title.plot([0, 100], [34, 34], color="#475569", lw=1.0)
ax_title.plot([68, 68], [0, 68], color="#475569", lw=1.0)

ax_title.text(4, 86, "SITE LOCATION MAP (ROADS, STRUCTURES & VEGETATION)", color="#ffffff", fontsize=11, weight="bold")
ax_title.text(4, 74, "MANUAL-DRAFTED CAD QUALITY WITH DEDICATED LAYERING", color="#94a3b8", fontsize=7.5)

ax_title.text(4, 55, "SITE NAME: US1051671_BLUE DIAMOND", color="#ffffff", fontsize=9.5, weight="bold")
ax_title.text(4, 42, "TOWER STATUS: EXISTING CONSTRUCTED (120' MONOPOLE)", color="#ec4899", fontsize=9, weight="bold")

ax_title.text(4, 23, "COORDINATES: 39°11'47.2\"N, 114°51'18.9\"W", color="#e2e8f0", fontsize=8.5)
ax_title.text(4, 10, "LAT: 39.196442° N | LONG: -114.855244° W (WGS84)", color="#94a3b8", fontsize=8)

ax_title.text(84, 52, "SHEET NO.", color="#94a3b8", fontsize=8, ha="center")
ax_title.text(84, 40, "C-101", color="#ffffff", fontsize=16, weight="bold", ha="center")
ax_title.text(84, 22, "REV: 4 (CLEAN CAD)", color="#38bdf8", fontsize=8, ha="center", weight="bold")
ax_title.text(84, 9, "DATE: 2026-10", color="#94a3b8", fontsize=7.5, ha="center")

# Save Presentation Sheet
plt.savefig(PREVIEW_PATH, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Saved complete architectural sheet to: {PREVIEW_PATH}")

# Standalone Detail Plan
fig_detail, ax_d_only = plt.subplots(figsize=(12, 10), dpi=200, facecolor="#14171c")
ax_d_only.set_facecolor("#0e1117")
ax_d_only.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.7)

ax_d_only.add_patch(patches.Rectangle((comp_x0, comp_y0), FENCE_WIDTH_FT, FENCE_DEPTH_FT, facecolor="#1e293b", edgecolor="#ef4444", lw=3.0, zorder=2))
ax_d_only.add_patch(patches.Polygon(apron_cad, facecolor="#334155", edgecolor="#38bdf8", lw=1.8, ls="--", alpha=0.7, zorder=2))

ax_d_only.plot([-25, -25], [-45, 45], color="#38bdf8", lw=3.0, ls="-", zorder=3, label="Western Street Road Edge")
ax_d_only.plot([-41, -41], [-45, 45], color="#38bdf8", lw=3.0, ls="-", zorder=3)
ax_d_only.plot([-33, -33], [-45, 45], color="#38bdf8", lw=2.0, ls="-.", zorder=3, label="Street Road Centerline (Dirt)")

ax_d_only.add_patch(patches.Rectangle((pad_x0, pad_y0), 14.0, 22.0, facecolor="#64748b", edgecolor="#ffffff", lw=2.0, zorder=4))
ax_d_only.add_patch(patches.Rectangle((pad_x0 + 1.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.5, zorder=5))
ax_d_only.add_patch(patches.Rectangle((pad_x0 + 7.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.5, zorder=5))
ax_d_only.add_patch(patches.Rectangle((pad_x0 + 2.0, pad_y0 + 11.0), 10.0, 3.0, facecolor="#0284c7", edgecolor="#ffffff", lw=1.5, zorder=5))

ax_d_only.add_patch(plt.Circle((0, 0), CAISSON_DIA_FT / 2.0, facecolor="#94a3b8", edgecolor="#ffffff", lw=2.0, zorder=5))
ax_d_only.add_patch(plt.Circle((0, 0), POLE_BASE_DIA_FT / 2.0, facecolor="#334155", edgecolor="#ec4899", lw=2.5, zorder=6))
ax_d_only.add_patch(plt.Circle((0, 0), POLE_TOP_DIA_FT / 2.0, facecolor="#ec4899", edgecolor="#ffffff", lw=1.8, zorder=7))
ax_d_only.plot([-6, 6], [0, 0], color="#ffffff", lw=1.5, zorder=8)
ax_d_only.plot([0, 0], [-6, 6], color="#ffffff", lw=1.5, zorder=8)

ax_d_only.plot([0.0, pad_x0 + 3.0], [0.0, 0.0], color="#f59e0b", lw=3.5, zorder=6)
ax_d_only.plot([comp_x0, comp_x0 - 9.0], [gate_p1[1], gate_p1[1]], color="#ef4444", lw=2.5, ls="--", zorder=6)
ax_d_only.plot([comp_x0, comp_x0 - 9.0], [gate_p2[1], gate_p2[1]], color="#ef4444", lw=2.5, ls="--", zorder=6)

ax_d_only.text(0, -18, "EXISTING MONOPOLE TOWER (120' AGL)\nLAT: 39.196442° N, LONG: -114.855244° W\nSITE: US1051671_BLUE DIAMOND",
               color="#ffffff", fontsize=9.5, weight="bold", ha="center",
               bbox=dict(boxstyle="round,pad=0.5", facecolor="#1e293b", edgecolor="#ec4899", lw=1.8))
ax_d_only.text(pad_x0 + 7, pad_y0 + 17, "CONCRETE PAD\n14' x 22'", color="#0f172a", fontsize=8.5, weight="bold", ha="center")
ax_d_only.text(-33, 35, "WESTERN STREET ROAD\n(OFF-ROAD / DIRT ROAD)", color="#38bdf8", fontsize=9.5, weight="bold", ha="center")
ax_d_only.text(comp_x0 - 2, (gate_p1[1] + gate_p2[1])/2.0, "12' SWING GATE", color="#ef4444", fontsize=9, weight="bold", rotation=90, va="center")

ax_d_only.annotate("", xy=(comp_x0, comp_y1 + 4), xytext=(comp_x1, comp_y1 + 4), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.5))
ax_d_only.text((comp_x0 + comp_x1)/2.0, comp_y1 + 6.5, "40'-0\" COMPOUND WIDTH", color="#e2e8f0", fontsize=9, ha="center", weight="bold")

ax_d_only.annotate("", xy=(comp_x1 + 4, comp_y0), xytext=(comp_x1 + 4, comp_y1), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.5))
ax_d_only.text(comp_x1 + 7.0, (comp_y0 + comp_y1)/2.0, "40'-0\" COMPOUND DEPTH", color="#e2e8f0", fontsize=9, va="center", rotation=-90, weight="bold")

ax_d_only.set_xlim(-50, 42)
ax_d_only.set_ylim(-42, 42)
ax_d_only.set_aspect("equal", adjustable="box")
ax_d_only.set_title("EXISTING MONOPOLE TOWER LOCATION & COMPOUND PLAN", color="#ffffff", fontsize=13, weight="bold", pad=12)
ax_d_only.tick_params(colors="#64748b")
ax_d_only.set_xlabel("East Offset (Feet, Center at Tower)", color="#64748b", fontsize=9.5)
ax_d_only.set_ylabel("North Offset (Feet, Center at Tower)", color="#64748b", fontsize=9.5)

plt.tight_layout()
plt.savefig(DETAIL_PATH, dpi=200, bbox_inches="tight")
plt.close(fig_detail)
print(f"Saved standalone tower detail plan to: {DETAIL_PATH}")

# Side-by-side comparison
orig_2k_im = Image.open(INPUT_2K_PATH)
cad_im = Image.open(PREVIEW_PATH)

fig_comp, axes = plt.subplots(1, 2, figsize=(26, 12), dpi=150)
axes[0].imshow(orig_2k_im)
axes[0].set_title("INPUT IMAGE (Map_Location.png_2K_20261009192633.jpg)", fontsize=13, weight="bold", pad=10)
axes[0].axis("off")

axes[1].imshow(cad_im)
axes[1].set_title("PROFESSIONAL MULTI-COLOR 2D CAD MAP (Map_Location_2D.dxf)", fontsize=13, weight="bold", pad=10)
axes[1].axis("off")

plt.tight_layout()
plt.savefig(COMPARISON_PATH, bbox_inches="tight")
plt.close(fig_comp)
print(f"Saved updated comparison to: {COMPARISON_PATH}")
print("ALL MANUAL-STYLE CLEAN CAD PIPELINE COMPLETE.")
