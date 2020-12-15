
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os
import math
import argparse
import datetime


# NOTE Equation and page numbers in the comments refer to
#      Parameterization Schemes: Keys to Understanding Numerical Weather Prediction Models
#      https://doi.org/10.1017/CBO9780511812590
#      by David J. Stensrud http://www.met.psu.edu/people/djs78


def float_range(min=None, max=None):
    def check_range(x):
        x = float(x)

        if x < min and min is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, min, max))

        if x > max and max is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, min, max))

        return x

    return check_range


def int_range(min=None, max=None):
    def check_range(x):
        x = int(x)

        if x < min and min is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, min, max))

        if x > max and max is not None:
            raise argparse.ArgumentTypeError("%r not in range [%r, %r]" % (x, min, max))

        return x

    return check_range


# NOTE Could not get argparse.Action to validate both Celsius and Fahrenheit temperatures
#      because degrees returned None instead of F or C (when using getattr)
#      Possibly because parse_args() not yet ran
def temp_range(temp, degrees):
    '''
    Validate temperatures within Celsius or Fahrenheit ranges
    '''

    if temp is None:
        return 0

    if (temp < -150.0 or temp > 150.0) and degrees.upper() == 'F':
        print("ERROR: Fahrenheit temperatures must be between -150 and 150 F")
        print("ERROR: Supplied value %f F" % temp)
        exit()
    elif (temp < -100.0 or temp > 66.0) and degrees.upper() == 'C':
        print("ERROR: Celsius temperatures must be between -100 and 66 C")
        print("ERROR: Supplied value %f C" % temp)
        exit()

    return 0


def f_to_k(f):
    '''
    Convert Fahrenheit to Kelvin
    '''

    if f is not None:
        k = (f + 459.67) * 5 / 9
    else:
        k = None

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

    if c is not None:
        k = c + 273.15
    else:
        k = None

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
    w_p = args.precip_water  # cm - precipitable water
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

    # This command line argument models temperature at 40 hPa above the ground surface
    # Atmospheric temperature constant or adjustment or surface temperature:
    #   Constant   - constant value
    #   Adjustment - surface temperature +/- argument  EXPERIMENTAL
    #   Default    - surface temperature
    if args.atmos_temp_constant is not None:
        T_a = args.atmos_temp_constant
    elif args.atmos_temp_adjust is not None:
        T_a = args.surface_temp + args.atmos_temp_adjust
    else:
        T_a = args.surface_temp

    # This command line argument models temperature at the base of the cloud
    # Irrelevant if cloud fraction is 0
    # Cloud base temperature constant or adjustment or surface temperature:
    #   Constant   - constant value
    #   Adjustment - surface temperature +/- argument  EXPERIMENTAL
    #   Default    - surface temperature
    if args.cloud_temp_constant is not None:
        T_c = args.cloud_temp_constant
    elif args.cloud_temp_adjust is not None:
        T_c = args.surface_temp + args.cloud_temp_adjust
    else:
        T_c = args.surface_temp

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
    T_g = args.ground_temp

    # Equation 2.5  Page 25
    Q_Lu = e_g * sigma * T_g**4

    print_v("Q_Lu:\t", Q_Lu)

    return Q_Lu


def sensible_heat_flux(args, N_R):
    '''
    Calculate sensible heat flux using percent of solar radiation or
    resistance to heat flux
    '''

    # "Constants"
    rho = 1.225  # kg m^-3 - Density of air at sea level and 15 degrees C
    c_p = 1004   # J K^-1 kg^-1 - Specific heat at constant pressure

    r_H   = args.resistance             # s m^-1 - Resistance to heat flux
    pc_nr = args.percent_net_radiation  # percent net radiation

    if pc_nr != 0:
        # Based on Question 6  Pages 60 and 61
        Q_H = pc_nr * N_R
    elif r_H != 0:
        # EXPERIMENTAL  Based on Equation 2.23  Page 31
        T_g = args.ground_temp
        T_s = args.surface_temp
        Q_H = rho * c_p * (T_g - T_s) / r_H

    print_v("Q_H:\t", Q_H)

    return Q_H


def latent_heat_flux(args, Q_H):
    '''
    Calculate latent heat flux using Bowen ratio
    '''

    # Based on the definition on Page 22
    Q_E = Q_H / args.bowen_ratio

    print_v("Q_E:\t", Q_E)

    return Q_E


