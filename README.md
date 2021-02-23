forked from [cflib, esp-drone branch](https://github.com/leeebo/crazyflie-lib-python/tree/esp-drone)

# cflib: Crazyflie python library [![Build Status](https://api.travis-ci.org/bitcraze/crazyflie-lib-python.svg)](https://travis-ci.org/bitcraze/crazyflie-lib-python)

cflib is an API written in Python that is used to communicate with the Crazyflie
and Crazyflie 2.0 quadcopters. It is intended to be used by client software to
communicate with and control a Crazyflie quadcopter. For instance the [cfclient][cfclient] Crazyflie PC client uses the cflib.

This repository has been modified to communicate with **espdrone** as well using python.

See [below](#platform-notes) for platform specific instruction.
For more info see esp-drone [wiki](https://docs.espressif.com/projects/espressif-esp-drone/en/latest/index.html "Bitcraze Wiki").


## Development
### Developing for the cfclient
1. [Clone the cflib](https://help.github.com/articles/cloning-a-repository/), 
  `git clone git@github.com:YOUR-USERNAME/crazyflie-lib-python.git`
2. Install dependencies required by the lib: 
  `pip install -r requirements.txt`

3.  *  `pip install -e .`
* [Uninstall the cflib if you don't want it any more](http://pip-python3.readthedocs.org/en/latest/reference/pip_uninstall.html), `pip uninstall cflib`

### Linux, OSX, Windows

The following should be executed in the root of the crazyflie-lib-python file tree.

#### Virtualenv
This section contains a very short description of how to use [virtualenv (local python environment)](https://virtualenv.pypa.io/en/latest/) 
with package dependencies. If you don't want to use virualenv and don't mind installing cflib dependencies system-wide
you can skip this section.

* Install virtualenv: `pip install virtualenv`
* create an environment: `python -m virtualenv venv`
* Activate the environment: `cd venv/Scripts && activate.bat`


* To deactivate the virtualenv when you are done using it `deactivate`

Note: For systems that support [make](https://www.gnu.org/software/make/manual/html_node/Simple-Makefile.html), you can use `make venv` to
create an environment, activate it and install dependencies.
