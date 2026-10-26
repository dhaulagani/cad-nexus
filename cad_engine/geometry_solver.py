"""
cad_engine.geometry_solver
Perhitungan geometri presisi dan pencegahan tabrakan teks/dimensi.
"""
from typing import Tuple, List, Dict, Any

class TowerGeometrySolver:
    """Menghitung dimensi dan koordinat eksak untuk struktur tower telekomunikasi."""
    
    @staticmethod
    def calculate_taper_diameter(z: float, z_base: float, z_top: float, d_base: float, d_top: float) -> float:
        """Menghitung diameter pole pada elevasi z tertentu dengan interpolasi linier presisi."""
        if z <= z_base:
            return d_base
        if z >= z_top:
            return d_top
        ratio = (z - z_base) / (z_top - z_base)
        return d_base + ratio * (d_top - d_base)

    @staticmethod
    def get_dimension_clearance(text_height: float, margin_ratio: float = 0.35) -> float:
        """Menghitung margin aman agar teks dimensi tidak menempel/menabrak garis referensi."""
        return text_height * margin_ratio

    @staticmethod
    def compute_elevation_tick(center_x: float, pole_radius: float, tick_extension: float = 0.5) -> Tuple[float, float]:
        """Menghitung rentang garis elevasi horizontal di luar badan pole."""
        x_left = center_x - pole_radius - tick_extension
        x_right = center_x + pole_radius + tick_extension
        return x_left, x_right
