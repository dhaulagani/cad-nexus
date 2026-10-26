r"""
Direct Raster-to-Vector (JPG to DXF) Converter
Source: C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\RAW\Map_Location.png_2K_20261009192633.jpg
Outputs:
- C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final\Map_Location_2D.dxf (Direct 1:1 Vectorized CAD)
- C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final\Map_Location_2K_Direct.dxf
- C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final\Map_Location_Direct_Vector_Preview.png
"""

import os
import time
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import ezdxf
from ezdxf import colors

# File Paths
JPG_PATH = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\RAW\Map_Location.png_2K_20261009192633.jpg"
OUTPUT_DIR = r"C:\Data\Documents\Documents Gani\Monopole\US1051671_Blue Diamond\Final"
DXF_DIRECT = os.path.join(OUTPUT_DIR, "Map_Location_2K_Direct.dxf")
DXF_FINAL = os.path.join(OUTPUT_DIR, "Map_Location_2D.dxf")
PNG_PREVIEW = os.path.join(OUTPUT_DIR, "Map_Location_Direct_Vector_Preview.png")

print(f"Loading input JPG: {JPG_PATH}")
t0 = time.time()
im = Image.open(JPG_PATH).convert("L")
arr = np.array(im)
h, w = arr.shape
print(f"Input dimensions: W={w}, H={h} pixels")

# 1. High-Performance Contour Extraction (Marching Squares)
# Thresholding dark linework (linework is black/dark gray < 180)
print("Extracting vector contours from raster pixels...")
fig, ax = plt.subplots()
cs = ax.contour(arr, levels=[180])
raw_paths = cs.allsegs[0]
plt.close(fig)
print(f"Extracted {len(raw_paths)} raw contour paths in {time.time() - t0:.2f}s")

# 2. Vector Simplification & Smoothing (Douglas-Peucker)
# Removes staircase raster pixel noise while preserving 100% geometric corners and shapes
SIMPLIFY_TOLERANCE = 0.5 # 0.5 pixel sub-pixel tolerance
print(f"Simplifying vectors with tolerance = {SIMPLIFY_TOLERANCE} px...")

cleaned_polylines = []
total_pts_before = 0
total_pts_after = 0

for seg in raw_paths:
    if len(seg) >= 2:
        total_pts_before += len(seg)
        ls = LineString(seg)
        s_ls = ls.simplify(SIMPLIFY_TOLERANCE, preserve_topology=False)
        pts = list(s_ls.coords)
        if len(pts) >= 2:
            total_pts_after += len(pts)
            # Flip Y coordinate so that CAD Y points UP (Standard North Up CAD)
            cad_pts = [(float(c[0]), float(h - c[1])) for c in pts]
            is_closed = np.allclose(pts[0], pts[-1])
            cleaned_polylines.append((cad_pts, is_closed))

print(f"Simplified vertices: {total_pts_before} -> {total_pts_after} ({(1 - total_pts_after/total_pts_before)*100:.1f}% reduction)")
print(f"Total clean vector polylines: {len(cleaned_polylines)}")

# 3. Create Master DXF (AutoCAD R2018 format)
doc = ezdxf.new(dxfversion="R2018")
doc.header["$INSUNITS"] = 0 # Unitless / 1:1 Drawing Units matching 2K pixel coordinates

# Layers
doc.layers.add("VECT-MAP-LINES", color=colors.WHITE)
doc.layers.add("VECT-MAP-BORDER", color=colors.CYAN)
doc.layers.add("VECT-MAP-FILL", color=colors.GRAY)

msp = doc.modelspace()

for cad_pts, is_closed in cleaned_polylines:
    xs = [p[0] for p in cad_pts]
    ys = [p[1] for p in cad_pts]
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    
    # Classify layer
    if min(xs) < 15 and max(xs) > w - 15 and min(ys) < 15 and max(ys) > h - 15:
        layer_name = "VECT-MAP-BORDER"
    else:
        layer_name = "VECT-MAP-LINES"
        
    msp.add_lwpolyline(cad_pts, close=is_closed, dxfattribs={"layer": layer_name})

# Save DXF Files
doc.saveas(DXF_DIRECT)
doc.saveas(DXF_FINAL)

sz_direct = os.path.getsize(DXF_DIRECT) / 1024
sz_final = os.path.getsize(DXF_FINAL) / 1024
print(f"Saved DXF files successfully:")
print(f"- {DXF_DIRECT} ({sz_direct:.1f} KB)")
print(f"- {DXF_FINAL} ({sz_final:.1f} KB)")

# 4. Generate High-Resolution Visual Render Preview (PNG)
print("Rendering high-resolution vector visual preview...")
fig_prev, ax_prev = plt.subplots(figsize=(18, 10), dpi=200, facecolor="#14171c")
ax_prev.set_facecolor("#0e1117")
ax_prev.grid(True, which="both", color="#1c212b", linestyle="--", linewidth=0.5, alpha=0.7)

for cad_pts, is_closed in cleaned_polylines:
    xs = [p[0] for p in cad_pts]
    ys = [p[1] for p in cad_pts]
    if min(xs) < 15 and max(xs) > w - 15 and min(ys) < 15 and max(ys) > h - 15:
        col = "#38bdf8"
        lw = 1.5
    else:
        col = "#f8fafc"
        lw = 0.85
    ax_prev.plot(xs, ys, color=col, linewidth=lw)

ax_prev.set_xlim(-20, w + 20)
ax_prev.set_ylim(-20, h + 20)
ax_prev.set_aspect("equal", adjustable="box")
ax_prev.set_title("DIRECT VECTORIZED 2D CAD DRAWING (FROM 2K JPG)", color="#ffffff", fontsize=13, weight="bold", pad=12)
ax_prev.tick_params(colors="#64748b", labelsize=8.5)
ax_prev.set_xlabel("CAD X Units (1:1 with 2K image pixels)", color="#64748b", fontsize=9.5)
ax_prev.set_ylabel("CAD Y Units (North Up)", color="#64748b", fontsize=9.5)

plt.tight_layout()
plt.savefig(PNG_PREVIEW, dpi=200, bbox_inches="tight")
plt.close(fig_prev)
print(f"Saved visual vector preview to: {PNG_PREVIEW}")

# 5. Side-by-side comparison of original JPG and Direct Vector DXF
COMP_PATH = os.path.join(OUTPUT_DIR, "Map_Location_2K_Direct_Comparison.png")
im_input = Image.open(JPG_PATH)
im_vect = Image.open(PNG_PREVIEW)

fig_c, axes = plt.subplots(1, 2, figsize=(24, 11), dpi=150)
axes[0].imshow(im_input, cmap="gray")
axes[0].set_title("ORIGINAL INPUT JPG (Map_Location.png_2K_20261009192633.jpg)", fontsize=13, weight="bold", pad=10)
axes[0].axis("off")

axes[1].imshow(im_vect)
axes[1].set_title("DIRECT VECTORIZED DXF (Map_Location_2D.dxf)", fontsize=13, weight="bold", pad=10)
axes[1].axis("off")

plt.tight_layout()
plt.savefig(COMP_PATH, bbox_inches="tight")
plt.close(fig_c)
print(f"Saved comparison to: {COMP_PATH}")
print("DIRECT CONVERSION COMPLETE.")
