
import math
import argparse

# "Constants"
k     = 11     # J m^-2 K^-1 s^-1 - Thermal diffusivity of the air??
c_g   = 1.4 * 10**5 # J m^-2 K^-1 - Soil heat capacity
S     = 1368   # W m^-2 - Solar irradiance
d_bar = 1.50 * 10**11 # m - Mean distance from sun to the Earth
d_y   = 365.25 # - days in year
d_s   = 173    # - solstice day


def f_to_k(f):
    '''Convert Fahrenheit to Kelvin'''

    k = (f + 459.67) * 5/9

    return k


def k_to_f(k):
    '''Convert Kelvin to Fahrenheit'''

    f = (k - 273.15) * 9/5 + 32

    return f


def c_to_k(c):
    '''Convert Celsius to Kelvin'''

    k = c + 273.15

    return k


def k_to_c(k):
    '''Convert Kelvin to Celsius'''

    c = k - 273.15

    return c


def local_hour(h_utc, lon):
    '''Calculate local hour of the sun'''

    h = (h_utc - 12) * math.pi / 12 + lon * math.pi / 180
    print "h:\t", h

    return h


def declination(doy):
    '''Calculate declination angle'''

    delta = 23.45 * math.cos(2*math.pi*(doy - d_s)/d_y)
    print "delta:\t", delta

    return delta


def zenith(doy, h_utc, lat, lon):
    '''Calculate zenith angle'''

    h   = local_hour(h_utc, lon)
    dec = declination(doy)

    zenith = math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(h)
    print "zenith:\t", zenith

    return zenith


def t_to_utc(t):
    '''Convert hour to UTC'''

    # NOTE: Hardcoded for Seattle, WA
    utc = t + 7

    return utc


def solar_rad(args):
    '''Calculate incoming solar radiation at latitude and longitude'''

    h_utc = t_to_utc(16)
    doy   = 229
    zen   = zenith(doy, h_utc, float(args.latitude), float(args.longitude))
    #zen   = - zenith(doy, h_utc, float(args.latitude), float(args.longitude))
    #print zen

    a     = 0.2 # albedo
    tau_s = 0.8 # atmospheric transmissivity

    if zen < 0:
        Q_S = 0
    else:
        # Note: Ignoring elliptical orbit
        #Q_S = S * d_bar**2 * (1 - a) * zen * tau_s
        Q_S  = S * (1.5)**2 * (1 - a) * zen * tau_s

    print "Q_S:\t", Q_S

    return Q_S


def main(args):
    '''Calculate surface temperature at latitude and longitude'''

    Q_S = solar_rad(args) # Incoming solar radiation
    Q_Ld = 0              # Downwelling longwave radiation
    Q_Lu = 0              # Upwelling longwave radiation
    Q_H  = 0              # Sensible heat flux
    Q_E  = 0              # Latent heat flux
    T_r  = f_to_k(54)     # K reservoir temperature
    T_g_init = f_to_k(72) # K initial ground temperature

    T_g = (Q_S + Q_Ld - Q_Lu - Q_H - Q_E - k*(T_g_init - T_r)) 
    #T_g = (Q_S + Q_Ld - Q_Lu - Q_H - Q_E - k*(T_g_init - T_r)) / c_g
    # last term equivalent to Q_G the ground heat flux

    print "T_g:\t", T_g
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 
            'Calculate surface temperature at latitude and longitude')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-la', '--latitude',  help='Specify latitude', required=True)
    required.add_argument('-lo', '--longitude', help='Specify longitude', required=True)
    optional.add_argument('-ho', '--hour', help='Specify hour of day', default=12)
    parser._action_groups.append(optional)
    args = parser.parse_args()

    main(args)
