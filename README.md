# pi-daq-server
This software facilitates the following:
- Logging of data from Advantech ADAM-6200 series or similar devices
- Serving of data over the network via an API
- Analysis of data
---
# Steps to install the server portion of this software on a raspberry pi:
- Get a terminal
	- Setting up SSH is recommended.
	- USB keyboard and HDMI display are also okay.
- Install git.
    - Try `git` to test for an existing installation.
- Clone this repository
	-`git clone https://github.com/jasonharriot/pi-daq-server`
- Create a virtual environment inside this repository. `py -m venv venvdir` invokes the `venv` module, and creates a virtual environment called `venvdir`, which lives inside a directory with the same name.
- Activate the virtual environment.
	- `venvdir\Scripts\activate.bat` on Windows.
	- `source venvdir/bin/activate` on Linux.

- Run the install script:
	- `sudo python3 server-install.py`
		- Creates the `pidaq` user, which will act as a sandbox for the server daemon.
		- Sets the server to run at boot and restart on a crash.
			- Systemd is used. The install script creates a symbolic link in /etc/systemd/system/, which points to the file `pi-daq-server.service`, which lives in this repository.
		- Checks permissions
			- The daemon needs write permissions for the data directory
		- Sets the pi's hostname (pidaq.local)
		- Set up the webserver
# Steps to use the client portion of the software:
- Repeat steps above to clone another copy of this repository to your personal computer.
- Figure out which Python command to use.
	- On Windows:
		-`py --version` should yield something like `Python 3.x.x`.
	- On Linux, or some Windows machines: 
		-`python3 --version`  should yield similar.

It is assumed you will use the `py` command. Substitute with a different way to invoke python if necessary; syntax shouldn't change.

- Test the web endpoints on the server
	- Navigate to `pidaq.local/` in a browser