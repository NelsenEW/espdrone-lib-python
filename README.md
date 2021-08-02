forked from [espdlib, esp-drone branch](https://github.com/leeebo/espdrone-lib-python/tree/esp-drone)

# espdlib: Espdrone python library

espdlib is an API written in Python that is used to communicate with the Espdrone
and Espdrone 2.0 quadcopters. It is intended to be used by client software to
communicate with and control a Espdrone quadcopter. For instance the [edclient][edclient] Espdrone PC client uses the espdlib.

This repository has been modified to communicate with **espdrone** as well using python.

See [below](#platform-notes) for platform specific instruction.
For more info see esp-drone [wiki](https://docs.espressif.com/projects/espressif-esp-drone/en/latest/index.html "Bitcraze Wiki").


## Development
### Developing for the edclient
1. [Clone the espdlib](https://help.github.com/articles/cloning-a-repository/), 
  `git clone git@github.com:YOUR-USERNAME/espdrone-lib-python.git`
2. Install dependencies required by the lib: 
  `pip install -r requirements.txt`

3.  *  `pip install -e .`
* [Uninstall the espdlib if you don't want it any more](http://pip-python3.readthedocs.org/en/latest/reference/pip_uninstall.html), `pip uninstall espdlib`

### Linux, OSX, Windows

The following should be executed in the root of the espdrone-lib-python file tree.

#### Virtualenv
This section contains a very short description of how to use [virtualenv (local python environment)](https://virtualenv.pypa.io/en/latest/) 
with package dependencies. If you don't want to use virualenv and don't mind installing espdlib dependencies system-wide
you can skip this section.

* Install virtualenv: `pip install virtualenv`
* create an environment: `python -m virtualenv venv`
* Activate the environment: `cd venv/Scripts && activate.bat`


* To deactivate the virtualenv when you are done using it `deactivate`

Note: For systems that support [make](https://www.gnu.org/software/make/manual/html_node/Simple-Makefile.html), you can use `make venv` to
create an environment, activate it and install dependencies.
