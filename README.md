Pi DAQ Server
EDAC Labs, Inc. 2025

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
- Run the install script:
	- `chmod +x install_server.sh`
	- `./install_server.sh`
- Create or edit the `config_server.ini` file in the repository directory:
	```[mysql]
	host=localhost
	user=pi-daq-server
	password=<Pi DAQ server password>
	database=hydromet_reactor

	[adam1]
	ip=192.168.1.10

# Steps to use the client portion of the software:
- Repeat steps above to clone another copy of this repository to your personal computer.
- Create or edit the `config_server.ini` file in the repository directory:
	```[mysql]
		host=pidaq.local
		user=pi-daq-client
		password=<Pi DAQ client password>
		database=hydromet_reactor
- Figure out which Python command to use.
	- On Windows:
		-`py --version` should yield something like `Python 3.x.x`.
	- On Linux, or some Windows machines: 
		-`python3 --version`  should yield similar.

It is assumed you will use the `py` command. Substitute with a different way to invoke python if necessary; syntax shouldn't change.

# Insert I - Installing mysql server
- `sudo apt install default-mysql-server`
- `sudo mysql_secure_installation`
	- No password for root.
	- (y) Switch to unix_socket authentication
	- (n) Do not change the root password.
	- (y) Remove anonymous users.
	- (y) Disallow root login remotely
	- (y) Remove test database and access to it.
	- (y) Reload privilege tables.
- `sudo mysql`
	- `create database hydromet_reactor;`
	- `create user 'pi-daq-client' identified by '<Pi DAQ client password>';`
	- `grant select on hydromet_reactor.* to 'pi-daq-client';`
	- `create user 'pi-daq-server' identified by '<Pi DAQ server password>';`
	- `grant all privileges on hydromet_reactor.* to 'pi-daq-server'@'localhost';`
- Append to `/etc/mysql/my.cnf`
	```[mysqld]
	skip-networking=0
	skip-bind-address
- `sudo service mysql restart`
- From your client machine, `nmap pidaq.local -p 3306` should yeild "open" on port 3306.