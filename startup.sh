#!/bin/bash

sudo killall python
sudo killall node

sudo service mosquitto stop
sudo rm /var/lib/mosquitto/mosquitto.db
sudo service mosquitto start

cd /home/pi/ModelRailway/SensorEditor
sudo /usr/bin/node server.js &

# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh

. /home/pi/.virtualenvs/cv/bin/activate


cd /home/pi/ModelRailway/TrackMonitor
python track_mon_mqtt6.py 2>&1 > track_monitor.log &
