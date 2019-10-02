
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import math
import argparse
import datetime


class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end   = end

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


def atmospheric_emissivity(args):
    '''
    Calculate atmospheric emissivity
    '''

    # Equation 2.7  Page 26
    w_p = args.precip_water
    e_a = 0.725 + 0.17 * math.log10(w_p)

    return e_a


def downwelling_rad(args):
    '''
    Calculate downwelling longwave radiation
    '''

    # Constants
    sigma = 5.67 * 10**(-8)  # W m^-2 K^-4 - Stefan-Boltzmann constant

    b   = args.cloud_fraction  # Cloud fraction
    e_g = args.emissivity      # Surface emissivity
    T_a = f_to_k(args.surface_temp)  # Temperature at 40 hPa above the ground surface
    T_c = f_to_k(args.surface_temp)  # Temperature at the base of the cloud
    # NOTE Assuming T_a equals surface_temp which it very definitely does not
    # NOTE Assuming T_c equals surface_temp which it very definitely does not

    e_a = atmospheric_emissivity(args)

    # Equation 2.8  Page 27
    Q_Ld = e_g * e_a * sigma * T_a**4 + b * e_g * (1 - e_a) * sigma * T_c**4

    print_v("Q_Ld:\t", Q_Ld)

    return Q_Ld


def upwelling_rad(args):
    '''
    Calculate upwelling longwave radiation
    '''

    # Constants
    sigma = 5.67 * 10**(-8)  # W m^-2 K^-4 - Stefan-Boltzmann constant

    e_g = args.emissivity  # Surface emissivity
    T_g = f_to_k(args.ground_temp)

    # Equation 2.5  Page 25
    Q_Lu = e_g * sigma * T_g**4

    print_v("Q_Lu:\t", Q_Lu)

    return Q_Lu


def sensible_heat_flux(args):
    '''
    Calculate sensible heat flux
    '''

    # Constants
    k_a = 2.5 * 10**(-2)  # W m^-1 K^-1 s^-1 - Thermal conductivity of air

    T_g = f_to_k(args.ground_temp)
    T_s = f_to_k(args.surface_temp)

    # Based on Equation 2.18  Page 30
    Q_H = - k_a * (T_g - T_s)

    print_v("Q_H:\t", Q_H)

    return Q_H


def latent_heat_flux(args, Q_H):
    '''
    Calculate latent heat flux using Bowen ratio
    '''

    # Based on the definition on Page 22
    Q_E = Q_H * args.bowen_ratio

    print_v("Q_E:\t", Q_E)

    return Q_E


def local_hour(args):
    '''
    Calculate local hour of the sun
    '''

    # TODO Fix local hour of the sun calculation
    # Didn't get the below equation for h to work
    # lon   = args.longitude
    # h_utc = hour_to_utc(args)
    # Equation 2.4  Page 24
    # h = (h_utc - 12) * math.pi / 12 + lon * math.pi / 180
    # print_v("h:\t", h)

    # See following web page for explanation of each equation
    # https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time
    # EoT is an approximation accurate to within 1/2 minute
    LSTM = 15 * args.utc_offset
    B    = math.radians(360 * (args.day_of_year - 81) / 365.25)
    EoT  = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    TC  = 4 * (args.longitude - LSTM) + EoT
    LST = args.hour + TC / 60
    HRA = 15 * (LST - 12)
    print_v("LSTM:\t", LSTM)
    print_v("B:\t", B)
    print_v("EOT:\t", EoT)
    print_v("TC:\t", TC)
    print_v("LST:\t", LST)
    print_v("HRA:\t", HRA)

    return HRA


def declination(args):
    '''
    Calculate declination angle
    '''

    # "Constants"
    d_y = 365.25

    d_s = args.day_of_solstice
    doy = args.day_of_year

    # Equation 2.3  Page 24
    delta = 23.45 * math.cos(2 * math.pi * (doy - d_s) / d_y)
    print_v("delta:\t", delta)

    return delta


def zenith(args):
    '''
    Calculate cosine of zenith angle
    '''

    h   = math.radians(local_hour(args))
    lat = math.radians(args.latitude)
    dec = math.radians(declination(args))

    # Equation 2.2  Page 22
    zenith = math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(h)

    print_v("zenith:\t", zenith)

    return zenith


def hour_to_utc(args):
    '''
    Convert hour to UTC
    '''

    utc_time = datetime.datetime.strptime(str(args.hour), "%H") + datetime.timedelta(hours=args.utc_offset)
    utc_hour = utc_time.hour
    print_v("h_utc:\t", utc_hour)

    return utc_hour


def elliptical_orbit_ratio(args):
    '''
    Calculate elliptical orbit ratio
    '''

    # See following web page for explanation
    # https://physics.stackexchange.com/q/177949
    # NOTE This is an approximation
    #      Earth reaches perihelion between 4th & 6th of January depending on year
    doy   = args.day_of_year
    angle = math.radians(0.9856 * (doy - 4))
    eor   = 1 / (1 - 0.01672 * math.cos(angle))

    return eor


