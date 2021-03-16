#!/usr/bin/env python3
# this script will communicate to Quectel EC25 through SixFab's Raspberry Pi 3G/4G-LTE Base HAT over serial using AT commands
# with this script you can control your Raspberry Pi via key words to do various functions
# Created by @Darthux
import serial
from time import sleep
from subprocess import Popen
from os import system
from gpiozero import LED, PingServer

read_delay = 10  # how long to wait between checking sms messages in seconds
ADMIN = '0123456789'  # sms capable phone number for admin of system
ADMIN_SMS = 'AT+CMGS="{}"\r'.format(ADMIN)
PORT = '/dev/ttyUSB2'
RATE = 115200
modem = serial.Serial(PORT, RATE, timeout=1)
SMS_MODE = 'AT+CMGF=1\r'
LIST = 'AT+CMGL="ALL"\r'
CLEAR = 'AT+CMGD=1,4\r'  # clear SMS messages from inbox
END = '\x1A'  # CTRL-Z
google = PingServer('google.com')

# assign external LED's and flash them
blue = LED(20)
green = LED(21)
blue.off()
green.off()
green.blink()
sleep(0.2)
blue.blink()
sleep(5)
green.off()
blue.off()

def sendCommand(command):
    modem.write(command.encode())
    sleep(0.2)

sendCommand(END)  # if python crashes mid sms composing this will exit composure
sendCommand(SMS_MODE)
modem.readline()  # ditch the first two readlines after sending SMS mode
modem.readline()

sendCommand(ADMIN_SMS)
sendCommand('waiting for sms')
sendCommand(END)

def net_check():  # blink external green LED if internet connection is good
    sendCommand(CLEAR)
    if google.is_active:
        green.blink()
        sleep(5)
        green.off()
    else:
        green.off()

def uptime():  # get current uptime and send to requestor
    sendCommand(CLEAR)
    blue.blink()
    system('uptime >> /home/pi/uptime.txt')
    sleep(1)
    with open("/home/pi/uptime.txt", "r") as F1:
        for line in F1:
            pass
    last_line = line
    uptime = last_line#[10:26]
    sendCommand(SEND_SMS)
    sendCommand(uptime)
    sendCommand(END)
    F1.close()
    blue.off()

def data():  # read last line in file and SMS it to requestor
    sendCommand(CLEAR)
    blue.blink()
    with open("/home/pi/bme280_data.csv", "r") as F2:
        for line in F2:
            pass
        last_reading = line
        sendCommand(SEND_SMS)
        sendCommand(last_reading)
        sendCommand(END)
        F2.close()
        blue.off()

def vnc():  # Open reverse VNC connection - only works if you have listening viewer
    sendCommand(SEND_SMS)
    sendCommand('Opening reverse VNC connection to VPI')
    sendCommand(END)
    system("x11vnc -display :0 -connect vpi & >> ~/lte/logs/vnclog.log")
    sendCommand(CLEAR)
#    print("vnc done")

def reboot():
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Rebooting')
    sendCommand(END)
    sleep(5)
    system("sudo reboot now")

def clear():
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Messages cleared')
    sendCommand(END)  # sending CTRL-Z

def shutdown():
    sendCommand(CLEAR)
    sendCommand(SEND_SMS)
    sendCommand('Shuting down')
    sendCommand(END)
    sleep(5)
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

read()  # must take a reading before the global variables are usable below

# MMS
APN = 'AT+QICSGP=1,1,"_PUT_YOUR_APN_HERE_","" ,"",1\r'  # Configure and activate a PDP context
CON = 'AT+QMMSCFG="contextid",1\r'
MMSC = 'AT+QMMSCFG="mmsc","_PUT_YOUR_MMSC_HERE_t"\r'
PROXY = 'AT+QMMSCFG="proxy","_PUT_YOUR_PROXY_HERE_",80\r'
PARAM = 'AT+QMMSCFG="sendparam",6,2,0,0,2,4\r'
SUP = 'AT+QMMSCFG="supportfield",0\r'
CHAR = 'AT+QMMSCFG="character","ASCII"\r'
SUBJ = 'AT+QMMSEDIT=4,1,"last image"\r'  # MMS subject
UPL = 'AT+QFUPL="RAM:photo.jpg",300,300,1\r'  # upload file for MMS
ATTACH = 'AT+QMMSEDIT=5,1,"RAM:photo.jpg"\r'  # attach uploaded file to MMS
MMSSEND = 'AT+QMMSEND=100\r'  # send the MMS
MMSCLEAR = 'AT+QMMSEDIT=0\r'  # clear current MMS
RAM = 'AT+QFDEL="RAM:*"\r'  # delete uploaded attachments

def mms():  # in progress
    sendCommand(APN)
    sendCommand(CON)
    sendCommand(MMSC)
    sendCommand(PROXY)
    sendCommand(PARAM)
    sendCommand(TO)
    sendCommand(CHAR)
    sendCommand(SUBJ)
    sendCommand(UPL)

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

    elif b'SSH' in r2 and num_ber == ADMIN:  # Start reverse SSH
        sendCommand(CLEAR)
        sendCommand(SEND_SMS)
        sendCommand('starting SSH')
        sendCommand(END)
        Popen(['ssh -B wwan0 -N -R 2222:localhost:22 user@host'], shell=True)  # ssh -p 2222 localhost to access from local server 

    elif b'+VNC' in r2 and num_ber == ADMIN:  # If "+VNC" command comes from ADMIN (line 12)
        sendCommand(CLEAR)
        vnc()
    elif b'-VNC' in r2 and num_ber == ADMIN:  # If "-VNC" command comes from ADMIN (line 12)
        sendCommand(CLEAR)
	sleep(0.5)
	sendCommand(ADMIN_SMS)
        sendCommand('See you next time')
        sendCommand(END)
        system("pkill x11vnc")  # kill VNC server

    elif b'Sync' in r2 and num_ber == ADMIN:
        sendCommand(CLEAR)
        blue.blink()
        Popen(['/home/pi/rsync.py'])
        blue.off()

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

    else:
        print("\n********** Waiting for instructions **********")
