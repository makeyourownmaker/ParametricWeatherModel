
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import math
import argparse


class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return self.start <= other <= self.end


def f_to_k(f):
    '''
    Convert Fahrenheit to Kelvin
    '''

    k = (f + 459.67) * 5 / 9

    return k


def k_to_f(k):
    '''
    Convert Kelvin to Fahrenheit
    '''

    f = (k - 273.15) * 9 / 5 + 32

    return f


def c_to_k(c):
    '''
    Convert Celsius to Kelvin
    '''

    k = c + 273.15

    return k


def k_to_c(k):
    '''
    Convert Kelvin to Celsius
    '''

    c = k - 273.15

    return c


def downwelling_rad(args):
    '''
    Calculate downwelling longwave radiation
    '''

    Q_Ld = 0

    print("Q_Ld:\t", Q_Ld)

    return Q_Ld


def upwelling_rad(args):
    '''
    Calculate upwelling longwave radiation
    '''

    Q_Lu = 0

    print("Q_Lu:\t", Q_Lu)

    return Q_Lu


def sensible_heat_flux(args):
    '''
    Calculate sensible heat flux
    '''

    Q_H = 0

    print("Q_H:\t", Q_H)

    return Q_H


def latent_heat_flux(args):
    '''
    Calculate latent heat flux
    '''

    Q_E = 0

    print("Q_E:\t", Q_E)

    return Q_E


def local_hour(h_utc, lon):
    '''
    Calculate local hour of the sun
    '''

    h = (h_utc - 12) * math.pi / 12 + lon * math.pi / 180
    print("h:\t", h)

    return h


def declination(args):
    '''
    Calculate declination angle
    '''

    # "Constants"
    d_y = 365.25

    d_s = args.day_of_solstice
    doy = args.day_of_year

    delta = 23.45 * math.cos(2 * math.pi * (doy - d_s) / d_y)
    print("delta:\t", delta)

    return delta


def zenith(args):
    '''
    Calculate zenith angle
    '''

    lat   = args.latitude
    lon   = args.longitude
    h_utc = t_to_utc(args)
    h     = local_hour(h_utc, lon)
    dec   = declination(args)

    zenith = math.sin(lat) * math.sin(dec) + \
             math.cos(lat) * math.cos(dec) * math.cos(h)

    print("zenith:\t", zenith)

    return zenith


def t_to_utc(args):
    '''
    Convert hour to UTC
    '''

    utc = args.hour + args.utc_offset

    return utc


def solar_rad(args):
    '''
    Calculate incoming solar radiation at latitude and longitude
    '''

    # "Constants"
    S = 1368                 # W m^-2 - Solar irradiance
    # d_bar = 1.50 * 10**11  # m      - Mean distance from sun to Earth
    eor = 1.5  # Elliptical orbit ratio NOTE Ignoring elliptical orbit for now

    tau_s = args.transmissivity  # Atmospheric transmissivity
    a     = args.albedo

    # zen = zenith(args)
    zen = - zenith(args)

    if zen < 0:
        Q_S = 0
    else:
        # NOTE: Ignoring elliptical orbit for now
        Q_S = S * eor**2 * (1 - a) * zen * tau_s

    print("Q_S:\t", Q_S)

    return Q_S


def main(args):
    '''
    Calculate surface temperature at latitude and longitude
    '''

    # "Constants"
    c_g = 1.4 * 10**5  # J m^-2 K^-1      - Soil heat capacity
    K   = 11           # J m^-2 K^-1 s^-1 - Thermal diffusivity of the air

    Q_S  = solar_rad(args)                # Incoming solar radiation
    Q_Ld = downwelling_rad(args)          # Downwelling longwave radiation
    Q_Lu = upwelling_rad(args)            # Upwelling longwave radiation
    Q_H  = sensible_heat_flux(args)       # Sensible heat flux
    Q_E  = latent_heat_flux(args)         # Latent heat flux
    T_r  = f_to_k(args.ground_temp)       # K - Reservoir temperature
    T_g_init = f_to_k(args.surface_temp)  # K - Initial ground temperature

    d_t   = args.forecast_period
    d_T_g = (Q_S + Q_Ld - Q_Lu - Q_H - Q_E - K * (T_g_init - T_r)) * d_t / c_g
    # last term approximates Q_G the ground heat flux

    T_g = k_to_f(T_g_init + d_T_g)

    print("d_T_g:\t", d_T_g, "K")
    print("T_g:\t", T_g, "F")

    return 0


# Parameters to add:
#   Required:
#     * Initial surface air temperature (Celsius)
#     * Ground reservoir temperature (Celsius)
#   Optional:
#     * Precipitable water
#     * Bowen ratio
#     * Atmospheric emissivity
#     * Verbose option

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Calculate surface temperature at latitude and longitude')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-la', '--latitude',
            help='Specify latitude (-90 to 90; plus for north, minus for south)',
            required=True, type=float, choices=[Range(-90.0, 90.0)])
    required.add_argument('-lo', '--longitude',
            help='Specify longitude (-180 to 180; plus for east, minus for west)',
            required=True, type=float, choices=[Range(-180.0, 180.0)])
    required.add_argument('-da', '--day_of_year',
            help='Specify Julian day of year (1 to 365)',
            required=True, type=int, choices=[Range(1, 366)])
    required.add_argument('-gt', '--ground_temp',
            help='Specify ground reservoir temperature (Fahrenheit only)',
            type=float)
    required.add_argument('-st', '--surface_temp',
            help='Specify initial surface air temperature (Fahrenheit only)',
            type=float)

    # optional.add_argument('-v', '--verbose', help='Print additional information')
    optional.add_argument('-ho', '--hour',
            help='Specify hour of day (0 to 24) default=12',
            default=12, type=int, choices=range(0, 25))
    optional.add_argument('-al', '--albedo',
            help='Specify albedo (0 to 1) default=0.3',
            default=0.3, type=float, choices=[Range(0.0, 1.0)])
    optional.add_argument('-cf', '--cloud_fraction',
            help='Specify cloud fraction (0 to 1) default=0',
            default=0, type=float, choices=[Range(0.0, 1.0)])
    optional.add_argument('-ds', '--day_of_solstice',
            help='Specify day of solstice (172 or 173) default=173',
            default=173, type=int, choices=range(172, 174))
    optional.add_argument('-uo', '--utc_offset',
            help='Specify UTC offset (-12 to 12) default=0',
            default=0, type=int, choices=range(-12, 13))
    optional.add_argument('-fp', '--forecast_period',
            help='Specify forecast period in seconds (600 to 3600) default=3600',
            default=3600, type=int, choices=[Range(600, 3601)])
    optional.add_argument('-tr', '--transmissivity',
            help='Specify atmospheric transmissivity default=0.8',
            default=0.8, type=float)

    parser._action_groups.append(optional)
    args = parser.parse_args()

    main(args)
