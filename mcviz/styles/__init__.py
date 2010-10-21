from styles import svg, simple, fancylines, linewidth_pt
from color import color, rainbow

styles = {}
styles["SVG"] = svg
styles["Simple"] = simple
styles["FancyLines"] = fancylines
styles["Color"] = color
styles["Rainbow"] = rainbow
styles["LineWidthPt"] = linewidth_pt

def list_styles():
    return sorted(styles.keys())

def apply_style(name, layout):
    styles[name](layout)

