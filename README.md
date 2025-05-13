# pi-daq-server
This software facilitates the following:
- Logging of data from Advantech ADAM-6200 series or similar devices
- Serving of data over the network via an API
- Analysis of data
---
# Steps to install the server portion of this software on a raspberry pi:
- Install git.
    - Try `git` to test for an existing installation.
- Clone this repository
	-`git clone https://github.com/jasonharriot/pi-daq-server.git`
- Create a virtual environment inside this repository. `py -m venv venvdir` invokes the `venv` module, and creates a virtual environment called `venvdir`, inside a folder named the same.
- Activate the virtual environment.
	- `venvdir\Scripts\activate.bat` on Windows.
	- `source venvdir/bin/activate` on Linux.

- Run the install script:
	- `sudo python3 server-install.py`

# Steps to use the client portion of the software:
- Repeat steps to clone this repository to your personal computer.
- Figure out which Python command to use
	- On Windows:
		-`py --version` should yield `Python 3.12.1` or similar.
	- On Linux or some Windows: 
		-`python3 --version`  should yield the same or similar.

It is assumed you will use `py`. Substitute with something else if necessary; syntax shouldn't change.

- Test the web endpoints on the server