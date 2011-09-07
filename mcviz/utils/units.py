units = [("T", 1000000.),
         ("G", 1000.),
	 ("M", 1.),
	 ("k", 0.001),
	 ("", 0.000001),
	 ("m", 0.000001),
	 ("u", 0.000000001),
	 ("n", 0.000000000001),
	 ("p", 0.000000000000001)
	 ]

CURRENT_ENERGY_MAG_STRING = "M"
CURRENT_ENERGY_MAG = 1

def pick_mag(value):
    """
    Take an energy in MeV and return it in the biggest unit possible
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

def energy_mag(value):
    return pick_mag(value * CURRENT_ENERGY_MAG)

if __name__ == '__main__':
    def trial(value):
        print("%f MeV is represented:" %value)
        print("    %.4g %seV" %pick_mag(value))
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

