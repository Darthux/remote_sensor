#!/usr/bin/env python3
# Boots off backup power (lipo).
# Disables all non essential devices
# Checks power voltages/percents on both batteries
# Starts up rest of system if on primary power
#
#	USE  PIN        BCM	     BCM    PIN	USE
#        3V3 (01)			        (02) 5V
#       SDA1 (03)	GP02		    (04) 5V
#       SCL1 (05)	GP03		    (06) GND
# RTC_SQWOUT (07)	GP04	GP14	(08) UART_TX
#        GND (09)	        GP15    (10) UART_RX
#  E-INK_RST (11)	GP17	GP18	(12) E-INK_D/C
#     SF_LED (13)	GP27		    (14) GND
#  E-INK_ENA (15)	GP22	GP23	(16) FAN1
#        3V3 (17)	        GP24    (18) FAN2
# E-INK_MOSI (19)	GP10		    (20) GND
# E-INK_MISO (21)	GP09	GP25	(22)
#  E-INK_SCK (23)	GP11	GP08	(24) E-INK_ECS
#        GND (25)	        GP07	(26) RGB_LED_R
#  RGB_LED_B (27)	GP00	GP01	(28) RGB_LED_G
#       FAN3 (29)	GP05		    (30) GND
#    SF_RING (31)	GP06	GP12	(32) RELAY_SIG
#  E-INK_BSY (33)	GP13		    (34) GND
#SF_AIRPLANE (35)	GP19	GP16	(36) BACKUP_EN (TPS61023_EN)
# SF_PWR_OFF (37)	GP26	GP20	(38) E-INK_SRC
#        GND (39)	        GP21	(40) LC709203F_INT

from time import sleep
import board
from adafruit_lc709203f import LC709203F
import adafruit_ina260
from gpiozero import OutputDevice
from os import system
#from subprocess import Popen
#import sys

i2c = board.I2C()  # uses board.SCL and board.SDA
relay = OutputDevice(12)  # non-latching relay NO=lipo, COM=USB, NC=AGM
agm = adafruit_ina260.INA260(i2c)
lipo = LC709203F(i2c)
miniboost = OutputDevice(16)  # connected to pn2222 to ground
lte_hat = OutputDevice(26)

sleep(2)
system('python3 ~/sms.py YOUR_9_DIGIT_NUMBER "I Have booted"')
#  if the hat was disabled while program crashes, this will turn it back on.
if lte_hat.value == 0:
    lte_hat.on()
    sleep(5)
    lte_hat.off()
    sleep(10)
else:
    pass


#  battery voltages and percents
agm_min = 4.9
agm_mid = 5.6
agm_max = 6.1
lipo_max = 80
lipo_mid = 50
lipo_min = 30

print("main battery voltage: " + str(agm.voltage))
#print("backup battery voltage: " + str(lipo.cell_voltage))
print("backup battery percent is: " + str(lipo.cell_percent) + "%")

def main_power():
    print("Switching to primary power")
    if lte_hat.value == 1:
        lte_hat.off()
        sleep(30)
    else:
        pass

    if relay.value == 0:
        relay.on()
        sleep(5)
        system('python3 ~/sms.py YOUR_9_DIGIT_NUMBER "Running on primary power"')
        sleep(1)
        system('/home/pi/sensor_main.sh & >> /home/pi/logs/sensor_main.log')
        sleep(2)
        system('/home/pi/smsread.sh & >> /home/pi/logs/smsread.log')
    else:
        pass

    sleep(.5)
    if miniboost.value == 0:
        miniboost.on()
    else:
        pass

def backup_power():
    print("Switching to backup power")
    if lte_hat.value == 1:
        pass
    else:
        system('python3 ~/sms.py YOUR_9_DIGIT_NUMBER "Running on backup power"')

    sleep(5)
    if lte_hat.value == 0:
        lte_hat.on()
    else:
        pass

    sleep(.5)
    if miniboost.value == 1:
        miniboost.off()
    else:
        pass

    sleep(.5)
    if relay.value == 1:
        relay.off()
    else:
        pass

def the_loop():
    print("agm voltage: " + str(agm.voltage))
    print("lipo %: " + str(lipo.cell_percent))
    print("relay value: " + str(relay.value))
    if relay.value == 1:
        if agm.voltage >= agm_max:
            main_power()
            sleep(60*120)
        elif agm.voltage >= agm_mid:
            main_power()
            sleep(60*60)
        elif agm.voltage <= agm_min:
            backup_power()
            sleep(60*30)
    elif relay.value == 0:
        if agm.voltage > agm_min:
            main_power()
            sleep(60*60)
        elif lipo.cell_percent >= lipo_max:
            sleep(60*30)
        elif lipo.cell_percent >= lipo_mid:
            sleep(60*120)
        elif lipo.cell_percent <= lipo_min:
            sleep(60*360)

while True:
    the_loop()  # start the loop