def solar_rad(args):
    '''
    Calculate incoming solar radiation at latitude, longitude, day and hour
    '''

    # "Constants"
    S = 1368  # W m^-2 - Solar irradiance

    eor = elliptical_orbit_ratio(args)

    tau_s = args.transmissivity  # Atmospheric transmissivity
    a     = args.albedo

    zen = zenith(args)

    if zen < 0:
        Q_S = 0
    else:
        # Based on Equation 2.1  Page 23
        Q_S = S * eor**2 * (1 - a) * zen * tau_s

    print_v("Q_S:\t", Q_S)

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
    Q_E  = latent_heat_flux(args, Q_H)    # Latent heat flux
    T_g  = f_to_k(args.ground_temp)       # K - Reservoir temperature
    T_s_init = f_to_k(args.surface_temp)  # K - Initial ground temperature

    d_t = args.forecast_period
    # Based on only equation in question 6  Page 61
    d_T_s = (Q_S + Q_Ld - Q_Lu - Q_H - Q_E - K * (T_s_init - T_g)) * d_t / c_g
    # NOTE Last term approximates Q_G the ground heat flux

    T_s = k_to_f(T_s_init + d_T_s)

    print_v("d_T_s:\t", d_T_s, "K")
    print("T_s:\t", T_s, "F")

    return 0


# Parameters to add:
#   Required:
#     * Initial surface air temperature (Celsius)
#     * Ground reservoir temperature (Celsius)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Calculate surface temperature at latitude and longitude https://github.com/makeyourownmaker/ParametricWeatherModel")
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-la', '--latitude',
            help='Latitude (-90 to 90; plus for north, minus for south)',
            required=True, type=float, metavar="[-90.0, 90.0]", choices=[Range(-90.0, 90.0)])
    required.add_argument('-lo', '--longitude',
            help='Longitude (-180 to 180; plus for east, minus for west)',
            required=True, type=float, metavar="[-180.0, 180.0]", choices=[Range(-180.0, 180.0)])
    required.add_argument('-da', '--day_of_year',
            help='Julian day of year (1 to 365)',
            required=True, type=int, metavar="[1, 365]", choices=[Range(1, 366)])
    required.add_argument('-gt', '--ground_temp',
            help='Ground reservoir temperature (Fahrenheit only)',
            type=float)
    required.add_argument('-st', '--surface_temp',
            help='Initial surface air temperature (Fahrenheit only)',
            type=float)

    optional.add_argument('-v',  '--verbose',
            help='Print additional information',
            default=True, action="store_false")
    optional.add_argument('-ho', '--hour',
            help='Hour of day (0 to 24) default=12',
            default=12, type=int, metavar="[0, 24]", choices=range(0, 25))
    optional.add_argument('-al', '--albedo',
            help='Albedo (0 to 1) default=0.3',
            default=0.3, type=float, metavar="[0.0, 1.0]", choices=[Range(0.0, 1.0)])
    optional.add_argument('-cf', '--cloud_fraction',
            help='Cloud fraction (0 to 1) default=0',
            default=0, type=float, metavar="[0.0, 1.0]", choices=[Range(0.0, 1.0)])
    optional.add_argument('-ds', '--day_of_solstice',
            help='Day of solstice (172 or 173) default=173',
            default=173, type=int, metavar="[172, 173]", choices=range(172, 174))
    optional.add_argument('-uo', '--utc_offset',
            help='UTC offset in hours (-12 to 12) default=0',
            default=0, type=int, metavar="[-12, 12]", choices=range(-12, 13))
    optional.add_argument('-fp', '--forecast_period',
            help='Forecast period in seconds (600 to 3600) default=3600',
            default=3600, type=int, metavar="[600, 3600]", choices=[Range(600, 3601)])
    optional.add_argument('-tr', '--transmissivity',
            help='Atmospheric transmissivity (greater than 0) default=0.8',
            default=0.8, type=float)
    optional.add_argument('-em', '--emissivity',
            help='Surface emissivity (0.9 to 0.99) default=0.95',
            default=0.95, type=float, metavar="[0.9, 0.99]", choices=[Range(0.9, 0.99)])
    optional.add_argument('-pw', '--precip_water',
            help='Precipitable water (greater than 0) default=2.5',
            default=2.5, type=float)
    optional.add_argument('-br', '--bowen_ratio',
            help='Bowen ratio (0 to 1) default=0.9',
            default=0.9, type=float, metavar="[0.0, 1.0]", choices=[Range(0.0, 1.0)])

    parser._action_groups.append(optional)
    args = parser.parse_args()

    print_v = print if args.verbose else lambda *a, **k: None

    main(args)