def ground_heat_flux(args):
    '''
    Calculate ground heat flux
    '''

    # "Constants"
    K = 11  # J m^-2 K^-1 s^-1 - Thermal diffusivity of air

    T_g = args.ground_temp   # K - Ground reservoir temperature
    T_s = args.surface_temp  # K - Surface air temperature

    # Based on last term in only equation in question 6  Page 61
    Q_G = K * (T_s - T_g)
    # NOTE This is an approximation

    print_v("Q_G:\t", Q_G)

    return Q_G


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
    LST = args.hour + args.minute / 60 + TC / 60
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


def inc_mins_hours_days(args):
    '''
    Increment minutes, hours and days in main computation loop
    '''

    if args.minute == 59:
        args.minute = 0
        if args.hour == 23:
            args.hour = 0
            if args.day_of_year == 365:
                args.day_of_year = 1
            else:
                args.day_of_year += 1
        else:
            args.hour += 1
    else:
        args.minute += 1

    return 0


def write_csv(args, Q_S, Q_Ld, Q_Lu, Q_H, Q_E, Q_G, d_T_s, T_s):
    '''
    Write to CSV file
    '''

    if args.filename is not None:
        line = str(args.day_of_year) + "\t" + str(args.hour) + "\t" + str(args.minute)
        line = line + "\t" + str(Q_S) + "\t" + str(Q_Ld) + "\t" + str(Q_Lu) + "\t" + str(Q_H)
        line = line + "\t" + str(Q_E) + "\t" + str(Q_G) + "\t" + str(d_T_s)
        line = line + "\t" + str(T_s) + "\n"

        header = False
        if not os.path.exists(args.filename) or os.stat(args.filename).st_size == 0:
            header = True

        with open(args.filename, 'a+') as f:
            if header is True:
                f.write("Day\tHour\tMinute\tQ_S\tQ_Ld\tQ_Lu\tQ_H\tQ_E\tQ_G\td_T_s\tT_s\n")
            f.write(line)
        f.close()

        return 0


def main(args):
    '''
    Calculate surface temperature at latitude and longitude
    Update surface temperature and solar hour angle every minute
    Optionally write to CSV file every args.report_period minutes
    '''

    # "Constants"
    c_g = 1.4 * 10**5  # J m^-2 K^-1 - Soil heat capacity
    d_t = 60
    sum_d_T_s = 0

    if args.degrees.upper() == 'C':
        args.ground_temp  = c_to_k(args.ground_temp)
        args.surface_temp = c_to_k(args.surface_temp)
        args.atmos_temp_constant = c_to_k(args.atmos_temp_constant)
        args.atmos_temp_adjust   = c_to_k(args.atmos_temp_adjust)
        args.cloud_temp_constant = c_to_k(args.cloud_temp_constant)
        args.cloud_temp_adjust   = c_to_k(args.cloud_temp_adjust)
    elif args.degrees.upper() == 'F':
        args.ground_temp  = f_to_k(args.ground_temp)
        args.surface_temp = f_to_k(args.surface_temp)
        args.atmos_temp_constant = f_to_k(args.atmos_temp_constant)
        args.atmos_temp_adjust   = f_to_k(args.atmos_temp_adjust)
        args.cloud_temp_constant = f_to_k(args.cloud_temp_constant)
        args.cloud_temp_adjust   = f_to_k(args.cloud_temp_adjust)

    for i in range(0, args.forecast_minutes):
        Q_S  = solar_rad(args)                # Incoming solar radiation
        Q_Ld = downwelling_rad(args)          # Downwelling longwave radiation
        Q_Lu = upwelling_rad(args)            # Upwelling longwave radiation
        N_R  = Q_S + Q_Ld - Q_Lu              # Net radiation
        print_v("N_R:\t", N_R)
        Q_H  = sensible_heat_flux(args, N_R)  # Sensible heat flux
        Q_E  = latent_heat_flux(args, Q_H)    # Latent heat flux
        Q_G  = ground_heat_flux(args)         # Ground heat flux

        # Based on only equation in question 6  Page 61
        d_T_s = (Q_S + Q_Ld - Q_Lu - Q_H - Q_E - Q_G) * d_t / c_g
        sum_d_T_s += d_T_s
        print_v("d_T_s:\t", d_T_s)  # , "K")
        args.surface_temp = args.surface_temp + d_T_s

        inc_mins_hours_days(args)

        if i % args.report_period == 0:
            if args.degrees.upper() == 'C':
                T_s = k_to_c(args.surface_temp)
            elif args.degrees.upper() == 'F':
                T_s = k_to_f(args.surface_temp)

            print_v("T_s:\t", T_s)  # , "F/C")
            write_csv(args, Q_S, Q_Ld, Q_Lu, Q_H, Q_E, Q_G, sum_d_T_s, T_s)
            sum_d_T_s = 0

    if args.degrees.upper() == 'C':
        T_s = k_to_c(args.surface_temp)
    elif args.degrees.upper() == 'F':
        T_s = k_to_f(args.surface_temp)

    print_v("Sum_dTs:\t", sum_d_T_s)  # , "K")
    print("T_s:\t", T_s)  # , "F/C")
    write_csv(args, Q_S, Q_Ld, Q_Lu, Q_H, Q_E, Q_G, sum_d_T_s, T_s)

    return 0


