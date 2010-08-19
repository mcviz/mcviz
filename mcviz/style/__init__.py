from base import Style
from svg import SVGStyle

styles = {}
styles["base"] = Style
styles["svg"] = SVGStyle
default = "svg"

def list_styles():
    return sorted(styles.keys())

def get_style(name):
    if name is None:
        return styles[default]
    return styles[name]
