import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
import time
import subprocess
import schedule
from Menu import *
from Printbox import *

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

def updateTimeTask():
  p1 = subprocess.run("date +%x", shell=True, capture_output=True, text=True)
  p2 = subprocess.run("date +%T", shell=True, capture_output=True, text=True)
  timevalbox.setMessage(p1.stdout)
  datevalbox.setMessage(p2.stdout)

def updateSystemctl():
  try:
    subprocess.run("systemctl is-active --quiet triggerbox", shell=True, check=True)
    tbboxvalbox.setMessage("Active")
  except subprocess.CalledProcessError:
    tbboxvalbox.setMessage("Failed")
  try:
    subprocess.run("systemctl is-active --quiet ntp", shell=True, check=True)
    ntpvalbox.setMessage("Active")
  except subprocess.CalledProcessError:
    ntpvalbox.setMessage("Failed")

menuList = []
menuIndex = 0
def menuLoop():
  global menuIndex
  if menuIndex < len(menuList)-1:
    menuIndex = menuIndex+1
  else:
    menuIndex = 0
#setting up menu stuff

timeMenu = Menu()
timebox = Printbox(0, 0, 7)# line, begin, end
datebox = Printbox(1, 0, 7)# line, begin, end
datevalbox = Printbox(0, 8, 15)
timevalbox = Printbox(1, 8, 15)
timebox.setMessage("Time:")
datebox.setMessage("Date:")
timeMenu.addPrintbox(timebox)
timeMenu.addPrintbox(datebox)
timeMenu.addPrintbox(timevalbox)
timeMenu.addPrintbox(datevalbox)

systemctlMenu = Menu()
tbbox = Printbox(0, 0, 9)
ntpbox = Printbox(1, 0, 9)
tbboxvalbox = Printbox(0, 10, 15)
ntpvalbox = Printbox(1, 10, 15)
tbbox.setMessage("Trigbox:")
ntpbox.setMessage("NTP:")
systemctlMenu.addPrintbox(tbbox)
systemctlMenu.addPrintbox(ntpbox)
systemctlMenu.addPrintbox(tbboxvalbox)
systemctlMenu.addPrintbox(ntpvalbox)

#menu order
menuList.append(timeMenu)
menuList.append(systemctlMenu)

#task stuff
schedule.every(1).seconds.do(updateTimeTask).tag('menuTask')
schedule.every(10).seconds.do(updateSystemctl).tag('menuTask')
schedule.every(5).seconds.do(menuLoop).tag('menuTask')

#main loop
while True:
  schedule.run_pending()
  menuList[menuIndex].display()


