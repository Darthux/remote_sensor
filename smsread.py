#!/usr/bin/env python3
# this script will communicate to Quectel EC25 through SixFab's Raspberry Pi 3G/4G-LTE Base HAT over serial using AT commands
# with this script you can control your Raspberry Pi via key words to do various functions
# Created by @Darthux
import serial
import socket
from time import sleep
from subprocess import Popen
from os import system
from gpiozero import RGBLED, PingServer
from colorzero import Color
import board
#from adafruit_lc709203f import LC709203F

read_delay = 10  # how long to wait between checking sms messages in seconds

ADMIN = 'YOUR_9_DIGIT_PHONE_NUMBER'  # sms capable phone number for admin of system
ADMIN_SMS = 'AT+CMGS="{}"\r'.format(ADMIN)
PORT = '/dev/ttyUSB3'
RATE = 115200
sleep(10)
modem = serial.Serial(PORT, RATE, timeout=2)
SMS_MODE = 'AT+CMGF=1\r'
LIST = 'AT+CMGL="ALL"\r'
CLEAR = 'AT+CMGD=3,4\r'
END = '\x1A'  # CTRL-Z
google = PingServer('google.com')


'''
#  External RGB LED to provide updated statuses.
#  Currently disabled until prototype PCB v2 working
led = RGBLED(red=26, green=28, blue=27)
_range = 25
# RED
for n in range(_range):
    led.color = (n/_range, 0, 0)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (n/_range, 0, 0)
    sleep(0.1)
led.color = (0, 0,0)
# GREEN
for n in range(_range):
    led.color = (0, n/_range, 0)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (0, n/_range, 0)
    sleep(0.1)
led.color = (0, 0,0)
# BLUE
for n in range(_range):
    led.color = (0, 0, n/_range)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (0, 0, n/_range)
    sleep(0.1)
led.color = (0, 0, 0)
# MAGENTA
for n in range(_range):
    led.color = (n/_range, 0, n/_range)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (n/_range, 0, n/_range)
    sleep(0.1)
led.color = (0, 0, 0)
# cyan
for n in range(_range):
    led.color = (0, n/_range, n/_range)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (0, n/_range, n/_range)
    sleep(0.1)
led.color = (0, 0, 0)
for n in range(_range):
    led.color = (n/_range, n/_range, n/_range)
    sleep(0.1)
for n in range(_range,-1, -1):
    led.color = (n/_range, n/_range, n/_range)
    sleep(0.1)
led.color = (0, 0, 0)  # off
'''

#  Sending AT commands to modem
def sendCommand(command):
    modem.write(command.encode())
    sleep(0.3)

# sendCommand(CLEAR)  # to clear messages upon start for troubleshooting

# Colors for RGB LED
def red(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(1,0,0), n=number_of_blinks, background = False)
def blue(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(0,0,1), n=number_of_blinks, background = False)
def green(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(0,1,0), n=number_of_blinks, background = False)
def cyan(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(0,1,1), n=number_of_blinks, background = False)
def white(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(1,1,1), n=number_of_blinks, background = False)
def magenta(number_of_blinks):
    led.blink(on_time=0.5, off_time=0.5, on_color=(1,0,1), n=number_of_blinks, background = False)

sendCommand(END)  # if python crashes mid sms composing, this will exit composure
sendCommand(SMS_MODE)
modem.readline()  # ditch the first two readlines after sending SMS mode
modem.readline()

def net_check():
    sendCommand(CLEAR)
    if google.is_active:
#        green(3)
    else:
        pass

# Reset stats, logs and photos
def reset():
    sendCommand(CLEAR)
#    red(1)
    logtime_clear()
    system('rm /home/pi/uptime.txt')
#    red(1)
    system('rm /home/pi/temperature_data.csv')
#    red(1)
    system('rm /home/pi/lte/backup/Pictures/*.jpg')
    sendCommand(ADMIN_SMS)
    sendCommand('reset complete')
    sendCommand(END)

# Send current uptime
def uptime():
    sendCommand(CLEAR)
#    cyan(6)
    system('uptime >> /home/pi/uptime.txt')
    sleep(1)
    with open('/home/pi/uptime.txt', 'r') as F1:
        for line in F1:
            pass
    uptime = line
    sendCommand(SEND_SMS)
    sendCommand(uptime)
    sendCommand(END)
    F1.close()

# Send temperature Data
def data():
    sendCommand(CLEAR)
#    cyan(4)
    with open('/home/pi/temperature_data.csv', 'r') as F2:
        for line in F2:
            pass
        data = line
    sendCommand(SEND_SMS)
    sendCommand(data)
    sendCommand(END)
    F2.close()
# Open reverse VNC connection - only works if you have listening viewer
def vnc():  # VNC+
    sendCommand(SEND_SMS)
    sendCommand('Opening reverse VNC connection to YOUR_HOST_HERE')
    sendCommand(END)
    system("x11vnc -display :0 -connect YOUR_IP/HOST & >> ~/lte/logs/vnclog.log")
    sendCommand(CLEAR)
#    print("vnc done")


def reboot():
#    magenta(2)
#    white(2)
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Rebooting in 5 seconds')
    sendCommand(END)
    sleep(5)
    system("sudo reboot now")

# Clear SMS messages
def clear():
#    green(2)
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Messages cleared')
    sendCommand(END)  # sending CTRL-Z


