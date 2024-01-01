#!/bin/bash

if [ $(/bin/pgrep -f "sensor_main.py") ]; then
    echo "script running"
    # Command when the script is runnung
else
    echo "starting script"
    python3 /home/pi/sensor_main.py
fi
