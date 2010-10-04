from __future__ import division

from .svg import SVGStyle
from .strong import StrongStyle

from random import shuffle

def rainbow_color(chromacity, brightness = 0.5):
    """ get chromacity spectrum; chromacity in [0,1]:
        red ff-ff; green 00-ff; blue 00-00
        red ff-00; green ff-ff; blue 00-00
        red 00-00; green ff-ff; blue 00-ff
        red 00-00; green ff-00; blue ff-ff
        red 00-ff; green 00-00; blue ff-ff
        red ff-ff; green 00-00; blue ff-00
    """
    min_val = 0x00 if brightness < 0.5 else 2 * (brightness - 0.5) * 255
    max_val = 0xff if brightness > 0.5 else 2 * brightness * 255
    c_range = max_val - min_val

    num = int(chromacity * 6)
    remainder = chromacity - num/6
    fixed_color = ((num + 1) // 2) % 3
    run_up = (num % 2 == 0)
    run_color = (num // 2 + 1 - (0 if run_up else 1)) % 3

    def get_val(color):
        if color == fixed_color:
            return max_val
        elif color == run_color:
            if run_up:
                return min_val + c_range * remainder
            else:
                return max_val - c_range * remainder
            return c_val
        else:
            return min_val

    res =  "#" + "".join('%02x' % get_val(c) for c in (0, 1, 2))
    #from sys import stderr
    #print >> stderr, "%.3f %.3f => %s" % (chromacity,brightness, res)
    return res

class RainbowStyle(StrongStyle):

    def paint(self):
        colors = [e.item.color for e in self.layout.edges]
        anticolors = [e.item.anticolor for e in self.layout.edges]
        unique_colors = sorted(list(set(colors + anticolors)))
        color_values = [i/len(unique_colors) for i in range(len(unique_colors))]
        shuffle(color_values)
        self.cmap = dict([(unique_colors[i], rainbow_color(color_values[i], 0.5)) for i in range(len(unique_colors))])
        self.amap = dict([(unique_colors[i], rainbow_color(color_values[i], 0.8)) for i in range(len(unique_colors))])
        return SVGStyle.paint(self)
    
    def paint_particle(self, particle): 
        return super(RainbowStyle, self).paint_particle(particle)
