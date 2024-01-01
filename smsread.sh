#!/bin/bash

if [ $(/bin/pgrep -f "smsread.py") ]; then
    echo "script running"
    # Command when the script is runnung
else
    echo "starting script"
    python3 /home/pi/smsread.py
fi
