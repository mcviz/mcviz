from styles import svg, simple, fancylines
from color import color, rainbow

styles = {}
styles["SVG"] = svg
styles["Simple"] = simple
styles["FancyLines"] = fancylines
styles["Color"] = color
styles["Rainbow"] = rainbow

def list_styles():
    return sorted(styles.keys())

def apply_style(name, layout):
    styles[name](layout)

