#!/usr/bin/env python3
# Sensor: Waveshare BME280 Environmental Sensor using the adafruit_bme280 library
# and their sammple code. credit to https://github.com/adafruit/Adafruit_CircuitPython_BME280
# Camera: Raspberry Pi Camear Module V2 (RPI-CAM-V2)
# This script will:
#  a. read and display sensor information from BME280
#  b. overlay BME280 readings on captured photo
#  c. save the captured data to a spreadsheet
# Created by @Darthux 20210212

from picamera import PiCamera, Color  # for camera
from time import time, sleep, strftime  # for camera
import board  # for BME280
import busio  # for BME280
import adafruit_bme280  # for BME280
import csv  # writing and data into csv
from subprocess import Popen
from os import system

camera = PiCamera()  # defind the camera outside of def incase i want to use it elsewhere
camera.start_preview()  # activate camera

Popen(["/home/pi/lte/lte_led.py"])  # start led for ping
sleep(2)
Popen(["/home/pi/sms/smsread.py"])  # start sms control script

# ASCII characters for some symbols I will be using. thank you www.codetable.net
percent = chr(37)  # %
degrees = chr(176)  # °
Cr = chr(10)  # New line (carrige return)

# configure the BME280 sensor and define its stats
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
def gather():
    # Change this to match the location's pressure (hPa) at sea level
    bme280.sea_level_pressure = 1070.8
    bme280.mode = adafruit_bme280.MODE_NORMAL
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme280.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme280.overscan_temperature = adafruit_bme280.OVERSCAN_X2
    global tempc, tempf, pres, hum, alt
    tempc = bme280.temperature
    tempf = round(((tempc * (9/5))+32), 1)  # Temperature output to F
    pres = round(bme280.pressure, 1)
    hum = round(bme280.relative_humidity)
    alt = round(bme280.altitude)

    # easy way for me to merge all the text and data into string
    global T, e, p, Tep, Temp
    T = "Temperature: "
    e = str(tempf)
    p = "F"
    Tep = str(T + e + p)
    Temp = str(T + e + degrees + p)

    global P, r, Pres
    P = "Preassure: "
    r = str(pres)
    Pres = str(P + r)

    global H, u, m, Hum
    H = "Humidity: "
    u = str(hum)
    m = percent
    Hum = str(H + u + m)

    global A, l, t, Alt
    A = "Altitude: "
    l = str(alt)
    t = "'"
    Alt = str(A + l + t)
gather()  # get first readings and discard them

"""
# display reading from the sensor - only used in command line for troubleshooting
def show_temp():
    global Temp
    print(Temp)

def show_hum():
    global Hum
    print(Hum)

def show_pres():
    global Pres
    print(Pres)

def show_alt():
    global Alt
    print(Alt)
"""

# adding data to CSV
def log():
    gather()
#    print(Temp)
    now = strftime('%m%d%Y-%H%M%S')  # output is MMDDYYYY-HHMMSS
    f = open("/home/pi/thp/bme280_data.csv", "a", newline = "")
    tup1 = (now, tempf, (str(hum) + percent), pres)
    writer = csv.writer(f)
    writer.writerow(tup1)
    f.close

# define what to do when taking a photo
def get_image():
#    camera.start_preview()  # activate camera
#    sleep(3)  # PiCamera documentation recommends at least 2 seconds to allow auto adjust
    now = strftime('%m%d%Y-%H%M')  # output is MMDDYYYY-HHMM
    camera.resolution = (1920, 1080)  # set resolution
    camera.brightness = 50  # set brightness
    camera.annotate_text_size = 30
    camera.annotate_foreground = Color('white')
    camera.annotate_background = Color('black')
    log()  # get fresh readings before taking photo
    camera.annotate_text = now + Cr + Tep + Cr + Hum + Cr + Pres  # text overlay goes here
    filename = "/home/pi/tlapse/" + now + ".jpg"  # output is MMDDYYYY-HHMMSS.jpg
    camera.capture(filename)  # take the photo and save as filename
#    sleep(0.5)  # just because, not needed
#    camera.stop_preview()  # deactivate camera

rcounter = 0
lcounter = 0
pcounter = 0
x = 10  # how many readings before photo
y = 60  # how often to sleep for readings
z = 600  # take photo on nth minute
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
    finally:
        camera.stop_preview()
