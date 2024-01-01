#! /usr/bin/python3

# This script sends SMS from Sixfab GSM/SPRS shield, 3G,4G/LTE Base Shield v2, RPi Cellular IoT App. Shield
# for running it: python3 sms.py <NUMBER> <"Your Message">
# Example: python3 sms.py +0123456789 "This is sample message"

import sys
import serial
from time import sleep

NUM = sys.argv[1]
MSG = sys.argv[2]

SERIAL_PORT = '/dev/ttyUSB3'
SERIAL_RATE = 115200
ser = serial.Serial(SERIAL_PORT,SERIAL_RATE)


OPERATE_SMS_MODE = 'AT+CMGF=1\r'
SEND_SMS = 'AT+CMGS="{}"\r'.format(NUM)

def sendCommand(command):
	ser.write(command.encode())
	sleep(0.2)
	
def main():
	print ("Sending SMS to {}".format(NUM))
	if not ser.is_open:
		ser.open()

	if ser.is_open:
		sendCommand(OPERATE_SMS_MODE)
		sendCommand(SEND_SMS)
		sendCommand(MSG)
		sendCommand('\x1A')	#sending CTRL-Z
							#https://en.wikipedia.org/wiki/ASCII
		ser.close()

if __name__ == "__main__":
	try:
		main()
	except ValueError as e:
		print ("Error : {}".format(e))
