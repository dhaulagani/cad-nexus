"""
cad_engine.survey_parser
Modul ekstraksi dan validasi parameter survei otomatis (terinspirasi dari auto-parameter extraction CADAM).
Menjamin semua ukuran tower terstandarisasi dalam desimal feet dan bebas kesalahan input.
"""
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class TowerSectionParam:
    section_index: int
    h_bottom: float
    h_top: float
    d_bottom: float
    d_top: float

@dataclass
class AntennaCarrierParam:
    elevation: float
    carrier_name: str = ""
    azimuths: List[float] = field(default_factory=list)
    mount_type: str = "T-Arm" # Platform, T-Arm, Sector Frame, Pipe Mount

@dataclass
class TowerSurveyData:
    site_id: str
    site_name: str
    tower_type: str # Monopole, Lattice 3L, Lattice 4L, Guyed
    total_height: float # in decimal feet
    lightning_rod_h: float = 6.2 # in decimal feet
    lightning_rod_top_el: Optional[float] = None
    sections: List[TowerSectionParam] = field(default_factory=list)
    carriers: List[AntennaCarrierParam] = field(default_factory=list)
    base_plate_d: Optional[float] = None
    anchor_bolts_count: int = 12

class SurveyDataParser:
    """Parser & normalizer data survei telekomunikasi."""
    
    @staticmethod
    def parse_dimension_str(val: Any) -> float:
        """
        Mengonversi input (angka, string feet-inch, atau desimal) menjadi desimal feet standar.
        Contoh:
          - 60.04 -> 60.04
          - "60.04'" -> 60.04
          - "60'-0 1/2\"" -> 60.0417
          - "1' 9\"" -> 1.75
        """
        if isinstance(val, (int, float)):
            return float(val)
        
        s = str(val).strip().replace("’", "'").replace("”", '"')
        
        # Cek jika format desimal murni: "60.04" atau "60.04'"
        m_dec = re.match(r"^([\d\.]+)\s*'*$", s)
        if m_dec:
            return float(m_dec.group(1))
        
        # Cek format feet-inch: misal 60'-6" atau 1'-9 1/4"
        m_ft_in = re.match(r"^(\d+)'(?:-|\s*)(\d+)?(?:\s+(\d+)/(\d+))?\"?$", s)
        if m_ft_in:
            ft = float(m_ft_in.group(1))
            inches = float(m_ft_in.group(2) or 0)
            num = float(m_ft_in.group(3) or 0)
            den = float(m_ft_in.group(4) or 1)
            total_inches = inches + (num / den)
            return round(ft + (total_inches / 12.0), 4)
        
        # Fallback extract first float found
        m_any = re.search(r"(\d+(?:\.\d+)?)", s)
        if m_any:
            return float(m_any.group(1))
        return 0.0

    @classmethod
    def create_monopole(cls, site_id: str, site_name: str, total_height: Any, 
                        d_base: Any, d_top: Any, 
                        lightning_rod_h: Any = 6.20,
                        carriers: Optional[List[Dict[str, Any]]] = None) -> TowerSurveyData:
        """Helper pembuatan spesifikasi monopole standar tervalidasi."""
        h = cls.parse_dimension_str(total_height)
        db = cls.parse_dimension_str(d_base)
        dt = cls.parse_dimension_str(d_top)
        l_rod = cls.parse_dimension_str(lightning_rod_h)

        # Validasi dasar geometri
        if db < dt:
            # Toleransi jika user terbalik memasukkan top & base
            db, dt = dt, db

        sec = TowerSectionParam(
            section_index=1,
            h_bottom=0.0,
            h_top=h,
            d_bottom=db,
            d_top=dt
        )

        carrier_objs = []
        if carriers:
            for c in carriers:
                c_el = cls.parse_dimension_str(c.get("elevation", 0))
                carrier_objs.append(AntennaCarrierParam(
                    elevation=c_el,
                    carrier_name=c.get("name", ""),
                    mount_type=c.get("mount_type", "T-Arm")
                ))

        return TowerSurveyData(
            site_id=site_id,
            site_name=site_name,
            tower_type="Monopole",
            total_height=h,
            lightning_rod_h=l_rod,
            lightning_rod_top_el=round(h + l_rod, 2),
            sections=[sec],
            carriers=carrier_objs,
            base_plate_d=round(db * 1.5, 2)
        )