def post_parse_args_checks(args):
    '''Further arg checks after parse_args.'''

    # NOTE: Could not get argparse.Action to validate both Celsius and Fahrenheit temperatures
    #       because degrees returned None instead of F or C (when using getattr)
    #       Possibly because parse_args() not yet ran
    #       So, validation using temp_range after parse_args()
    temp_range(args.ground_temp,         args.degrees)
    temp_range(args.surface_temp,        args.degrees)
    temp_range(args.atmos_temp_constant, args.degrees)
    temp_range(args.atmos_temp_adjust,   args.degrees)
    temp_range(args.cloud_temp_constant, args.degrees)
    temp_range(args.cloud_temp_adjust,   args.degrees)

    if args.percent_net_radiation == 0 and args.resistance == 0:
        print("\nERROR: 'percent net radiation' and 'resistance to heat flux' cannot both be zero.")
        print("ERROR: 'percent net radiation' %f" % args.percent_net_radiation)
        print("ERROR: 'resistance to heat flux' %f\n" % args.resistance)
        exit()

    if args.report_period > args.forecast_minutes:
        print("\nERROR: 'report_period' cannot be greater than 'forecast_minutes'.")
        print("ERROR: 'report_period' %d" % args.report_period)
        print("ERROR: 'forecast_minutes' %d\n" % args.forecast_minutes)
        exit()

    if args.cloud_fraction == 0 and (args.cloud_temp_constant is not None or args.cloud_temp_adjust is not None):
        print("\nERROR: 'cloud_temp_constant' and 'cloud_temp_adjust' cannot be used when 'cloud_fraction' is zero.")
        print("ERROR: 'cloud_fraction' %f" % args.cloud_fraction)
        if args.cloud_temp_constant is not None:
            print("ERROR: 'cloud_temp_constant' %f\n" % args.cloud_temp_constant)
        if args.cloud_temp_adjust is not None:
            print("ERROR: 'cloud_temp_adjust' %f\n" % args.cloud_temp_adjust)
        exit()

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Calculate surface temperature at latitude and longitude https://github.com/makeyourownmaker/ParametricWeatherModel")

    required = parser.add_argument_group('required arguments')
    required.add_argument('-la', '--latitude',
            help='Latitude (-90 to 90; plus for north, minus for south)',
            required=True, type=float_range(-90.0, 90.0), metavar="[-90.0, 90.0]")
    required.add_argument('-lo', '--longitude',
            help='Longitude (-180 to 180; plus for east, minus for west)',
            required=True, type=float_range(-180.0, 180.0), metavar="[-180.0, 180.0]")
    required.add_argument('-da', '--day_of_year',
            help='Julian day of year',
            required=True, type=int_range(0, 365), metavar="[1, 365]")
    # validation using temp_range after parse_args()
    required.add_argument('-gt', '--ground_temp',
            help='Ground reservoir temperature (Fahrenheit or Celsius)',
            default=None, type=float)
    # validation using temp_range after parse_args()
    required.add_argument('-st', '--surface_temp',
            help='Initial surface air temperature (Fahrenheit or Celsius)',
            default=None, type=float)
    required.add_argument('-de', '--degrees',
            help='Specify ground and surface temperature in Celsius or Fahrenheit (C, c, F or f)',
            required=True, type=str, choices=['C', 'F', 'c', 'f'])
    required.add_argument('-pr', '--percent_net_radiation',
            help='Percent net radiation',
            required=True, type=float_range(0, 1), metavar="[0, 1]")

    optional = parser._action_groups.pop()
    optional.add_argument('-v',  '--verbose',
            help='Print additional information',
            default=True, action="store_false")
    optional.add_argument('-ho', '--hour',
            help='Initial hour of day - default=12',
            default=12, type=int, metavar="[0, 24]", choices=range(0, 25))
    optional.add_argument('-mi', '--minute',
            help='Initial minute of hour - default=0',
            default=0, type=int, metavar="[0, 59]", choices=range(0, 60))
    optional.add_argument('-al', '--albedo',
            help='Albedo - default=0.3',
            default=0.3, type=float_range(0.0, 1.0), metavar="[0.0, 1.0]")
    optional.add_argument('-cf', '--cloud_fraction',
            help='Cloud fraction - default=0',
            default=0, type=float_range(0.0, 1.0), metavar="[0.0, 1.0]")
    optional.add_argument('-ds', '--day_of_solstice',
            help='Day of solstice - default=173',
            default=173, type=int, metavar="[172, 173]", choices=range(172, 174))
    optional.add_argument('-uo', '--utc_offset',
            help='UTC offset in hours - default=0',
            default=0, type=int, metavar="[-12, 12]", choices=range(-12, 13))
    optional.add_argument('-rp', '--report_period',
            help='Report period in minutes - default=60',
            default=60, type=int_range(1, 61), metavar="[1, 60]")
    optional.add_argument('-fm', '--forecast_minutes',
            help='Forecast period in minutes - default=1',
            default=1, type=int_range(1, 1441), metavar="[1, 1440]")
    optional.add_argument('-tr', '--transmissivity',
            help='Atmospheric transmissivity - default=0.8',
            default=0.8, type=float_range(0.0, 1.0), metavar="[0.0, 1.0]")
    optional.add_argument('-em', '--emissivity',
            help='Surface emissivity - default=0.9',
            default=0.9, type=float_range(0.7, 0.99), metavar="[0.7, 0.99]")
    optional.add_argument('-pw', '--precip_water',
            help='Precipitable water in cm - default=1',
            default=1, type=float_range(0.0, 7.5), metavar="[0.0, 7.5]")
    optional.add_argument('-br', '--bowen_ratio',
            help='Bowen ratio - default=0.9',
            default=0.9, type=float_range(-10.0, 10.0), metavar="[-10.0, 10.0]")
    optional.add_argument('-fn', '--filename',
            help='File name for CSV output', type=str)
    optional.add_argument('-rh', '--resistance',
            help='EXPERIMENTAL: Resistance to heat flux (greater than 0)',
            default=0, type=float_range(0, None), metavar="[0, None]")

    mutex1 = parser.add_mutually_exclusive_group()
    # validation using temp_range after parse_args()
    mutex1.add_argument('-at', '--atmos_temp_constant',
            help='Atmospheric temperature at 40 hPa - constant value',
            nargs='?', default=None, type=float)
    # validation using temp_range after parse_args()
    mutex1.add_argument('-ta', '--atmos_temp_adjust',
            help='EXPERIMENTAL: Atmospheric temperature at 40 hPa - surface temperature plus this adjustment value',
            nargs='?', default=None, type=float)

    mutex2 = parser.add_mutually_exclusive_group()
    # validation using temp_range after parse_args()
    mutex2.add_argument('-ct', '--cloud_temp_constant',
            help='Base of cloud temperature - constant value',
            nargs='?', default=None, type=float)
    # validation using temp_range after parse_args()
    mutex2.add_argument('-tc', '--cloud_temp_adjust',
            help='EXPERIMENTAL: Base of cloud temperature - surface temperature plus this adjustment value',
            nargs='?', default=None, type=float)

    parser._action_groups.append(optional)
    args = parser.parse_args()

    post_parse_args_checks(args)

    print_v = print if args.verbose else lambda *a, **k: None

    main(args)
