#!/usr/bin/python3
# this script will communicate to Quectel EC25 through SixFab's Raspberry Pi 3G/4G-LTE Base HAT over serial using AT commands
# with this script you can control your Raspberry Pi via key words to do various functions
# Created by @Darthux
import serial
import sys
from time import sleep
from subprocess import Popen
from os import system

read_delay = 10  # how long to wait between checking sms messages in seconds
ADMIN = '0123456789'  # sms capable phone number for admin of system
PORT = '/dev/ttyUSB2'
RATE = 115200
modem = serial.Serial(PORT, RATE, timeout=1)
SMS_MODE = 'AT+CMGF=1\r'
LIST = 'AT+CMGL="ALL"\r'
CLEAR = 'AT+CMGD=1,4\r'
END = '\x1A'  # CTRL-Z

def sendCommand(command):
	modem.write(command.encode())
	sleep(0.2)

sendCommand(END)  # if python crashes mid sms composing this will exit composure
sendCommand(SMS_MODE)
modem.readline()  # ditch the first two readlines after sending SMS mode
modem.readline()
modem.flush()  # wait for response

def vnc():  # Open reverse VNC connection - only works if you have listening viewer
    sendCommand(SEND_SMS)
    sendCommand('Opening reverse VNC connection to VPI')
    sendCommand(END)
    system("x11vnc -display :0 -connect vpi & >> ~/lte/logs/vnclog.log")
#    print("vnc done")

def reboot():
    sendCommand(SEND_SMS)
    sendCommand('Rebooting')
    sendCommand(END)
    sleep(5)
    system("sudo reboot now")

def clear():
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Messages cleared')
    sendCommand(END)	# sending CTRL-Z

def shutdown():
    sendCommand(SEND_SMS)
    sendCommand('Shuting down')
    sendCommand(END)
    system("sudo shutdown now")

def read():  # Read the last 7 lines from the modem
    global r1, r2, r3, r4, r5, r6, n, num_ber
    sendCommand(LIST)
    r0 = modem.readline()
    r1 = modem.readline()
    r2 = modem.readline()
    r3 = modem.readline()
    r4 = modem.readline()
    r5 = modem.readline()
    r6 = modem.readline()
    n = str(r1[23:36])  # Pull out the phone number that sms is recieved from
    num_ber = n[2:12]  # remove the b''
    print(r0)
    print(r1)
    print(r2)  # message 1 text
    print(r3)
    print(r4)  # message 2 text
    print(r5)
    print(r6)  # message 3 text

read()  #  must take a reading before the global variables are usable below

while True:  # start the loop
    sleep(read_delay)
    read()  # Take a fresh reading every loop
    SEND_SMS = 'AT+CMGS="{}"\r'.format(num_ber)
    if b'Error Invalid Number' in r2:
        sendCommand(CLEAR)

# will check for the clear command in more than once place, this is helpful when your
# Raspberry Pi recieves any spam or unwanted messages and you need to clear them so it
# will read your command messages
    elif b'Clear' in r2 and num_ber == ADMIN:  # If "Clear" command comes from ADMIN (line 12)
        clear()
    elif b'Clear' in r3 and num_ber == ADMIN:
        clear()
    elif b'Clear' in r4 and num_ber == ADMIN:
        clear()
    elif b'Clear' in r5 and num_ber == ADMIN:
        clear()
    elif b'Clear' in r6 and num_ber == ADMIN:
        clear()

    elif b'Hi' in r2 and b'REC READ' in r1:  # Check for "Hi" and reply with "Hello"
#        print("Message received from " + num_ber)
        sendCommand(SEND_SMS)
        sendCommand('Hello')
        sendCommand(END)	# sending CTRL-Z
        sleep(1)
        sendCommand(CLEAR)

    elif b'+VNC' in r2 and num_ber == ADMIN:  # If "VNC" command comes from ADMIN (line 12)
        sendCommand(CLEAR)
        vnc()
    elif b'-VNC' in r2 and num_ber == ADMIN:  # If "VNC" command comes from ADMIN (line 12)
        system("pkill xllvnc")
        sleep(0.5)
        sendCommand(CLEAR)

    elif b'Reboot' in r2 and num_ber == ADMIN:  # If "Reboot" command comes from ADMIN (line 12)
        sendCommand(CLEAR)
        reboot()
    elif b'Reboot' in r3 and num_ber == ADMIN:
        sendCommand(CLEAR)
        reboot()

    elif b'Shutdown' in r2 and num_ber == ADMIN:  # If "Shutdown" command comes from ADMIN (line 12)
        clear()
        sleep(10)
        shutdown()

    else:
        print("\n********** Waiting for instructions **********")