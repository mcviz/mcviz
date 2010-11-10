
def rainbow_color(hue, brightness = 0.5):
    """ get hue spectrum; hue in [0,1]:
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

    num = int(hue * 6)
    remainder = hue - num/6
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
    #print >> stderr, "%.3f %.3f => %s" % (hue,brightness, res)
    return res
