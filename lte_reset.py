# reset (power cycle) SixFab's 3G/4G-LTE Base HAT without rebooting
# created by @Darthux
from gpiozero import LED
import sys

reset = LED(26)  # not really LED
reset.on()
sleep(3)
reset.off()
sys.exit()