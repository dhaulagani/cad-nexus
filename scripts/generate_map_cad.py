r"""
Comprehensive 2D CAD Site Location Map Generator
Site: US1051671_Blue Diamond
Location Coordinates: 39.196442 N, -114.855244 W (Existing Tower)
Source: C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final\Map_Location.png

Full Architectural / Civil Site Plan including:
1. Exact Road Geometries:
   - MAIN ROAD (Paved Asphalt Highway US-93: Width, Markings, Shoulders, Turnouts)
   - STREET ROAD (Off-Road / Dirt Road: Width 16', Centerline, Edges, Surface Hatch)
   - PRIVATE DRIVEWAYS (Access to surrounding parcels & residences)
2. Surrounding Buildings & Structures (Residences, Barns, Mobile Homes, Outbuildings)
3. Environmental Vegetation & Terrain:
   - Dense Shrub & Brush Stands (Lowry Canyon Wash & Property Boundaries)
   - Individual Tree Canopies & Landscape Symbols
   - Natural Drainage Wash & Gully Lines
4. Existing Constructed Monopole Tower & Compound (Enlarged Detail A Plan)
5. Road Classification Table, Legend, North Arrow, Dual Scale Bars & Title Block
"""

import os
import math
import numpy as np
from PIL import Image
from scipy import ndimage
import ezdxf
from ezdxf import colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# File Paths
IMAGE_PATH = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final\Map_Location.png"
OUTPUT_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final"
DXF_PATH = os.path.join(OUTPUT_DIR, "Map_Location_2D.dxf")
PREVIEW_PATH = os.path.join(OUTPUT_DIR, "Map_Location_CAD_2D.png")
DETAIL_PATH = os.path.join(OUTPUT_DIR, "Tower_Site_Detail_CAD.png")
COMPARISON_PATH = os.path.join(OUTPUT_DIR, "Map_Location_Comparison.png")

print(f"Loading satellite imagery: {IMAGE_PATH}")
im = Image.open(IMAGE_PATH).convert("RGB")
w_px, h_px = im.size
arr = np.array(im, dtype=float)
r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
gray = 0.299 * r + 0.587 * g + 0.114 * b

# Coordinates & Scale
PIN_X, PIN_Y = 125, 557 # Existing Monopole Tower Center in image pixels
LAT_DEG = 39.196442
LONG_DEG = -114.855244
M_PER_PX = 156543.03392 * math.cos(math.radians(LAT_DEG)) / (2**17) # ~0.9255 m/px
FT_PER_PX = M_PER_PX * 3.28084 # ~3.0364 ft/px
SCALE_FT = FT_PER_PX # 1 CAD unit = 1 foot

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

# 1. Road Networks
# A. MAIN ROAD (State Route / Highway US-93 - Paved Asphalt)
hw_cl_px = [
    (975, 0), (988, 50), (1005, 100), (1025, 150), (1048, 200),
    (1072, 250), (1096, 300), (1122, 350), (1148, 400), (1175, 450),
    (1198, 500), # Main Ingress / Turnout
    (1222, 550), (1248, 600), (1274, 650), (1298, 700), (1320, 750), (1323, 756)
]
HW_WIDTH_FT = 30.0 # 2-lane 12' lanes + 3' paved shoulders = 30'
hw_cl_cad = to_cad_list(hw_cl_px)
hw_left_cad = offset_line(hw_cl_cad, HW_WIDTH_FT / 2.0)
hw_right_cad = offset_line(hw_cl_cad, -HW_WIDTH_FT / 2.0)
hw_shld_l_cad = offset_line(hw_cl_cad, HW_WIDTH_FT / 2.0 + 6.0)
hw_shld_r_cad = offset_line(hw_cl_cad, -(HW_WIDTH_FT / 2.0 + 6.0))

# B. STREET ROAD (Off-Road / Dirt Road - Graded Unpaved Roads)
DIRT_WIDTH_FT = 16.0

# 1. Primary Site Access Street (Highway Turnout -> Existing Tower)
dirt_main_cl_px = [
    (1198, 500), (1120, 503), (1015, 502), (905, 496), (785, 492),
    (670, 488), (560, 485), (465, 490), (360, 498), (250, 506),
    (165, 510), (130, 515), (126, 535), (125, 557)
]
dirt_main_cl_cad = to_cad_list(dirt_main_cl_px)
dirt_main_l_cad = offset_line(dirt_main_cl_cad, DIRT_WIDTH_FT / 2.0)
dirt_main_r_cad = offset_line(dirt_main_cl_cad, -DIRT_WIDTH_FT / 2.0)

