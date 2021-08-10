forked from [edlib, esp-drone branch](https://github.com/leeebo/crazyflie-lib-python/tree/esp-drone)

# edlib: Espdrone python library

edlib is an API written in Python that is used to communicate with the Espdrone. It is intended to be used by client software to
communicate with and control an espdrone quadcopter. For instance the [edclient](https://github.com/NelsenEW/espdrone-clients) Espdrone PC client uses the edlib.

For more info see esp-drone [wiki](https://docs.espressif.com/projects/espressif-esp-drone/en/latest/index.html "Espdrone Wiki from espressif").


## Development
### Developing for the edclient
* [Clone the edlib](https://help.github.com/articles/cloning-a-repository/), 
  `git clone https://github.com/NelsenEW/espdrone-lib-python.git`
* Install dependencies required by the lib: 
  `pip install -r requirements.txt`

* Install the edlib in editable mode: `pip install -e .`
* [Uninstall the edlib if you don't want it any more](http://pip-python3.readthedocs.org/en/latest/reference/pip_uninstall.html), `pip uninstall edlib`

#### Virtualenv
This section contains a very short description of how to use [virtualenv (local python environment)](https://virtualenv.pypa.io/en/latest/) 
with package dependencies. If you don't want to use virualenv and don't mind installing edlib dependencies system-wide
you can skip this section.

* Install virtualenv: `pip install virtualenv`
* create an environment: `python -m virtualenv venv`
* Activate the environment: `cd venv/Scripts && activate.bat`


* To deactivate the virtualenv when you are done using it `deactivate`

Note: For systems that support [make](https://www.gnu.org/software/make/manual/html_node/Simple-Makefile.html), you can use `make venv` to
create an environment, activate it and install dependencies.

## Examples
There are several examples under the `examples` directory that can be run with the following command:

`python[3] path/to/example_file.py --uri [YOUR DRONE's IP]` 

e.g. `python examples/basiclog.py --uri 192.168.0.105`

Here is the list of the working examples:
* [basiclog.py](examples/basiclog.py) - Log the drone roll, pitch, yaw and the battery voltage asynchronously.
* [basicparam.py](examples/basicparam.py) - Get the value of each parameters inside the drone, and set the pitch derivative gain controller to a random number
* [basiclogSync.py](examples/basiclogSync.py) - Log the drone roll, pitch yaw synchronously
* [camera_example.py](examples/camera_example.py) - Get the camera stream from the drone and show it on an opencv window
* [multilog.py](examples/multilog.py) - Log mutliple drones roll, pitch, yaw, and battery voltage asynchronously
* [multiramp.py](examples/multiramp.py) - Ramp multiple drones motor