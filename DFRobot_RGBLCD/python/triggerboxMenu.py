import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
import time
from Menu import * #import menu class

GPIO.setmode(GPIO.BCM)
# Define keys
lcd_key     = 0
key_in  = 0

btnRIGHT  = 0
btnUP     = 1
btnDOWN   = 2
btnLEFT   = 3
btnSELECT = 4

GPIO.setup(16, GPIO.IN)
GPIO.setup(17, GPIO.IN)
GPIO.setup(18, GPIO.IN)
GPIO.setup(19, GPIO.IN)
GPIO.setup(20, GPIO.IN)


#Read the key value
def read_LCD_buttons():
  key_in16 = GPIO.input(16)
  key_in17 = GPIO.input(17)
  key_in18 = GPIO.input(18)
  key_in19 = GPIO.input(19)
  key_in20 = GPIO.input(20)
 
  if (key_in16 == 1):
    return btnSELECT
  if (key_in17 == 1):
    return btnUP
  if (key_in18 == 1):
    return btnDOWN
  if (key_in19 == 1):
    return btnLEFT
  if (key_in20 == 1):
    return btnRIGHT


menu1 = Menu("Triggerbox", 1)
menu2 = Menu("GPS", 0)

while True:
    menu1.display()
    time.sleep(1.0)
    menu2.display()
    time.sleep(1.0)