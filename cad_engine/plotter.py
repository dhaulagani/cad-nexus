r"""
cad_engine.plotter
High-performance, zero-error AutoCAD Core Console plotter and PDF/PNG exporter.
Enforces all learned invariants:
- acad.ctb plot style
- Plot with lineweights = NO (crisp hairlines, zero ink bloat)
- Double-quoted paths for whitespace resilience
- Pre-registration of standard DXF linetypes (DASHED, CENTER, etc.)
- 300 DPI high-resolution PNG export with auto-cropping
"""

import os
import subprocess
import ezdxf
import fitz  # PyMuPDF
from PIL import Image

ACCORECONSOLE = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"

class CadPlotter:
    @staticmethod
    def ensure_linetypes(doc: ezdxf.document.Drawing):
        """Pre-registers standard linetypes so DXFIN never discards drawings."""
        if "DASHED" not in doc.linetypes:
            doc.linetypes.new("DASHED", dxfattribs={"description": "Dashed __ __", "pattern": [0.5, 0.5, -0.25]})
        if "CENTER" not in doc.linetypes:
            doc.linetypes.new("CENTER", dxfattribs={"description": "Center ____ _ ____ _", "pattern": [1.25, 0.75, -0.125, 0.125, -0.125]})
            
    @staticmethod
    def plot_window(
        dxf_path: str,
        out_dwg: str,
        out_pdf: str,
        out_png: str,
        p_min: tuple,
        p_max: tuple,
        paper_size: str = "ANSI B (17.00 x 11.00 Inches)",
        orientation: str = "L",
        dpi: int = 300
    ) -> bool:
        """
        Plots a modelspace window using accoreconsole with acad.ctb and lineweights OFF.
        Converts the resulting PDF to a tightly cropped PNG at the specified DPI.
        """
        scr_path = os.path.join(os.path.dirname(dxf_path), "_temp_plot.scr")
        
        x1, y1 = p_min
        x2, y2 = p_max
        
        scr_lines = [
            '(setvar "EXPERT" 2)',
            '(setvar "CTAB" "Model")',
            f'DXFIN "{dxf_path}"',
            '-PLOT',
            'Y',
            'Model',
            'AutoCAD PDF (General Documentation).pc3',
            paper_size,
            'I',
            orientation,
            'N',
            'W',
            f'{x1},{y1}',
            f'{x2},{y2}',
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
            
        cmd = [ACCORECONSOLE, "/s", scr_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(scr_path):
            try:
                os.remove(scr_path)
            except Exception:
                pass
                
        if not os.path.exists(out_pdf):
            print(f"[CadPlotter ERROR] PDF plot failed. Return code: {res.returncode}")
            return False
            
        # Convert to high-res PNG
        pdf_doc = fitz.open(out_pdf)
        page = pdf_doc.load_page(0)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(out_png)
        pdf_doc.close()
        
        # Tightly auto crop margins
        im = Image.open(out_png)
        bbox = im.getbbox()
        if bbox:
            w, h = im.size
            pad = 25
            cb = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
            cropped = im.crop(cb)
            cropped.save(out_png)
            
        return True
