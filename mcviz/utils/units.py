from logging import getLogger; log = getLogger("mcviz.utils.units")

"""
Module to look after units.
Defaults are GeV and MM.
"""

units = [("T", 1000.),
         ("G", 1.),
         ("M", 0.001),
         ("k", 0.000001),
         ("" , 0.000001),
         ("m", 0.000000001),
         ("u", 0.000000000001),
         ("n", 0.000000000000001),
         ("p", 0.000000000000000001)]

energy_mag_string = ""
energy_mag = 1

length_mag_string = ""
length_mag = 1

def set_energy(string):
    """
    Set the global energy scale and scale factor
    """
    global energy_mag
    global energy_mag_string
    if not energy_mag_string:
        energy_mag_string = string
        if string.lower() == "gev": energy_mag = 1
        elif string.lower() == "mev": energy_mag = 0.001
        elif string.lower() == "kev": energy_mag = 0.000001
        else: log.error("unit %s not recognised" %string)
        log.info("setting energy unit to %s factor %f" %(string, energy_mag))
    else:
        log.info("unit is already %s, not overriding with %s" %(energy_mag_string, string))

def set_length(string):
    """
    Set the global length scale and scale factor
    """
    global length_mag
    global length_mag_string
    if not length_mag_string:
        log.info("setting length unit to %s" %string)
        length_mag_string = string
        if string.lower() == "mm": length_mag = 1
        elif string.lower() == "cm": length_mag = 10
    else:
        log.info("unit is already %s, not overriding with %s" %(length_mag_string, string))

def pick_mag(value):
    """
    Take an energy in GeV and return it in the biggest unit possible
    """
    selected_unit = ""
    selected_val = 0.000001
    for unit, val in units:
        if value > val:
            selected_unit = unit
            selected_val = val
            break
    selected_val = value / selected_val
    return (selected_val, selected_unit)

def pick_energy_mag(value):
    """
    Take an energy in the input units, return it in an appropriate display unit
    """
    return pick_mag(value * energy_mag)

if __name__ == '__main__':
    CURRENT_ENERGY_MAG = 1
    def trial(value):
        print("%f GeV is represented:" %value)
        print("    %.4g %seV" %energy_mag(value))
    trial(1234567890.123456789)
    trial(34567890.123456789)
    trial(547890.123456789)
    trial(7890.123456789)
    trial(90.123456789)
    trial(0.123456789123456789)
    trial(0.003456789123456789)
    trial(0.000056789123456789)
    trial(0.000000789123456789)
    trial(0.000000009123456789)
    trial(0.000000000023456789)
    trial(0.000000000000456789)
    trial(0.000000000000006789)
    trial(0.000000000000000089)

