#!/usr/bin/env python3
# Sensor: Thermistor and Adafruit ADS1115 ADC breakout
# and their sammple code. credit to https://github.com/adafruit/Adafruit_CircuitPython_BME280
# Camera: Raspberry Pi Camear Module V2 (RPI-CAM-V2)
# This script will:
#  a. read sensor information
#  b. overlay Date, time and readings on captured photo
#  c. save the captured data to a spreadsheet
# Created by @Darthux 20210212

from picamera import PiCamera, Color  # for camera
from time import time, sleep, strftime  # for camera
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import csv  # writing and data into csv
from subprocess import Popen
from os import system
import math
from gpiozero import DigitalOutputDevice

camera = PiCamera()  # defind the camera outside of def incase i want to use it elsewhere
camera.rotation = 180
#camera.start_preview()  # activate camera

system('python3 ~/sms.py YOUR_9_DIGIT_PHONE_NUMBER "sensor running"')
therm1 = DigitalOutputDevice(25)
# configure the thermistor
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
therm = AnalogIn(ads, ADS.P0)

def gather():
    therm1.on()
    sleep(.25)
    global TEMPF
    VIN = 3.3
    VOUT = therm.voltage
    RO = 10000
    RT = (VOUT * RO) / (VIN - VOUT)
    A = 0.001129148
    B = 0.000234125
    C = 0.0000000876741
    TEMPF = ((1 / (A + (B * math.log(RT)) + C * math.pow(math.log(RT),3))) - 273.15) * (9/5) + 32
    therm1.off()

gather()  # get first readings and discard them


# adding data to CSV
def log():
    gather()
    print(TEMPF)
#    now = strftime('%m%d%Y-%H%M%S')  # output is MMDDYYYY-HHMMSS
    now = strftime('%d%b%Y-%H%M')
    f = open("/home/pi/temperature_data.csv", "a", newline = "")
    tup1 = (now, TEMPF)
    writer = csv.writer(f)
    writer.writerow(tup1)
    f.close

# define what to do when taking a photo
def get_image():
    system('uptime >> /home/pi/uptime.txt')
    camera.start_preview(fullscreen=False,window=(200,400,600,800))  # activate camera
    now = strftime('%d%b%Y-%H%M%S')
    camera.resolution = (1920, 1080)  # set resolution
#    camera.brightness = 50  # set brightness
    camera.annotate_text_size = 50
    camera.annotate_foreground = Color('white')
    camera.annotate_background = Color('black')
    log()  # get fresh readings before taking photo
#    camera.annotate_text = now + Cr + Tep + Cr + Hum + Cr + Pres  # text overlay goes here
    camera.annotate_text = now + ", " + str(round(TEMPF,1)) + "F"
    filename = "/home/pi/Pictures/" + now + ".jpg"  # output is MMDDYYYY-HHMMSS.jpg
    camera.capture(filename)  # take the photo and save as filename
    last_photo = "/home/pi/Pictures/photo.jpg"  # Most recent photo taken
    sleep(2.5)
    camera.capture(last_photo)  # take the photo and save as last_photo
    camera.stop_preview()  # deactivate camera

rcounter = 0
lcounter = 0
pcounter = 0
x = 5  # how many readings before photo
y = 60  # how often to sleep for readings
z = 60  # take photo on nth minute
def collect():
    global rcounter, lcounter, pcounter
    if lcounter == 0:  # take photo on furst run
#        print("\nfirst reading")
        get_image()
        lcounter += 1  # add 1 to lcounter to push to elif
#        collect()  # start loop over

    elif lcounter != 0 and pcounter == 0:  # take nth minute reading
#        print("\nWaiting for 10th minute")
        sleep(z - time() % z)
        rcounter += 1
#        print("\ntaking photo")
#        print("read count " + str(rcounter))
        get_image()
        pcounter += 1  # add 1 to pcounter, push to next elif
#        collect()

    elif pcounter != 0 and rcounter < x:
#        print("\nTaking reading only")
        sleep(y - time() % y)
#        print("\ntaking reading")
        log()
        rcounter += 1  # add 1 to rcounter until push to else
#        print("read count " + str(rcounter))
#        collect()

    else:
#        print("\nStarting Over")
        pcounter = 0  # reset pcounter
        rcounter = 0  # reset rcounter
#        collect()  # start loop over

while True:
    try:
        collect()  # start the loop
    except Exception:
        system('python3 ~/sms.py YOUR_9_DIGIT_PHONE_NUMBER "Sensor broke"')
    finally:
        camera.stop_preview()
