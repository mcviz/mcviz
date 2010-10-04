from base import Style
from svg import SVGStyle
from simple import SimpleStyle
from strong import StrongStyle
from rainbow import RainbowStyle

styles = {}
styles["base"] = Style
styles["svg"] = SVGStyle
styles["simple"] = SimpleStyle
styles["strong"] = StrongStyle
styles["rainbow"] = RainbowStyle
default = "svg"

def list_styles():
    return sorted(styles.keys())

def get_style(name):
    if name is None:
        return styles[default]
    return styles[name]
