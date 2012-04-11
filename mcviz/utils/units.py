from .. import log; log = log.getChild(__name__)

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

energy_units = ("tev", "gev", "mev", "kev")
length_units = ("mm", "cm")


class Units(object):
    def __init__(self, string = None):
        if string is None: string = "GeV MM"
        self.energy_mag_string = ""
        self.energy_mag = 1
        self.length_mag_string = ""
        self.length_mag = 1
        self.auto = False

        units = string.replace(',',' ').split(' ')
        for unit in units:
            if unit.lower() == "auto":
                self.auto = True
            elif unit.lower() in energy_units:
                self.set_energy(unit)
            elif unit.lower() in length_units:
                self.set_length(unit)
            else: raise RuntimeError("unit {0} not recognised".format(unit))
        return

    def set_energy(self, string):
        """
        Set the global energy scale and scale factor
        """
        if not self.energy_mag_string:
            self.energy_mag_string = string
            if string.lower() == "gev": self.energy_mag = 1
            elif string.lower() == "mev": self.energy_mag = 0.001
            elif string.lower() == "kev": self.energy_mag = 0.000001
            elif string.lower() == "tev": self.energy_mag = 1000
            else: raise RuntimeError("unit {0} not recognised".format(string))
            log.debug("setting energy unit to {0} factor {1:g}".format(string, self.energy_mag))
        else:
            log.error("unit is already {0:s}, not overriding with {1:s}".format(self.energy_mag_string, string))

    def set_length(self, string):
        """
        Set the global length scale and scale factor
        """
        if not self.length_mag_string:
            self.length_mag_string = string
            if string.lower() == "mm": self.length_mag = 1
            elif string.lower() == "cm": self.length_mag = 10
            else: raise RuntimeError("unit {0} not recognised".format(string))
            log.debug("setting length unit to {0:s}".format(string))
        else:
            log.error("unit is already {0:s}, not overriding with {0:s}".format(self.length_mag_string, string))

    def pick_mag(self, value):
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

    def pick_energy_mag(self, value):
        """
        Take an energy in the input units, return it in an appropriate display unit
        """
        return self.pick_mag(value * self.energy_mag)

    def initial_check(self, initial_particle):
        """
        Check an incoming particle has a resonable energy.
        If units are automatic, the best units will be picked, else a warning is issued.
        """
        e = self.energy_mag * initial_particle.e
        log.verbose("initial particle of energy {0:.4g}{1:s}eV"
            .format(*self.pick_mag(e)))
        if e > 100000:
            new = self.pick_mag(e*0.0000001)
        elif e < 100:
            new = self.pick_mag(e*100)
        else:
            log.verbose("initial particle of energy {0:.4g}{1:s}eV"
                .format(*self.pick_mag(e)))
            return

        if self.auto:
            self.set_energy(new[1]+"eV")
            info = "Input has beam particle with an energy of {0:.4g}{1:s}eV"\
                       ", units have been changed to {new:s}eV"
            log.info(info.format(*self.pick_mag(initial_particle.e * self.energy_mag), new=new[1]))
        else:
            warning = "Input has beam particle with an energy of {0:.4g}{1:s}eV"\
                       ", consider setting --units={new:s}eV or auto if this is incorrect"
            log.warn(warning.format(*self.pick_mag(initial_particle.e * self.energy_mag), new=new[1]))
        return

if __name__ == '__main__':
    u = Units()
    def trial(value):
        print("{0:f} GeV is represented: {1:g}{2:s}eV".format(value, *u.pick_mag(value * energy_mag)))
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

