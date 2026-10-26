"""
cad_engine.parametric_tower
Modul pemodelan 3D parametrik solid dan proyeksi 2D otomatis (build123d + OpenCASCADE).
"""
import time
from typing import Dict, Any, Tuple, List
from build123d import *
import ezdxf

class ParametricMonopole:
    def __init__(self, height: float, d_base: float, d_top: float, lightning_rod_h: float = 6.2, lightning_rod_d: float = 0.16):
        self.height = height
        self.d_base = d_base
        self.d_top = d_top
        self.lightning_rod_h = lightning_rod_h
        self.lightning_rod_d = lightning_rod_d
        self._part = None

    def build_3d(self) -> Part:
        """Membangun model solid 3D sejati."""
        r_base = self.d_base / 2.0
        r_top = self.d_top / 2.0
        r_rod = self.lightning_rod_d / 2.0

        with BuildPart() as b:
            # 1. Badan Monopole (taper frustum cone)
            Cone(bottom_radius=r_base, top_radius=r_top, height=self.height)
            # 2. Lightning Rod di puncak
            with Locations((0, 0, self.height)):
                Cylinder(radius=r_rod, height=self.lightning_rod_h)

        self._part = b.part
        return self._part

    def project_top_view(self) -> Tuple[List[Dict[str, Any]], float]:
        """
        Melakukan proyeksi ortografis tampak atas (Plan View).
        Mengembalikan daftar lingkaran (radius, center) dan waktu proses.
        """
        t0 = time.time()
        if self._part is None:
            self.build_3d()

        # Proyeksi tampak atas dari Z positif
        visible, hidden = self._part.project_to_viewport(Vector(0, 0, 1000))
        
        circles = []
        for edge in visible.edges():
            if edge.geom_type == GeomType.CIRCLE:
                # Ambil radius dari length (keliling = 2 * pi * r)
                radius = edge.length / (2 * 3.141592653589793)
                circles.append({
                    "radius": radius,
                    "diameter": radius * 2,
                    "center": (0.0, 0.0)
                })

        # Urutkan dari diameter terkecil ke terbesar
        circles.sort(key=lambda c: c["radius"])
        elapsed = time.time() - t0
        return circles, elapsed

    def create_top_view_block(self, doc: ezdxf.document.Drawing, block_name: str = "TOWER_TOP_VIEW"):
        """Menambahkan blok tampak atas ke dokumen DXF untuk dipakai di Page-02 (Compound)."""
        circles, _ = self.project_top_view()
        block = doc.blocks.new(name=block_name)
        
        # Gambar lingkaran-lingkaran proyeksi
        # Outer base
        if len(circles) >= 3:
            block.add_circle((0, 0), circles[-1]["radius"], dxfattribs={"layer": "C-TOWR", "color": 3}) # Green
            # Top pole
            block.add_circle((0, 0), circles[-2]["radius"], dxfattribs={"layer": "C-TOWR", "color": 3})
            # Lightning rod
            block.add_circle((0, 0), circles[0]["radius"], dxfattribs={"layer": "C-TOWR", "color": 1}) # Red center
        
        # Tambah garis sumbu / crosshair
        max_r = circles[-1]["radius"] if circles else self.d_base / 2.0
        ext = max_r * 1.3
        block.add_line((-ext, 0), (ext, 0), dxfattribs={"layer": "C-TOWR-CLINE", "color": 1})
        block.add_line((0, -ext), (0, ext), dxfattribs={"layer": "C-TOWR-CLINE", "color": 1})
        
        return block