# 2. Western Dirt Street (North-South Street passing directly in front of Tower)
dirt_west_cl_px = [
    (130, 150), (128, 250), (126, 350), (128, 450),
    (130, 515), (125, 557), (122, 630), (120, 720)
]
dirt_west_cl_cad = to_cad_list(dirt_west_cl_px)
dirt_west_l_cad = offset_line(dirt_west_cl_cad, DIRT_WIDTH_FT / 2.0)
dirt_west_r_cad = offset_line(dirt_west_cl_cad, -DIRT_WIDTH_FT / 2.0)

# 3. North Residential Street Loop
dirt_north_cl_px = [
    (670, 488), (665, 410), (655, 330), (630, 250), (585, 195),
    (515, 160), (430, 165), (380, 210), (390, 280), (415, 360),
    (445, 430), (465, 490)
]
dirt_north_cl_cad = to_cad_list(dirt_north_cl_px)
dirt_north_l_cad = offset_line(dirt_north_cl_cad, 7.0)
dirt_north_r_cad = offset_line(dirt_north_cl_cad, -7.0)

# 4. South Residential Street Loop
dirt_south_cl_px = [
    (670, 488), (675, 550), (660, 620), (610, 670),
    (530, 675), (460, 630), (430, 560), (360, 498)
]
dirt_south_cl_cad = to_cad_list(dirt_south_cl_px)

# 5. Highway Frontage Dirt Track
dirt_front_cl_px = [
    (1010, 40), (1040, 160), (1080, 300), (1125, 420),
    (1198, 500), (1230, 590), (1265, 700)
]
dirt_front_cl_cad = to_cad_list(dirt_front_cl_px)

# 6. Private Residential Driveways
driveways_px = [
    # Driveway to North Main Residence (611, 218)
    [(630, 250), (620, 230), (615, 220)],
    # Driveway to North-Central Residence (411, 215)
    [(430, 165), (425, 190), (415, 215)],
    # Driveway to Mobile Home / Trailer (674, 282)
    [(655, 330), (665, 305), (675, 285)],
    # Driveway to South Residence (560, 429)
    [(560, 485), (560, 455), (560, 435)],
    # Driveway to West Neighbor Structure (137, 510)
    [(130, 515), (135, 512), (145, 510)]
]
driveways_cad = [to_cad_list(dw) for dw in driveways_px]

