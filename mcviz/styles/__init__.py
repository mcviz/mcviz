from styles import (svg_setup, simple_colors, fancylines, linewidth_pt, 
    thicken_color)
from qcd import qcd_rgb, qcd_rainbow

styles = {}
styles["Color"] = simple_colors
styles["FancyLines"] = fancylines
styles["QCDColor"] = qcd_rgb
styles["QCDRainbow"] = qcd_rainbow
styles["LineWidthPt"] = linewidth_pt
styles["ThickenColor"] = thicken_color

def list_styles():
    return sorted(styles.keys())

def apply_style(name, layout):
    styles[name](layout)

