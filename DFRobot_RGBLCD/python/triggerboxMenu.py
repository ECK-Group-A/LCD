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

#gpio for buttons
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

#scheduler task to update time
def updateTimeTask():
  try:
    p1 = subprocess.run("date +%x", shell=True, capture_output=True, text=True)
    p2 = subprocess.run("date +%T", shell=True, capture_output=True, text=True)
    timevalbox.setMessage(p1.stdout)
    datevalbox.setMessage(p2.stdout)
  except Exception as e:
    print("Update time and date is broken")
    print(e)

#scheduler taskt o update systemctl
def updateSystemctlTask():
  try:
    subprocess.run("systemctl is-active --quiet triggerbox", shell=True, check=True)
    tbboxvalbox.setMessage("Active")
  except subprocess.CalledProcessError:
    tbboxvalbox.setMessage("Down")
  try:
    subprocess.run("systemctl is-active --quiet chrony", shell=True, check=True)
    chronyvalbox.setMessage("Active")
  except subprocess.CalledProcessError:
    chronyvalbox.setMessage("Down")

#some 'globals' for the menuloop task
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

#setting up time menu stuff
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
restartChrony = Option("Restart Chrony")
restartTrigbox = Option("Restart T-box")
restartChrony.addCommand("sudo systemctl restart chrony")
restartChrony.execute()
restartTrigbox.addCommand("sudo systemctl daemon-reload")
restartTrigbox.addCommand("sudo systemctl restart triggerbox")
systemctlOptions.addOptions(restartChrony)
systemctlOptions.addOptions(restartTrigbox)

#systemctl menu
systemctlMenu = Menu()
systemctlMenu.setScrollMenu(systemctlOptions)
tbbox = Printbox(0, 0, 9)
chronybox = Printbox(1, 0, 9)
tbboxvalbox = Printbox(0, 10, 15)
chronyvalbox = Printbox(1, 10, 15)
tbbox.setMessage("Trigbox:")
chronybox.setMessage("Chrony:")
systemctlMenu.addPrintbox(tbbox)
systemctlMenu.addPrintbox(chronybox)
systemctlMenu.addPrintbox(tbboxvalbox)
systemctlMenu.addPrintbox(chronyvalbox)

#settings file
cameraAnglesFile = "/etc/triggerbox.conf"
cameraAngles = []
with open(cameraAnglesFile,"r") as file:
    lines = file.readlines()
    for line in lines:
      strippedLine = line.strip()
      strippedLine = strippedLine[3:]
      if strippedLine.isnumeric(): 
        cameraAngles.append(int(strippedLine))
file.close()

#camera scroll menu
cameraOptions = ScrollMenu()
adjustCamera1 = Option("Cam 1 Angle", cameraAngles[0], 1, 360, 0, 3)
adjustCamera2 = Option("Cam 2 Angle", cameraAngles[1], 1, 360, 0, 3)
adjustCamera3 = Option("Cam 3 Angle", cameraAngles[2], 1, 360, 0, 3)
adjustCamera4 = Option("Cam 4 Angle", cameraAngles[3], 1, 360, 0, 3)
adjustCamera5 = Option("Cam 5 Angle", cameraAngles[4], 1, 360, 0, 3)
adjustCamera6 = Option("Cam 6 Angle", cameraAngles[5], 1, 360, 0, 3)
cameraOptions.addOptions(adjustCamera6)
cameraOptions.addOptions(adjustCamera5)
cameraOptions.addOptions(adjustCamera4)
cameraOptions.addOptions(adjustCamera3)
cameraOptions.addOptions(adjustCamera2)
cameraOptions.addOptions(adjustCamera1)
cameraOptions.addOptions(restartTrigbox)

#camera menu
cameraMenu = Menu()
cameraMenu.setScrollMenu(cameraOptions)
camerasbox = Printbox(0, 0, 15)
camerastatusbox = Printbox(1, 0, 15)
camerasbox.setMessage("Camera status:")
camerastatusbox.setMessage("-unimplemented-")
cameraMenu.addPrintbox(camerasbox)
cameraMenu.addPrintbox(camerastatusbox)


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
mainMenuList.append(cameraMenu)

#options menu list
optionsMenuList.append

#task stuff
schedule.every(1).seconds.do(updateTimeTask).tag('menuTask')
schedule.every(5).seconds.do(updateSystemctlTask).tag('menuTask')
schedule.every(6).seconds.do(menuLoop, 1)

#main loop vars and inits
updateSystemctlTask()
updateTimeTask()
optionsMenuFlag = False
mainMenuFlag = True
optionSelectedFlag = False

#loop
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
        flash("Showing options", "Use <> to return")
        options = currentMenu.getScrollMenu()
        options.setSelectorIcon("<")
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

    if read_LCD_buttons() == btnSELECT:
      #is there something to execute?
      selected = options.select()
      success = selected.execute()
      if success:
        options.setSelector(0)
        time.sleep(0.2)

      #if there is nothing to execute instead select the option and change state
      else:
        optionSelectedFlag = True
        optionsMenuFlag = False
        options.setSelectorIcon("*")
        options.setSelector(0)
        time.sleep(0.2)
        continue


  #option selected state
  if optionSelectedFlag == True:
    selected = options.select()

    #only needed when adjusting values
    if read_LCD_buttons() == btnLEFT:
      selected.incrementValue(-1)
      currentMenu.scrollMenu.update(cameraAnglesFile)
      time.sleep(0.2)

    #only needed when adjusting values
    if read_LCD_buttons() == btnRIGHT:
      selected.incrementValue(1)
      currentMenu.scrollMenu.update(cameraAnglesFile)
      time.sleep(0.2)

    if read_LCD_buttons() == btnSELECT:
      optionsMenuFlag = True
      optionSelectedFlag = False
      options.setSelectorIcon("<")
      options.setSelector(0)
      time.sleep(0.2)
      continue

    currentMenu.display(True)

    
