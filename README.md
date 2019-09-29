
# ParametricWeatherModel

![Lifecycle
](https://img.shields.io/badge/lifecycle-experimental-orange.svg?style=flat)
![Dependencies
](https://img.shields.io/badge/dependencies-none-brightgreen.svg?style=flat)

ParametricWeatherModel is a repository for forecasting surface temperature 
based primarily on latitude, longitude, day of year and hour of day.


## Development Stage

The repository is under active, but early, development.  It contains some 
limitations, hardcoded parameters and probably errors.  Please file an 
issue if you find a problem.


## Usage

Predict surface temperature at specified latitude, longitude, day of year, 
ground temperature and initial surface temperature:
```sh
python parametric_scheme.py -la 47.6928 -lo -122.3038 -da 229 -gt 54 -st 72

# Similarly with long options
python parametric_scheme.py --latitude 47.6928 --longitude -122.3038 --day_of_year 229 --ground_temp 54 --surface_temp 72

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

Radiative processes to add:
  * Sensible heat flux (heat transfer per unit area from the ground to the atmosphere)
  * Latent heat flux (rate of moisture transfer per unit area from the ground surface to the atmosphere)

Included parameters:
  * Required:
    * Latitude (-90 to 90; plus for north, minus for south)
    * Longitude (-180 to 180; plus for east, minus for west)
    * Day of year (1 to 365)
    * Initial surface air temperature (Fahrenheit)
    * Ground reservoir temperature (Fahrenheit)
  * Optional:
    * Hour of day (0 to 24) default=12
    * Cloud fraction (0 to 1) default=0
    * Albedo (0 to 1) default=0.3
    * UTC offset (-12 to 12) default=0
    * Day of solstice (172 or 173) default=173
    * Forecast period in seconds (600 to 3600) default=3600
    * Surface emissivity (0.9 to 0.99) default=0.95
    * Bowen ratio default=0.9
    * Atmospheric transmissivity default=0.8
    * Precipitable water default=2.5
    * Verbose option
    * Help option
    
Parameters to add:
  * Required:
    * Initial surface air temperature (Celsius)
    * Ground reservoir temperature (Celsius)


### Limitations

  * Earth's elliptical orbit is ignored
  * Some variables are treated as constants e.g. transmissivity
  * Hardcoded parameters include: thermal diffusivity of air, soil heat 
    capacity and solar radiation
  * Assumes temperature at 40 hPa above the ground surface equals surface 
    temperature which it certainly does not
  * Assumes temperature at the base of the cloud equals surface 
    temperature which it certainly does not


## Roadmap

* Improve command line options
  * Celsius reservoir and surface temperatures
  * Add more range checks: Bowen ratio, precipitable water etc
* Improve documentation
  * Expand the details section above
    * Explain default values used and/or
    * Include details of the constants used
  * Add more usage examples
    * Illustrate the most important command line options
  * Possibly add some illustrative plots
* Add unit tests


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