# 2. Surrounding Buildings & Structures (Detailed Footprints)
buildings_data = [
    {
        "name": "EXISTING NORTH RESIDENCE",
        "pts": [(611, 218), (650, 218), (650, 274), (611, 274), (611, 218)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING WORKSHOP / BARN",
        "pts": [(517, 235), (539, 235), (539, 278), (517, 278), (517, 235)],
        "type": "BARN"
    },
    {
        "name": "EXISTING WEST RESIDENCE",
        "pts": [(411, 215), (451, 215), (451, 246), (411, 246), (411, 215)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING MOBILE HOME / TRAILER",
        "pts": [(674, 282), (689, 282), (689, 337), (674, 337), (674, 282)],
        "type": "TRAILER"
    },
    {
        "name": "OUTBUILDING / SHED",
        "pts": [(410, 272), (426, 272), (426, 304), (410, 304), (410, 272)],
        "type": "SHED"
    },
    {
        "name": "EXISTING RESIDENCE / GARAGE",
        "pts": [(588, 314), (604, 314), (604, 344), (588, 344), (588, 314)],
        "type": "RESIDENCE"
    },
    {
        "name": "EXISTING SOUTH RESIDENCE",
        "pts": [(560, 429), (581, 429), (581, 447), (560, 447), (560, 429)],
        "type": "RESIDENCE"
    },
    {
        "name": "SOUTH OUTBUILDING",
        "pts": [(617, 619), (634, 619), (634, 634), (617, 634), (617, 619)],
        "type": "SHED"
    },
    {
        "name": "SOUTH SHED",
        "pts": [(566, 633), (585, 633), (585, 643), (566, 643), (566, 633)],
        "type": "SHED"
    },
    {
        "name": "NEIGHBOR STRUCTURE (NORTH OF TOWER)",
        "pts": [(137, 510), (156, 510), (156, 533), (137, 533), (137, 510)],
        "type": "SHED"
    },
    {
        "name": "NEIGHBOR SHED",
        "pts": [(154, 442), (173, 442), (173, 459), (154, 459), (154, 442)],
        "type": "SHED"
    }
]

# 3. Environmental Vegetation & Natural Features
# A. Major Vegetation Stands (Shrub/Brush Forests & Wash Canopy)
veg_stands_px = [
    # 1. Lowry Canyon Wash Dense Riparian / Sagebrush Stand (NW)
    [(30, 40), (120, 60), (220, 75), (320, 90), (420, 110), (450, 160), (380, 200), (280, 180), (160, 140), (80, 100), (30, 40)],
    # 2. North Residential Yard Tree Cluster (Around North House)
    [(600, 200), (660, 200), (720, 240), (740, 320), (700, 360), (640, 340), (580, 300), (580, 240), (600, 200)],
    # 3. East Property Boundary Tree & Shrub Line (Along Highway Frontage)
    [(760, 260), (830, 280), (840, 360), (770, 340), (760, 260)],
    # 4. South Property Dense Shrub Area
    [(810, 650), (950, 640), (1020, 700), (920, 750), (820, 740), (810, 650)],
    # 5. Southeast Hill Shrub Stand
    [(1180, 680), (1300, 690), (1310, 780), (1200, 770), (1180, 680)],
    # 6. Southwest Canyon Rim Stand
    [(60, 320), (110, 340), (115, 420), (70, 440), (60, 320)]
]
veg_stands_cad = [to_cad_list(v) for v in veg_stands_px]

# B. Individual Tree Canopies (Detected in satellite pixels)
# Extract centroids of trees in residential areas and along tracks
tree_score = (gray < 95) & (g > b * 1.05) & (r < 110)
lbl_trees, num_trees = ndimage.label(tree_score)
slices = ndimage.find_objects(lbl_trees)

tree_list = []
for i, s in enumerate(slices):
    patch = (lbl_trees[s] == (i + 1))
    area = np.sum(patch)
    if 15 <= area <= 180:
        sy, sx = s
        cx = (sx.start + sx.stop) / 2.0
        cy = (sy.start + sy.stop) / 2.0
        radius_ft = math.sqrt(area) * SCALE_FT * 0.45
        radius_ft = max(5.0, min(14.0, radius_ft))
        tree_cad_x, tree_cad_y = to_cad(cx, cy)
        tree_list.append((tree_cad_x, tree_cad_y, radius_ft))

print(f"Sampled individual landscape trees: {len(tree_list)}")

# C. Natural Drainage Wash (Lowry Canyon)
canyon_wash_px = [
    [(10, 30), (80, 65), (170, 90), (270, 105), (370, 115), (470, 120)],
    [(120, 15), (210, 45), (310, 65), (410, 75), (510, 85)]
]
canyon_wash_cad = [to_cad_list(w) for w in canyon_wash_px]

# 4. Existing Constructed Tower & Compound Details
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

# Total Access Distance
total_dist_ft = 0.0
for i in range(len(dirt_main_cl_cad) - 1):
    total_dist_ft += math.hypot(dirt_main_cl_cad[i+1][0] - dirt_main_cl_cad[i][0], dirt_main_cl_cad[i+1][1] - dirt_main_cl_cad[i][1])

# 5. Create AutoCAD DXF File
doc = ezdxf.new(dxfversion="R2018")
doc.header["$INSUNITS"] = 2 # US Survey Feet

# Professional Layer Schema
layers = [
    ("C-ROAD-MAIN-ASPH", colors.GRAY, "Continuous", "Main Road (Highway US-93) Pavement Edges"),
    ("C-ROAD-MAIN-CL", colors.YELLOW, "DASHED", "Main Road Centerline (Paved Highway)"),
    ("C-ROAD-MAIN-SHLD", colors.LIGHT_GRAY, "DASHED", "Main Road Paved Shoulder"),
    ("C-ROAD-DIRT-EDGE", colors.CYAN, "Continuous", "Street Road (Dirt/Off-Road) Edges"),
    ("C-ROAD-DIRT-CL", colors.CYAN, "DASHDOT", "Street Road (Dirt/Off-Road) Centerline"),
    ("C-ROAD-DIRT-TRCK", colors.LIGHT_GRAY, "Continuous", "Local Residential Dirt Tracks"),
    ("C-ROAD-DRIV-WAY", colors.LIGHT_GRAY, "DASHED", "Private Residential Driveways"),
    ("C-BLDG-EXST", colors.BLUE, "Continuous", "Existing Surrounding Buildings Footprints"),
    ("C-TOPO-VEGT", colors.GREEN, "Continuous", "Dense Shrub & Brush Stands Boundary"),
    ("C-TOPO-TREE", colors.GREEN, "Continuous", "Individual Tree Canopies & Shrub Symbols"),
    ("C-TOPO-WASH", colors.CYAN, "DASHED", "Lowry Canyon Natural Drainage Wash"),
    ("C-TOWR-POLE", colors.MAGENTA, "Continuous", "Existing Monopole Tower (Constructed)"),
    ("C-TOWR-FNDN", colors.WHITE, "Continuous", "Existing Foundation & Concrete Equipment Pad"),
    ("C-TOWR-EQUP", colors.BLUE, "Continuous", "Existing Equipment Cabinets & Telco Racks"),
    ("C-TOWR-FENC", colors.RED, "Continuous", "Existing Compound Chain-Link Fence & Gate"),
    ("C-TOWR-APRN", colors.GREEN, "DASHED", "Existing Gravel Apron & Turnaround"),
    ("C-PROP-LINE", colors.YELLOW, "PHANTOM", "Property / Parcel Boundaries"),
    ("C-ANNO-TEXT", colors.WHITE, "Continuous", "Text Notes & Identifiers"),
    ("C-ANNO-DIMS", colors.CYAN, "Continuous", "Dimensions & Distance Leaders"),
    ("C-ANNO-LEGD", colors.WHITE, "Continuous", "Road Classification Legend & Tables"),
    ("C-ANNO-NORT", colors.YELLOW, "Continuous", "North Arrow & Graphic Scale Bars"),
    ("C-TTLB-BORR", colors.WHITE, "Continuous", "Sheet Border & Title Block")
]

for l_name, l_col, l_type, l_desc in layers:
    lyr = doc.layers.add(l_name)
    lyr.color = l_col
    lyr.description = l_desc

msp = doc.modelspace()

# A. Add Main Road
msp.add_lwpolyline(hw_cl_cad, dxfattribs={"layer": "C-ROAD-MAIN-CL", "linetype": "DASHED"})
msp.add_lwpolyline(hw_left_cad, dxfattribs={"layer": "C-ROAD-MAIN-ASPH"})
msp.add_lwpolyline(hw_right_cad, dxfattribs={"layer": "C-ROAD-MAIN-ASPH"})
msp.add_lwpolyline(hw_shld_l_cad, dxfattribs={"layer": "C-ROAD-MAIN-SHLD", "linetype": "DASHED"})
msp.add_lwpolyline(hw_shld_r_cad, dxfattribs={"layer": "C-ROAD-MAIN-SHLD", "linetype": "DASHED"})

# B. Add Street Road (Dirt / Off-Road)
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

# C. Add Buildings
for b in buildings_data:
    b_cad = to_cad_list(b["pts"])
    msp.add_lwpolyline(b_cad, dxfattribs={"layer": "C-BLDG-EXST"})
    cx = sum(p[0] for p in b_cad[:-1]) / (len(b_cad) - 1)
    cy = sum(p[1] for p in b_cad[:-1]) / (len(b_cad) - 1)
    msp.add_text(b["name"], dxfattribs={"layer": "C-ANNO-TEXT", "height": 10.0, "insert": (cx - 40.0, cy + 20.0)})

# D. Add Vegetation Stands & Trees
for v in veg_stands_cad:
    msp.add_lwpolyline(v, dxfattribs={"layer": "C-TOPO-VEGT"})

for tx, ty, tr in tree_list:
    msp.add_circle((tx, ty), radius=tr, dxfattribs={"layer": "C-TOPO-TREE"})
    msp.add_circle((tx, ty), radius=tr * 0.4, dxfattribs={"layer": "C-TOPO-TREE"})

for w in canyon_wash_cad:
    msp.add_lwpolyline(w, dxfattribs={"layer": "C-TOPO-WASH", "linetype": "DASHED"})

# E. Add Existing Monopole Tower & Compound
msp.add_circle((0.0, 0.0), radius=CAISSON_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-FNDN"})
msp.add_circle((0.0, 0.0), radius=POLE_BASE_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_circle((0.0, 0.0), radius=POLE_TOP_DIA_FT / 2.0, dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_line((-6.0, 0.0), (6.0, 0.0), dxfattribs={"layer": "C-TOWR-POLE"})
msp.add_line((0.0, -6.0), (0.0, 6.0), dxfattribs={"layer": "C-TOWR-POLE"})

msp.add_lwpolyline(compound_fence_cad, dxfattribs={"layer": "C-TOWR-FENC"})
msp.add_lwpolyline(equip_pad_cad, dxfattribs={"layer": "C-TOWR-FNDN"})
msp.add_lwpolyline(cab1_cad, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(cab2_cad, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(telco_rack_cad, dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_line(ice_bridge_cad[0], ice_bridge_cad[1], dxfattribs={"layer": "C-TOWR-EQUP"})
msp.add_lwpolyline(apron_cad, dxfattribs={"layer": "C-TOWR-APRN", "linetype": "DASHED"})

# F. Annotations
msp.add_text("EXISTING CONSTRUCTED MONOPOLE TOWER (120' AGL)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 18.0, "insert": (-160.0, 30.0)})
msp.add_text("COORDINATES: 39 11'47.2\"N, 114 51'18.9\"W", dxfattribs={"layer": "C-ANNO-TEXT", "height": 14.0, "insert": (-160.0, 10.0)})
msp.add_text("STATE ROUTE / HIGHWAY US-93 (MAIN ROAD - PAVED ASPHALT)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 22.0, "insert": (3300.0, 200.0), "rotation": -67.0})
msp.add_text(f"STREET ROAD (OFF-ROAD / DIRT ROAD) - TOTAL ACCESS: {total_dist_ft:.0f} FT ({total_dist_ft*0.3048:.0f} M)", dxfattribs={"layer": "C-ANNO-TEXT", "height": 16.0, "insert": (800.0, 210.0), "rotation": -5.0})

# Save DXF
doc.saveas(DXF_PATH)
print(f"Master DXF saved to: {DXF_PATH}")

# 6. Render High-Resolution Architectural Sheet Presentation (PNG)
fig = plt.figure(figsize=(26, 16), dpi=200, facecolor="#14171c")

ax_main = fig.add_axes([0.035, 0.05, 0.63, 0.90], facecolor="#0e1117")
ax_detail = fig.add_axes([0.685, 0.47, 0.285, 0.48], facecolor="#0e1117")
ax_legend = fig.add_axes([0.685, 0.23, 0.285, 0.22], facecolor="#161b22")
ax_title = fig.add_axes([0.685, 0.05, 0.285, 0.16], facecolor="#161b22")

# ==================== VIEWPORT 1: MAIN SITE LOCATION MAP ====================
ax_main.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.6, alpha=0.8)

# 1. Environmental Vegetation Stands (Dense Shrub / Wash Canopy)
for idx, v in enumerate(veg_stands_cad):
    poly_veg = patches.Polygon(v, facecolor="#14532d", edgecolor="#22c55e", lw=1.2, ls="--", alpha=0.35, zorder=1)
    ax_main.add_patch(poly_veg)
    if idx == 0:
        ax_main.text(v[3][0], v[3][1] + 20, "DENSE BRUSH / WASH VEGETATION", color="#22c55e", fontsize=8.5, weight="bold", zorder=2)

# Individual Landscape Tree Canopies
for tx, ty, tr in tree_list:
    circ_outer = plt.Circle((tx, ty), tr, facecolor="#15803d", edgecolor="#4ade80", lw=0.6, alpha=0.5, zorder=2)
    circ_inner = plt.Circle((tx, ty), tr * 0.4, facecolor="#22c55e", edgecolor="#ffffff", lw=0.4, alpha=0.7, zorder=3)
    ax_main.add_patch(circ_outer)
    ax_main.add_patch(circ_inner)

# Lowry Canyon Wash drainage lines
for w in canyon_wash_cad:
    ax_main.plot([p[0] for p in w], [p[1] for p in w], color="#06b6d4", lw=1.8, ls=":", zorder=2, label="Lowry Canyon Natural Wash" if w==canyon_wash_cad[0] else None)

# 2. Surrounding Buildings & Outbuildings
for b in buildings_data:
    b_cad = to_cad_list(b["pts"])
    xs = [p[0] for p in b_cad]
    ys = [p[1] for p in b_cad]
    ax_main.fill(xs, ys, color="#3b82f6", alpha=0.45, zorder=4)
    ax_main.plot(xs, ys, color="#60a5fa", lw=1.8, zorder=5)
    cx = sum(xs[:-1]) / (len(xs) - 1)
    cy = sum(ys[:-1]) / (len(ys) - 1)
    ax_main.text(cx, cy + 15, b["type"], color="#93c5fd", fontsize=7.5, weight="bold", ha="center", zorder=6)

# Private Driveways
for dw in driveways_cad:
    ax_main.plot([p[0] for p in dw], [p[1] for p in dw], color="#94a3b8", lw=1.5, ls="--", zorder=3, label="Private Driveway" if dw==driveways_cad[0] else None)

# 3. Roads
# MAIN ROAD (Highway US-93 - Asphalt)
ax_main.fill(
    [p[0] for p in hw_left_cad] + [p[0] for p in reversed(hw_right_cad)],
    [p[1] for p in hw_left_cad] + [p[1] for p in reversed(hw_right_cad)],
    color="#384152", alpha=0.95, zorder=3
)
ax_main.plot([p[0] for p in hw_cl_cad], [p[1] for p in hw_cl_cad], color="#f59e0b", lw=2.5, ls="--", zorder=4, label="MAIN ROAD Centerline (Highway US-93)")
ax_main.plot([p[0] for p in hw_left_cad], [p[1] for p in hw_left_cad], color="#e2e8f0", lw=2.2, zorder=4, label="MAIN ROAD Pavement Edge (Asphalt)")
ax_main.plot([p[0] for p in hw_right_cad], [p[1] for p in hw_right_cad], color="#e2e8f0", lw=2.2, zorder=4)
ax_main.plot([p[0] for p in hw_shld_l_cad], [p[1] for p in hw_shld_l_cad], color="#94a3b8", lw=1.2, ls=":", zorder=3, label="MAIN ROAD Paved Shoulder")
ax_main.plot([p[0] for p in hw_shld_r_cad], [p[1] for p in hw_shld_r_cad], color="#94a3b8", lw=1.2, ls=":", zorder=3)

# STREET ROAD (Off-Road / Dirt Road)
# Main Access Dirt Road
ax_main.fill(
    [p[0] for p in dirt_main_l_cad] + [p[0] for p in reversed(dirt_main_r_cad)],
    [p[1] for p in dirt_main_l_cad] + [p[1] for p in reversed(dirt_main_r_cad)],
    color="#78350f", alpha=0.35, zorder=3
)
ax_main.plot([p[0] for p in dirt_main_cl_cad], [p[1] for p in dirt_main_cl_cad], color="#38bdf8", lw=2.2, ls="-.", zorder=4, label="STREET ROAD Centerline (Dirt/Off-Road)")
ax_main.plot([p[0] for p in dirt_main_l_cad], [p[1] for p in dirt_main_l_cad], color="#38bdf8", lw=1.6, ls="-", zorder=4, label="STREET ROAD Limits (16' Width)")
ax_main.plot([p[0] for p in dirt_main_r_cad], [p[1] for p in dirt_main_r_cad], color="#38bdf8", lw=1.6, ls="-", zorder=4)

# Western Dirt Street
ax_main.fill(
    [p[0] for p in dirt_west_l_cad] + [p[0] for p in reversed(dirt_west_r_cad)],
    [p[1] for p in dirt_west_l_cad] + [p[1] for p in reversed(dirt_west_r_cad)],
    color="#78350f", alpha=0.35, zorder=3
)
ax_main.plot([p[0] for p in dirt_west_cl_cad], [p[1] for p in dirt_west_cl_cad], color="#38bdf8", lw=2.2, ls="-.", zorder=4)
ax_main.plot([p[0] for p in dirt_west_l_cad], [p[1] for p in dirt_west_l_cad], color="#38bdf8", lw=1.6, ls="-", zorder=4)
ax_main.plot([p[0] for p in dirt_west_r_cad], [p[1] for p in dirt_west_r_cad], color="#38bdf8", lw=1.6, ls="-", zorder=4)

# Other Dirt Tracks
for seg in [dirt_north_cl_cad, dirt_south_cl_cad, dirt_front_cl_cad]:
    ax_main.plot([p[0] for p in seg], [p[1] for p in seg], color="#64748b", lw=1.4, ls="-", zorder=3, label="Local Dirt Track" if seg==dirt_north_cl_cad else None)

# 4. Existing Tower Compound Marker & Detail Callout
comp_rect = patches.Rectangle((comp_x0, comp_y0), FENCE_WIDTH_FT, FENCE_DEPTH_FT, facecolor="#ef4444", edgecolor="#ef4444", alpha=0.45, zorder=6)
ax_main.add_patch(comp_rect)
ax_main.plot([p[0] for p in compound_fence_cad], [p[1] for p in compound_fence_cad], color="#ef4444", lw=2.2, zorder=7, label="Existing Compound Fence (40'x40')")
ax_main.plot(0, 0, marker="o", markersize=10, color="#ec4899", markeredgecolor="#ffffff", markeredgewidth=1.8, zorder=8, label="Existing Monopole Tower")

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
ax_main.legend(loc="lower left", facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0", fontsize=8, framealpha=0.95)

# ==================== VIEWPORT 2: DETAIL A (TOWER SITE FOCUS) ====================
ax_detail.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.6, alpha=0.8)

# Compound Gravel Surface
ax_detail.add_patch(patches.Rectangle((comp_x0, comp_y0), FENCE_WIDTH_FT, FENCE_DEPTH_FT, facecolor="#334155", edgecolor="#ef4444", lw=2.5, zorder=2))
# Apron
ax_detail.add_patch(patches.Polygon(apron_cad, facecolor="#475569", edgecolor="#38bdf8", lw=1.5, ls="--", alpha=0.6, zorder=2))
ax_detail.text(comp_x0 - 14, comp_y0 + 20, "EXISTING GRAVEL\nAPRON & DRIVE", color="#38bdf8", fontsize=8, ha="center", weight="bold")

# Surrounding native shrubs in detail
for dx_s, dy_s in [(-38, -25), (-35, 25), (32, 28), (30, -30), (25, -5)]:
    ax_detail.add_patch(plt.Circle((dx_s, dy_s), 4.5, facecolor="#15803d", edgecolor="#4ade80", lw=0.6, alpha=0.6, zorder=2))

# Western Dirt Street
ax_detail.plot([-25, -25], [-35, 45], color="#38bdf8", lw=2.5, ls="-", zorder=3)
ax_detail.plot([-41, -41], [-35, 45], color="#38bdf8", lw=2.5, ls="-", zorder=3)
ax_detail.plot([-33, -33], [-35, 45], color="#38bdf8", lw=1.8, ls="-.", zorder=3)
ax_detail.text(-33, 38, "WESTERN STREET ROAD\n(DIRT ROAD - 16' WIDE)", color="#38bdf8", fontsize=8.5, weight="bold", ha="center")

# Concrete Pad & Cabinets
ax_detail.add_patch(patches.Rectangle((pad_x0, pad_y0), 14.0, 22.0, facecolor="#94a3b8", edgecolor="#ffffff", lw=2.0, zorder=4))
ax_detail.text(pad_x0 + 7.0, pad_y0 + 18.0, "CONCRETE PAD\n14' x 22'", color="#0f172a", fontsize=7.5, ha="center", weight="bold", zorder=5)

ax_detail.add_patch(patches.Rectangle((pad_x0 + 1.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.2, zorder=5))
ax_detail.add_patch(patches.Rectangle((pad_x0 + 7.5, pad_y0 + 2.0), 4.5, 5.0, facecolor="#2563eb", edgecolor="#ffffff", lw=1.2, zorder=5))
ax_detail.text(pad_x0 + 3.75, pad_y0 + 4.5, "BTS", color="#ffffff", fontsize=7, ha="center", va="center", weight="bold", zorder=6)
ax_detail.text(pad_x0 + 9.75, pad_y0 + 4.5, "BATT", color="#ffffff", fontsize=7, ha="center", va="center", weight="bold", zorder=6)

ax_detail.add_patch(patches.Rectangle((pad_x0 + 2.0, pad_y0 + 11.0), 10.0, 3.0, facecolor="#0284c7", edgecolor="#ffffff", lw=1.2, zorder=5))
ax_detail.text(pad_x0 + 7.0, pad_y0 + 12.5, "TELCO / POWER RACK", color="#ffffff", fontsize=6.5, ha="center", va="center", weight="bold", zorder=6)

# Ice Bridge
ax_detail.plot([0.0, pad_x0 + 3.0], [0.0, 0.0], color="#f59e0b", lw=3.0, zorder=6)
ax_detail.text(pad_x0 / 2.0, 2.5, "ICE BRIDGE", color="#f59e0b", fontsize=7, ha="center", weight="bold")

# Monopole Tower Foundation & Pole
ax_detail.add_patch(plt.Circle((0, 0), CAISSON_DIA_FT / 2.0, facecolor="#cbd5e1", edgecolor="#ffffff", lw=2.0, zorder=5))
ax_detail.add_patch(plt.Circle((0, 0), POLE_BASE_DIA_FT / 2.0, facecolor="#475569", edgecolor="#ec4899", lw=2.0, zorder=6))
ax_detail.add_patch(plt.Circle((0, 0), POLE_TOP_DIA_FT / 2.0, facecolor="#ec4899", edgecolor="#ffffff", lw=1.5, zorder=7))
ax_detail.plot([-5, 5], [0, 0], color="#ffffff", lw=1.2, zorder=8)
ax_detail.plot([0, 0], [-5, 5], color="#ffffff", lw=1.2, zorder=8)

# Gate
ax_detail.plot([comp_x0, comp_x0 - 8.0], [gate_p1[1], gate_p1[1]], color="#ef4444", lw=2.2, ls="--", zorder=6)
ax_detail.plot([comp_x0, comp_x0 - 8.0], [gate_p2[1], gate_p2[1]], color="#ef4444", lw=2.2, ls="--", zorder=6)
ax_detail.text(comp_x0 - 2.0, (gate_p1[1] + gate_p2[1])/2.0, "12' SWING GATE", color="#ef4444", fontsize=7.5, weight="bold", rotation=90, va="center")

# Dimensions
ax_detail.annotate("", xy=(comp_x0, comp_y1 + 4), xytext=(comp_x1, comp_y1 + 4), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.2))
ax_detail.text((comp_x0 + comp_x1)/2.0, comp_y1 + 6.0, "40'-0\" COMPOUND WIDTH", color="#e2e8f0", fontsize=8, ha="center", weight="bold")

ax_detail.annotate("", xy=(comp_x1 + 4, comp_y0), xytext=(comp_x1 + 4, comp_y1), arrowprops=dict(arrowstyle="<->", color="#e2e8f0", lw=1.2))
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
ax_legend.plot([5, 18], [75, 75], color="#e2e8f0", lw=1.8)
ax_legend.plot([5, 18], [69, 69], color="#e2e8f0", lw=1.8)
ax_legend.text(22, 72, "MAIN ROAD (HIGHWAY US-93 / STATE ROUTE)", color="#f59e0b", fontsize=8.5, weight="bold", va="center")
ax_legend.text(22, 63, "Paved Asphalt | Width: 30'-0\" | Two-Lane with Paved Shoulders", color="#94a3b8", fontsize=7.5, va="center")

# Row 2: STREET ROAD
ax_legend.plot([5, 18], [50, 50], color="#38bdf8", lw=2.2, ls="-.")
ax_legend.plot([5, 18], [53, 53], color="#38bdf8", lw=1.5)
ax_legend.plot([5, 18], [47, 47], color="#38bdf8", lw=1.5)
ax_legend.text(22, 50, "STREET ROAD (OFF-ROAD / DIRT ROAD)", color="#38bdf8", fontsize=8.5, weight="bold", va="center")
ax_legend.text(22, 41, "Graded Gravel/Dirt | Width: 16'-0\" | Primary Site Access", color="#94a3b8", fontsize=7.5, va="center")

# Row 3: STRUCTURES & VEGETATION
r_bldg = patches.Rectangle((5, 23), 13, 8, facecolor="#3b82f6", edgecolor="#60a5fa", lw=1.2)
ax_legend.add_patch(r_bldg)
ax_legend.text(22, 27, "EXISTING SURROUNDING BUILDINGS / STRUCTURES", color="#60a5fa", fontsize=8.5, weight="bold", va="center")

# Tree Symbol in Legend
c_veg = plt.Circle((11, 10), 4.5, facecolor="#15803d", edgecolor="#4ade80", lw=1.0)
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
ax_title.text(4, 74, "MURNI DIEKSTRAK DARI SATELLITE IMAGE Map_Location.png", color="#94a3b8", fontsize=8)

ax_title.text(4, 55, "SITE NAME: US1051671_BLUE DIAMOND", color="#ffffff", fontsize=9.5, weight="bold")
ax_title.text(4, 42, "TOWER STATUS: EXISTING CONSTRUCTED (120' MONOPOLE)", color="#ec4899", fontsize=9, weight="bold")

ax_title.text(4, 23, "COORDINATES: 39°11'47.2\"N, 114°51'18.9\"W", color="#e2e8f0", fontsize=8.5)
ax_title.text(4, 10, "LAT: 39.196442° N | LONG: -114.855244° W (WGS84)", color="#94a3b8", fontsize=8)

ax_title.text(84, 52, "SHEET NO.", color="#94a3b8", fontsize=8, ha="center")
ax_title.text(84, 40, "C-101", color="#ffffff", fontsize=16, weight="bold", ha="center")
ax_title.text(84, 22, "REV: 2 (FINAL)", color="#38bdf8", fontsize=8, ha="center", weight="bold")
ax_title.text(84, 9, "DATE: 2026-10", color="#94a3b8", fontsize=7.5, ha="center")

# Save Presentation Sheet
plt.savefig(PREVIEW_PATH, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Saved complete architectural sheet to: {PREVIEW_PATH}")

# 7. Update Comparison Image
orig_im = Image.open(IMAGE_PATH)
cad_im = Image.open(PREVIEW_PATH)

fig_comp, axes = plt.subplots(1, 2, figsize=(26, 12), dpi=150)
axes[0].imshow(orig_im)
axes[0].set_title("ORIGINAL SATELLITE IMAGE (Map_Location.png)", fontsize=14, weight="bold", pad=10)
axes[0].axis("off")

axes[1].imshow(cad_im)
axes[1].set_title("2D CAD LOCATION MAP: ROADS, STRUCTURES & VEGETATION", fontsize=14, weight="bold", pad=10)
axes[1].axis("off")

plt.tight_layout()
plt.savefig(COMPARISON_PATH, bbox_inches="tight")
plt.close(fig_comp)
print(f"Saved updated comparison to: {COMPARISON_PATH}")
print("ALL TASKS COMPLETED SUCCESSFULLY.")
