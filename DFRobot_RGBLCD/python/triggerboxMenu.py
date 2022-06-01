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
  try:
    p1 = subprocess.run("date +%x", shell=True, capture_output=True, text=True)
    p2 = subprocess.run("date +%T", shell=True, capture_output=True, text=True)
    timevalbox.setMessage(p1.stdout)
    datevalbox.setMessage(p2.stdout)
  except Exception as e:
    print("Update time and date is broken")
    print(e)

def updateSystemctlTask():
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

mainMenuList = []
optionsMenuList = []
menuIndex = 0
loopingFlag = True

def menuLoop(direction):
  global loopingFlag
  if loopingFlag == True:
    global menuIndex
    menuIndex = menuIndex + direction
    if menuIndex > len(mainMenuList)-1:
      menuIndex = 0
    if menuIndex < 0:
      menuIndex = len(mainMenuList)-1

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

#options for systemctl menu
systemctlOptions = ScrollMenu()
restartNTP = Option("Restart NTP")
restartTrigbox = Option("Restart T-box")
adjustCamera1 = Option("C1 Degrees", 360, 1, 360, 0, 3)
systemctlOptions.addOptions(restartNTP)
systemctlOptions.addOptions(restartTrigbox)
systemctlOptions.addOptions(adjustCamera1)

#systemctl menu
systemctlMenu = Menu()
systemctlMenu.setScrollMenu(systemctlOptions)
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

#Flash menu function
flashMenu = Menu()
l1box = Printbox(0, 0, 15)
l2box = Printbox(1, 0, 15)
flashMenu.addPrintbox(l1box)
flashMenu.addPrintbox(l2box)
def flash(line1, line2):
  l1box.setMessage(line1)
  l2box.setMessage(line2)
  flashMenu.display(False)
  time.sleep(1.0)

#main menu order list
mainMenuList.append(timeMenu)
mainMenuList.append(systemctlMenu)

#options menu list
optionsMenuList.append

#task stuff
schedule.every(1).seconds.do(updateTimeTask).tag('menuTask')
schedule.every(10).seconds.do(updateSystemctlTask).tag('menuTask')
schedule.every(6).seconds.do(menuLoop, 1)

#main loop
updateSystemctlTask()
updateTimeTask()
optionsMenuFlag = False
mainMenuFlag = True

while True:
  schedule.run_pending()
  currentMenu = mainMenuList[menuIndex]

  #The main menu state
  if mainMenuFlag == True: 
    if read_LCD_buttons() == btnRIGHT: #skip to next menu
      loopingFlag = True # resume the main menu loop
      menuLoop(1)
      time.sleep(0.2)  
      optionsMenuFlag = False

    if read_LCD_buttons() == btnLEFT: #previous menu
      loopingFlag = True # resume the main menu loop
      menuLoop(-1)   
      time.sleep(0.2)
      optionsMenuFlag = False

    if read_LCD_buttons() == btnSELECT:
      if loopingFlag == False:
        flash("Showing options", "Use <> to resume")
        options = currentMenu.getScrollMenu()
        options.setSelector(0)
        optionsMenuFlag = True
        mainMenuFlag = False
        continue #skips to the options menu directly for a smoother transition since display isnt called

      loopingFlag = False #freezes the menu for monitoring or further action
      flash("Monitoring menu", "Use <> to resume")

    currentMenu.display(False)    #this is where the menu actually gets displayed for the mainmenu state


  #The options menu state
  if optionsMenuFlag == True:  
    if read_LCD_buttons() == btnRIGHT or read_LCD_buttons() == btnLEFT: 
      flash("Returning to", "main menu")
      mainMenuFlag = True
      optionsMenuFlag = False
      loopingFlag = True
      time.sleep(0.2)  
      continue  #skips the display of the options menu for a smoother transition

    if read_LCD_buttons() == btnUP:
      if loopingFlag == False and optionsMenuFlag == True:
        options.setSelector(-1)

      time.sleep(0.2)

    if read_LCD_buttons() == btnDOWN:
      if loopingFlag == False and optionsMenuFlag == True:
        options.setSelector(1)

      time.sleep(0.2)
    currentMenu.display(True)

