#!/bin/bash
#

echo "Installing Pi-DAQ @ $(date)"

cd $(dirname $0)

#Configuration variables:

repositorydirpath="$(realpath .)"	#Absolute path to the directory where this script lives, which should be the root of the repository.
#daemonuser="pidaq"	#Username for the daemon user. Must match that of the service file.
daemonuser="pi"	#pi is the login user. Separate daemon user will not be used.
hostname="pidaq.local"	#This script changes the hostname of the pi to pidaq.local.
datadirname="data"
daemondirpath="/var/pid-aq"	#Directory where the daemon start script lives. It is a symlink to a script in this directory.



#
generalerror=0




#Checks
if [ $(whoami) != "pi" ]; then
	echo "Please run as pi. Do not run as root or another user."
	generalerror=1
fi






#Change hostname

sudo su -c "printf \"$hostname\" > /etc/hostname" root

e=$?

if [ $e -eq "0" ]; then
	echo "Changed hostname to $(cat /etc/hostname)"
else
	echo "Couldn't change hostname. Hostname is currently: $(cat /etc/hostname). ($e)"
	generalerror=1
fi







#Configure daemon user

#sudo useradd $daemonuser > /dev/null 2>&1

#e=$?

# if [ $e -eq "9" ]; then
# 	echo "User $daemonuser already exists. ($e)"
# elif [ $e -ne "0" ]; then
# 	echo "Did not create the $daemonuser user. ($e)"
# 	generalerror=1
# else
# 	echo "Created the $daemonuser user."
# fi







#Configure linked directory in /var. All hardcoded paths such as in the .service file will point to /var/pi-daq.

sudo rm "$daemondirpath"	#Remove symlink

e=$?

if [ $e -eq "0" ]; then
	echo "Removed old daemon directory/symlink."
else
	echo "Failed to remove old daemon directory/symlink. ($e)"
	generalerror=1
fi

sudo ln -s "$repositorydirpath" "$daemondirpath" > /dev/null 2>&1

e=$?

if [ $e -eq "0" ]; then
	echo "Created daemon dir symlink."
else
	echo "Couldn't create daemon dir symlink $daemondirpath. ($e)"
	generalerror=1
fi

sudo chown -h "$daemonuser:$daemonuser" "$daemondirpath" > /dev/null 2>&1

e=$?

if [ $e -eq "0" ]; then
	echo "Set permissions for dir symlink."
else
	echo "Couldn't set permissions for dir symlink. ($e)"
	generalerror=1
fi







#Set up python environment
python3 -m venv "venv"
source "venv/bin/activate"

echo "Installing the following Python packges:"
cat requirements.txt
echo

pip install -r requirements.txt

e=$?

if [ $e -eq "0" ]; then
	echo "Set up Python environment."
else
	echo "Failed to set up Python environment. ($e)"
	generalerror=1
fi









# Start service
servicefilepath="$repositorydirpath/pi-daq.service" 

sudo rm "/etc/systemd/system/pi-daq.service" > /dev/null 2>&1

sudo ln -s "$servicefilepath" "/etc/systemd/system/" > /dev/null 2>&1

e=$?

if [ $e -eq "1" ]; then
	echo "Symlink $servicefilepath already exists."
elif [ $e -eq "0" ]; then
	echo "Created service symlink $servicefilepath."
else
	echo "Failed to create service symlink $servicefilepath. ($e)"
	generalerror=1
fi

sudo systemctl enable "pi-daq.service"

systemctl status "pi-daq.service" > /dev/null 2>&1

e=$?

if [ $e -eq "3" ]; then
	echo "Daemon is dead. ($e)"
	generalerror=1
elif [ $e -eq "4" ]; then
	echo "Daemon service does not exist. ($e)"
	generalerror=1
elif [ $e -eq "0" ]; then
	echo "Daemon is running."
fi


















#End section

if [ $generalerror -eq "0" ]; then
	echo "Server configuration completed without errors. The hostname change may not come into effect until a reboot."
else
	echo "Configuration did not complete sucessfully, please fix the issues."
fi

echo "Installation done @ $(date)"


