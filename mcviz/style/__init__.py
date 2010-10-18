from styles import svg, simple, fancylines
from color import color, rainbow

styles = {}
styles["svg"] = svg
styles["simple"] = simple
styles["fancylines"] = fancylines
styles["color"] = color
styles["rainbow"] = rainbow

def list_styles():
    return sorted(styles.keys())

def apply_style(name, layout):
    styles[name](layout)
