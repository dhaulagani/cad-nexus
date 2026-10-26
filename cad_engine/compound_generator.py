r"""
cad_engine.compound_generator
Crystallized procedural compound plan generator:
- Fence polylines with non-touching 'X' symbols (6"x6" with 1.25" clearance)
- Strict decimal feet dimensioning with architectural tick marks
- Double swing and pedestrian swing gates with swing arcs
- Equipment bubble labels and modular equipment/foundation legend table
"""

import math
from typing import Tuple, List
import ezdxf
from ezdxf.enums import TextEntityAlignment

class CompoundGenerator:
    @staticmethod
    def draw_fence_line(
        msp,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        layer: str = "0",
        color: int = 7,
        cross_spacing: float = 96.0,
        cross_size: float = 6.0,
        gap: float = 1.25
    ):
        """
        Draws fence segments interrupted by non-touching 'X' crosses.
        """
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        L = math.hypot(dx, dy)
        if L < 24.0:
            msp.add_line(p1, p2, dxfattribs={"layer": layer, "color": color})
            return
            
        ux, uy = dx / L, dy / L
        vx, vy = -uy, ux
        
        n_crosses = max(1, int(round(L / cross_spacing)))
        actual_spacing = L / (n_crosses + 1)
        
        half_c = cross_size / 2.0
        half_gap = half_c + gap
        
        curr_pt = (x1, y1)
        for i in range(1, n_crosses + 1):
            cx = x1 + i * actual_spacing * ux
            cy = y1 + i * actual_spacing * uy
            
            seg_end = (cx - half_gap * ux, cy - half_gap * uy)
            msp.add_line(curr_pt, seg_end, dxfattribs={"layer": layer, "color": color})
            
            arm1_p1 = (cx - half_c * ux - half_c * vx, cy - half_c * uy - half_c * vy)
            arm1_p2 = (cx + half_c * ux + half_c * vx, cy + half_c * uy + half_c * vy)
            arm2_p1 = (cx - half_c * ux + half_c * vx, cy - half_c * uy - half_c * vy)
            arm2_p2 = (cx + half_c * ux - half_c * vx, cy + half_c * uy - half_c * vy)
            
            msp.add_line(arm1_p1, arm1_p2, dxfattribs={"layer": layer, "color": color})
            msp.add_line(arm2_p1, arm2_p2, dxfattribs={"layer": layer, "color": color})
            
            curr_pt = (cx + half_gap * ux, cy + half_gap * uy)
            
        msp.add_line(curr_pt, (x2, y2), dxfattribs={"layer": layer, "color": color})

    @staticmethod
    def draw_tick_dim(
        msp,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        offset: float,
        text: str,
        layer: str = "Dim Compound",
        tick_len: float = 6.0,
        text_h: float = 7.0
    ):
        """
        Draws architectural tick dimension line with decimal feet text.
        """
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        L = math.hypot(dx, dy)
        if L < 1e-4:
            return
        ux, uy = dx / L, dy / L
        vx, vy = -uy, ux
        
        d1 = (x1 + offset * vx, y1 + offset * vy)
        d2 = (x2 + offset * vx, y2 + offset * vy)
        
        ext_over = 4.0 if offset >= 0 else -4.0
        e1_start = (x1 + (2.0 if offset >= 0 else -2.0) * vx, y1 + (2.0 if offset >= 0 else -2.0) * vy)
        e1_end = (d1[0] + ext_over * vx, d1[1] + ext_over * vy)
        e2_start = (x2 + (2.0 if offset >= 0 else -2.0) * vx, y2 + (2.0 if offset >= 0 else -2.0) * vy)
        e2_end = (d2[0] + ext_over * vx, d2[1] + ext_over * vy)
        
        msp.add_line(e1_start, e1_end, dxfattribs={"layer": layer, "color": 7})
        msp.add_line(e2_start, e2_end, dxfattribs={"layer": layer, "color": 7})
        msp.add_line(d1, d2, dxfattribs={"layer": layer, "color": 7})
        
        t_arm = tick_len / math.sqrt(2.0)
        for dp in [d1, d2]:
            tx1 = dp[0] - t_arm * (ux - vx)
            ty1 = dp[1] - t_arm * (uy - vy)
            tx2 = dp[0] + t_arm * (ux - vx)
            ty2 = dp[1] + t_arm * (uy - vy)
            msp.add_line((tx1, ty1), (tx2, ty2), dxfattribs={"layer": layer, "color": 7})
            
        mx = (d1[0] + d2[0]) / 2.0 + 5.0 * vx
        my = (d1[1] + d2[1]) / 2.0 + 5.0 * vy
        rot = math.degrees(math.atan2(dy, dx))
        if rot > 90.0 or rot <= -90.0:
            rot = (rot + 180.0) % 360.0
            
        t = msp.add_text(
            text,
            dxfattribs={
                "layer": layer,
                "color": 7,
                "height": text_h,
                "rotation": rot,
                "style": "Standard"
            }
        )
        t.set_placement((mx, my), align=TextEntityAlignment.BOTTOM_CENTER)

    @staticmethod
    def draw_bubble(msp, cx: float, cy: float, text: str, radius: float = 10.0, layer: str = "TEXT"):
        msp.add_circle((cx, cy), radius, dxfattribs={"layer": layer, "color": 7})
        msp.add_text(
            text,
            dxfattribs={
                "layer": layer,
                "color": 7,
                "height": radius * 1.1,
                "style": "Standard"
            }
        ).set_placement((cx, cy), align=TextEntityAlignment.MIDDLE_CENTER)
