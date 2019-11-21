
# ParametricWeatherModel

![Lifecycle
](https://img.shields.io/badge/lifecycle-experimental-orange.svg?style=flat)
![Dependencies
](https://img.shields.io/badge/dependencies-none-brightgreen.svg?style=flat)

ParametricWeatherModel is a repository for forecasting surface temperature
based primarily on latitude, longitude, day of year and hour of day.


## Development Stage

The repository is under active, but early, development.  It contains some
limitations, hardcoded parameters and possibly errors.  Please file an
issue if you find a problem.


## Usage

Predict surface temperature at specified latitude, longitude, day of year,
ground temperature and initial surface temperature:
```sh
python parametric_scheme.py -la 47.6928 -lo -122.3038 -da 229 -gt 54 -st 72 -rh 10

# Similarly with long options
python parametric_scheme.py --latitude 47.6928 --longitude -122.3038 --day_of_year 229 --ground_temp 54 --surface_temp 72 --resistance 10

# To list command line options
python parametric_scheme.py -h
```


## Installation

Requires a recent version of python (either 2 or 3 should work).

The following should work on any unix-ish environment:
```sh
wget https://raw.githubusercontent.com/makeyourownmaker/ParametricWeatherModel/master/parametric_scheme.py
python parametric_scheme.py -h
```


## Details

This repository contains code for a simple parameterization scheme to
forecast the air temperature at the surface at a point over the next hour.
It is based on chapter 2 from the book
[Parameterization Schemes: Keys to Understanding Numerical Weather Prediction Models](https://www.cambridge.org/core/books/parameterization-schemes/C7C8EC8901957314433BE7C8BC36F16D#fndtn-information)
by [David J. Stensrud](http://www.met.psu.edu/people/djs78).

According to [wikipedia](https://en.wikipedia.org/wiki/Parametrization_(atmospheric_modeling)):
A parameterization scheme "in a weather or climate model in the context of
numerical weather prediction is a method of replacing processes that are too
small-scale or complex to be physically represented in the model by a
simplified process."

The python code models the following radiative processes:
  * Incoming solar radiation
  * Upwelling longwave radiation from the surface
  * Downwelling longwave radiation from the atmosphere
  * Ground heat flux (heat transfer from the ground surface into the deeper soil levels)
  * Sensible heat flux (heat transfer per unit area from the ground to the atmosphere)
  * Latent heat flux (rate of moisture transfer per unit area from the ground surface to the atmosphere)

Equation and page numbers in the python code refer to
[Parameterization Schemes: Keys to Understanding Numerical Weather Prediction Models](https://doi.org/10.1017/CBO9780511812590)
by [David J. Stensrud](http://www.met.psu.edu/people/djs78).

Included parameters:
  * Required:

| Name                    | Short | Long           | Description                                  | Default |
|-------------------------|-------|----------------|----------------------------------------------|---------|
| Latitude                | -la   | --latitude     | -90 to 90; plus for north, minus for south   | N/A     |
| Longitude               | -lo   | --longitude    | -180 to 180; plus for east, minus for west   | N/A     |
| Day                     | -da   | --day_of_year  | Julian day of year; 1 to 365                 | N/A     |
| Surface temperature     | -st   | --surface_temp | Initial surface air temperature (Fahrenheit) | N/A     |
| Ground temperature      | -gt   | --ground_temp  | Ground reservoir temperature (Fahrenheit)    | N/A     |
| Resistance to heat flux | -rh   | --resistance   | Resistance to heat flux (m s^-1)             | N/A     |

  * Optional:

| Name               | Short | Long              | Description                                | Default |
|--------------------|-------|-------------------|--------------------------------------------|---------|
| Hour               | -ho   | --hour            | Hour of day; 0 to 24                       | 12      |
| Albedo             | -al   | --albedo          | Albedo; 0 to 1                             | 0.3     |
| Cloud fraction     | -cf   | --cloud_fraction  | Cloud fraction; 0 to 1                     | 0       |
| Solstice           | -ds   | --day_of_solstice | Day of solstice; 172 or 173                | 173     |
| UTC offset         | -uo   | --utc_offset      | UTC offset in hours; -12 to 12             | 0       |
| Forecast period    | -fp   | --forecast_period | Forecast period in seconds; 600 to 3600    | 3600    |
| Transmissivity     | -tr   | --transmissivity  | Atmospheric transmissivity; greater than 0 | 0.8     |
| Emissivity         | -em   | --emissivity      | Surface emissivity; 0.9 to 0.99            | 0.95    |
| Bowen ratio        | -br   | --bowen_ratio     | Bowen ratio; -10 to 10                     | 0.9     |
| Precipitable water | -pw   | --precip_water    | Precipitable water; greater than 0         | 0.25    |
| Help               | -h    | --help            | Show this help message and exit            | N/A     |
| Verbose            | -v    | --verbose         | Print additional information               | N/A     |

Parameters to add:
  * Required:
    * Support initial surface air temperature in Celsius
    * Support gound reservoir temperature in Celsius

Constants used:
**Note**: Strictly speaking some of these values are not constants; meaning constant values have been used as simpliying approximations.

| Constant                    | Value           | Unit             | Simpliying approximation |
|-----------------------------|-----------------|------------------|--------------------------|
| Stefan-Boltzmann            | 5.67 * 10**(-8) | W m^-2 K^-4      | No                       |
| Thermal conductivity of air | 2.5 * 10**(-2)  | W m^-1 K^-1 s^-1 | No                       |
| Solar irradiance            | 1368            | W m^-2           | No                       |
| Soil heat capacity          | 1.4 * 10**5     | J m^-2 K^-1      | Yes                      |
| Thermal diffusivity of air  | 11              | J m^-2 K^-1 s^-1 | Yes                      |

### Limitations and assumptions

  * Pollution is ignored
  * A host of atmospheric factors are ignored: refraction, humidity, pressure, wind, rain, snow etc
  * A host of geographic factors are ignored: elevation, slope of terrain, soil type, soil moisture, vegetation etc
  * Sunspot activity may influence the solar constant
  * Thermal conductivity of air is affected by temperature and pressure
  * Some variables are treated as constants e.g. transmissivity
  * Hardcoded parameters include: thermal diffusivity of air and soil heat capacity
  * Assumes temperature at 40 hPa above the ground surface equals surface
    temperature which it certainly does not
  * Assumes temperature at the base of the cloud equals surface
    temperature which it certainly does not


## Roadmap

* Investigate night time temperatures:
  * Anecdotally temperatures seem too low at night
  * There may be problems with the sensible and latent heat flux values

* Sanity checks:
  * Sensible heat flux increases during morning reaching a maximum in the
    afternoon before decreasing to zero after sunset on cloudless summer days
  * Surface energy budget should balance - Equation 2.102  Page 55:
    * Sensible heat flux (Q_H), latent heat flux (Q_E) and ground heat flux (Q_G)
      should be positive with high solar radiation (Q_S)

* Add unit tests:
  * Setup travis CI
  * Find range of test cases where surface temperature and all parameters are known
  * What is an acceptable prediction interval?

* Improve command line options:
  * Support ground reservoir and surface temperatures in Celsius
  * Improve argparse range checks:
    * Find reasonable upper limits for precipitable water and transmissivity values
      * Currently accepting all positive values
    * Find reasonable upper and lower limits for ground and surface temperatures
      * Currently not using range checks for temperatures

* Improve documentation:
  * Add more usage examples
    * Illustrate the most important command line options
  * Possibly add some illustrative plots
    * Including one for each of the heat fluxes


## Contributing

Pull requests are welcome.  For major changes, please open an issue first to discuss what you would like to change.


## See also

* [Digging into a "simple" weather model](http://lukemweather.blogspot.com/2011/08/digging-into-simple-weather-model.html)
  by [Luke Madaus](http://midlatitude.com/lukemadaus/)
* [Parameterization Schemes: Keys to Understanding Numerical Weather Prediction Models](https://doi.org/10.1017/CBO9780511812590)
  by [David J. Stensrud](http://www.met.psu.edu/people/djs78)
* The [ESCOMP repositories](https://github.com/ESCOMP) particularly the Community Land Model included in
  [CTSM](https://github.com/ESCOMP/ctsm) which has detailed
  [radiative flux](https://escomp.github.io/ctsm-docs/doc/build/html/tech_note/Radiative_Fluxes/CLM50_Tech_Note_Radiative_Fluxes.html)
  and
  [heat flux](https://escomp.github.io/ctsm-docs/doc/build/html/tech_note/Fluxes/CLM50_Tech_Note_Fluxes.html#sensible-and-latent-heat-fluxes-for-non-vegetated-surfaces)
  calculations


## License
[GPL-2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
