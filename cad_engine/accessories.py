"""
cad_engine.accessories
Koleksi komponen parametrik telekomunikasi (terinspirasi dari library BOSL2/MCAD pada CADAM).
Menyediakan blok dan geometri standar: Base Plate, Antenna Mount, Bolt Circle, dan Sumbu Azimuth.
"""
import math
from typing import Dict, Any, List, Tuple
import ezdxf

class TelecomAccessories:
    """Library komponen CAD parametrik standar telekomunikasi."""
    
    @staticmethod
    def draw_base_plate_top_view(block: ezdxf.layouts.BlockLayout, 
                                 base_plate_d: float, 
                                 pole_d: float, 
                                 bolt_count: int = 12, 
                                 bolt_circle_ratio: float = 1.25,
                                 bolt_hole_d: float = 0.15):
        """
        Menggambar tampak atas Base Plate lengkap dengan lingkaran baut angkur dan lubang tengah.
        Digunakan untuk Page-02 (Compound Plan) dan Detail Base Plate.
        """
        r_plate = base_plate_d / 2.0
        r_pole = pole_d / 2.0
        r_bc = (pole_d * bolt_circle_ratio) / 2.0
        r_bolt = bolt_hole_d / 2.0

        # 1. Plat Dasar (Lingkaran luar)
        block.add_circle((0, 0), r_plate, dxfattribs={"layer": "C-TOWR", "color": 3}) # Green
        
        # 2. Dinding Luar Pole
        block.add_circle((0, 0), r_pole, dxfattribs={"layer": "C-TOWR", "color": 3})

        # 3. Lingkaran Baut Angkur (Bolt Circle Line)
        block.add_circle((0, 0), r_bc, dxfattribs={"layer": "C-TOWR-CLINE", "color": 1}) # Red center line

        # 4. Lubang-lubang Baut (Anchor Bolts)
        angle_step = (2 * math.pi) / bolt_count
        for i in range(bolt_count):
            angle = i * angle_step
            bx = r_bc * math.cos(angle)
            by = r_bc * math.sin(angle)
            block.add_circle((bx, by), r_bolt, dxfattribs={"layer": "C-TOWR", "color": 4}) # Cyan bolts

    @staticmethod
    def draw_antenna_mount_elevation(msp: ezdxf.layouts.Modelspace, 
                                     center_x: float, 
                                     elevation_z: float, 
                                     pole_width: float, 
                                     mount_width: float = 6.0, 
                                     pipe_height: float = 6.0):
        """
        Menggambar tampak samping dudukan antena (T-Arm / Sector Frame / Pipe Mount) pada Page-07.
        """
        half_w = mount_width / 2.0
        pipe_r = 0.12 # 2.8" pipe
        
        # Garis horizontal boom mount
        y_center = elevation_z
        x_left = center_x - half_w
        x_right = center_x + half_w
        msp.add_line((x_left, y_center), (x_right, y_center), dxfattribs={"layer": "C-TOWR-EQPM", "color": 4})
        
        # Antenna pipes di ujung kiri, tengah, kanan
        for x_pos in [x_left, center_x - (half_w * 0.5), center_x + (half_w * 0.5), x_right]:
            # Jika pipa berada di luar badan pole
            if abs(x_pos - center_x) > (pole_width / 2.0):
                y_top = y_center + (pipe_height / 2.0)
                y_bot = y_center - (pipe_height / 2.0)
                # Garis pipa antena
                msp.add_line((x_pos, y_bot), (x_pos, y_top), dxfattribs={"layer": "C-TOWR-EQPM", "color": 4})
