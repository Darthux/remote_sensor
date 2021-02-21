#!/usr/bin/python3
# this script will check connectivity to google and activate the green LED
# on SixFab LTE HAT
# Created by @Darthux 20210131

from gpiozero import LED, PingServer
from signal import pause
led = LED(27)
server = PingServer('google.com')
led.source_delay = 30
led.source = server
pause()