def shutdown():
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Shuting down')
    sendCommand(END)
#    blue(15)
#    sleep(0.2)
#    green(15)
    sleep(5)
    system("sudo shutdown now")

def sync():
    sendCommand(CLEAR)
#    system('sudo ifmetric wwan0 300') # used for other RPi. (not for 2B)
#    blue(4)
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = ("DESTINATION_IP/HOSTMANE", 22)
    result_of_check = a_socket.connect_ex(location)
    if result_of_check == 0:
    #    print("starting rsync")
#        system("rsync -avz --recursive /home/pi/ pi@DESTINATION_IP/HOSTNAME:FOLDER")
        sendCommand(ADMIN_SMS)
        sendCommand('sync complete')
        sendCommand(END)
    else:
    #    print("vpi unreachable")
        system('python3 ~/sms.py YOUR_9_DIGIT_PHONE_NUMBER "rsync failed"')

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

read()  # must take a reading before the global variables are usable below


'''
# MMS NOT YET WORKING
APN = 'AT+QICSGP=1,1,"YOUR_APN","" ,"",1\r'  # Configure and activate a PDP context
CON = 'AT+QMMSCFG="contextid",1\r'
MMSC = 'AT+QMMSCFG="mmsc","YOUR_MMSC"\r'
PROXY = 'AT+QMMSCFG="proxy","YOUR_PROXY",80\r'
PARAM = 'AT+QMMSCFG="sendparam",6,2,0,0,2,4\r'
SUP = 'AT+QMMSCFG="supportfield",0\r'
CHAR = 'AT+QMMSCFG="character","ASCII"\r'
SUBJ = 'AT+QMMSEDIT=4,1,"last image"\r'
UPL = 'AT+QFUPL="RAM:photo.jpg",300,300,1\r'
ATTACH = 'AT+QMMSEDIT=5,1,"RAM:photo.jpg"\r'
MMSSEND = 'AT+QMMSEND=100\r'
MMSCLEAR = 'AT+QMMSEDIT=0\r'
RAM = 'AT+QFDEL="RAM:*"\r'

def mms():
    sendCommand(APN)
    sendCommand(CON)
    sendCommand(MMSC)
    sendCommand(PROXY)
    sendCommand(PARAM)
    sendCommand(TO)
    sendCommand(CHAR)
    sendCommand(SUBJ)
    sendCommand(UPL)
'''

# Text me to let me know you're running
sendCommand(ADMIN_SMS)
sendCommand('waiting for sms')
sendCommand(END)

while True:  # start the loop
    sleep(read_delay)
    sendCommand(END)
    read()  # Take a fresh reading every loop
    TO = 'AT+QMMSEDIT=1,1,"{}"\r'.format(num_ber)
    SEND_SMS = 'AT+CMGS="{}"\r'.format(num_ber)
    if b'Error Invalid Number' in r2:
        sendCommand(CLEAR)
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
        sendCommand(END)  # sending CTRL-Z
        sleep(1)
        sendCommand(CLEAR)

    elif b'SSH' in r2 and num_ber == ADMIN:
        sendCommand(CLEAR)
        sendCommand(SEND_SMS)
        sendCommand('starting SSH')
        sendCommand(END)
        Popen(['ssh -N -R 2222:localhost:22 pi@YOUR_DESTINATION_IP/HOSTNAME'], shell=True)

    elif b'+VNC' in r2 and num_ber == ADMIN:  # If "+VNC" command comes from ADMIN (line 12)
        sendCommand(CLEAR)
        vnc()
    elif b'-VNC' in r2 and num_ber == ADMIN:  # If "-VNC" command comes from ADMIN (line 12)
        system("pkill x11vnc")
        sleep(0.5)
        sendCommand(CLEAR)

    elif b'Sync' in r2 and num_ber == ADMIN:
        sync()

    elif b'Reboot' in r2 and num_ber == ADMIN:  # If "Reboot" command comes from ADMIN (line 12)
        reboot()

    elif b'Shutdown' in r2 and num_ber == ADMIN:  # If "Shutdown" command comes from ADMIN (line 12)
        shutdown()

    elif b'Data' in r2 and b'REC READ' in r1:
        data()

    elif b'Network' in r2 and b'REC READ' in r1:
        net_check()

    elif b'Uptime' in r2 and b'REC READ' in r1:
        uptime()

    elif b'Reset' in r2 and num_ber == ADMIN:  # If "Reset" command comes from ADMIN (line 12)
        reset()

    elif b'Stats' in r2 and b'REC READ' in r1:
        uptime()
        data()

    elif b'HELP' in r2 and num_ber == ADMIN:  # Forget what commands are available?
        sendCommand(CLEAR)
        sendCommand(ADMIN_SMS)
        sendCommand('Clear Uptime Reset Stats SSH +VNC -VNC Sync Reboot Shutdown Data Network Uptime')
        sendCommand(END)

    elif b'REC READ' in r1 and num_ber != ADMIN: # FWD incoming messages
        sendCommand(CLEAR)
        sleep(1)
        sendCommand(ADMIN_SMS)
        sendCommand('Message from ' + num_ber + ' with message: ' + str(r2))
        sendCommand(END)

    else:
        print("\n********** Waiting for instructions **********")
