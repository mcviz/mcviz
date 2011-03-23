from __future__ import division

from random import shuffle, seed
    
from mcviz.utils import rainbow_color

from mcviz.tools import Style, Arg

@Style.decorate("QCDRGB")
def qcd_rgb(layout):
    """
    Apply RGBCMY colours arbitrarily according to QCD color.
    """
    
    colors = [e.item.color for e in layout.edges]
    anticolors = [e.item.anticolor for e in layout.edges]
    unique_colors = sorted(list(set(colors + anticolors)))
    cmap = dict(zip(unique_colors, ["red", "lime", "blue"]*(len(unique_colors)//3+1)))
    amap = dict(zip(unique_colors, ["cyan", "magenta", "yellow"]*(len(unique_colors)//3+1)))
    set_color(layout, cmap, amap) 

@Style.decorate("QCDRainbow")
def qcd_rainbow(layout):
    """
    Colour particles according to their QCD color. Each colour+anticolour pair 
    gets a unique hue, with anti-colours brighter than the colours.
    """
    colors = [e.item.color for e in layout.edges]
    anticolors = [e.item.anticolor for e in layout.edges]
    unique_colors = sorted(list(set(colors + anticolors)))
    color_values = [i/len(unique_colors) for i in range(len(unique_colors))]
    seed(42) # Determinism, please.
    shuffle(color_values)
    cmap = dict([(unique_colors[i], rainbow_color(color_values[i], 0.5)) for i in range(len(unique_colors))])
    amap = dict([(unique_colors[i], rainbow_color(color_values[i], 0.8)) for i in range(len(unique_colors))])
    set_color(layout, cmap, amap)

def set_color(layout, cmap, amap):
    for edge in layout.edges:
        particle = edge.item
        if particle.gluon:
            edge.style_line_type = "multigluon"
            edge.style_args["color"] = cmap[particle.color]
            edge.style_args["anticolor"] = amap[particle.anticolor]
        elif particle.colored:
            if particle.color:
                edge.style_args["stroke"] = cmap[particle.color]
                edge.style_args["fill"] = cmap[particle.color]
            else:
                edge.style_args["stroke"] = amap[particle.anticolor]
                edge.style_args["fill"] = amap[particle.anticolor]



