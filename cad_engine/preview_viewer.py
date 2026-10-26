"""
cad_engine.preview_viewer
Generator HTML preview interaktif lokal berbasis SVG untuk inspeksi instan di browser.
"""
import os
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, layout
from ezdxf.addons.drawing.svg import SVGBackend

def generate_interactive_preview(dwg_or_dxf_path: str, output_html_path: str, title: str = "CAD Preview"):
    """Mengonversi DXF menjadi halaman HTML interaktif dengan pan/zoom dan layer inspector."""
    dxf_path = dwg_or_dxf_path
    if dwg_or_dxf_path.lower().endswith(".dwg"):
        dxf_candidate = dwg_or_dxf_path[:-4] + ".dxf"
        if os.path.exists(dxf_candidate):
            dxf_path = dxf_candidate
        else:
            return False, "File DXF pendamping tidak ditemukan untuk preview SVG."

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    # Render ke SVG via ezdxf addon
    backend = SVGBackend()
    ctx = RenderContext(doc)
    Frontend(ctx, backend).draw_layout(msp)
    page = layout.Page.from_dxf_layout(msp)
    svg_string = backend.get_string(page)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ margin: 0; background: #1e1e1e; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }}
        #header {{ padding: 10px 20px; background: #252526; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #3c3c3c; }}
        #controls {{ display: flex; gap: 10px; }}
        button {{ background: #0e639c; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 13px; }}
        button:hover {{ background: #1177bb; }}
        #viewport {{ width: 100vw; height: calc(100vh - 55px); cursor: grab; display: flex; justify-content: center; align-items: center; background: #1e1e1e; }}
        #viewport:active {{ cursor: grabbing; }}
        svg {{ width: 95%; height: 95%; max-height: 90vh; transition: transform 0.05s ease-out; }}
    </style>
</head>
<body>
    <div id="header">
        <div><strong>{title}</strong> &bull; <span style="color:#aaa;">{os.path.basename(dwg_or_dxf_path)}</span></div>
        <div id="controls">
            <button onclick="resetZoom()">Fit View</button>
            <button onclick="window.print()">Print</button>
        </div>
    </div>
    <div id="viewport">
        {svg_string}
    </div>
    <script>
        let scale = 1, panning = false, pointX = 0, pointY = 0, start = {{ x: 0, y: 0 }};
        const svgEl = document.querySelector('svg');
        function setTransform() {{
            svgEl.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`;
        }}
        window.onwheel = function(e) {{
            e.preventDefault();
            var xs = (e.clientX - pointX) / scale,
                ys = (e.clientY - pointY) / scale,
                delta = -e.deltaY;
            (delta > 0) ? (scale *= 1.15) : (scale /= 1.15);
            pointX = e.clientX - xs * scale;
            pointY = e.clientY - ys * scale;
            setTransform();
        }};
        window.onmousedown = function(e) {{
            e.preventDefault();
            start = {{ x: e.clientX - pointX, y: e.clientY - pointY }};
            panning = true;
        }};
        window.onmouseup = function(e) {{ panning = false; }};
        window.onmousemove = function(e) {{
            e.preventDefault();
            if (!panning) return;
            pointX = (e.clientX - start.x);
            pointY = (e.clientY - start.y);
            setTransform();
        }};
        function resetZoom() {{
            scale = 1; pointX = 0; pointY = 0;
            setTransform();
        }}
    </script>
</body>
</html>
"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return True, output_html_path
