from base import Style

styles = {}
styles["base"] = Style
default = "base"

def list_styles():
    return sorted(styles.keys())

def get_style(name):
    if name is None:
        return styles[default]
    return styles[name]
