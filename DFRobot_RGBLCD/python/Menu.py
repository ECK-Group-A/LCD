import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
import subprocess
from Printbox import *

lcd = rgb1602.RGB1602(16,2)

def isNaN(num):
    return num!= num

class Menu:
  def __init__(self, ):
    self.printBoxes = []
    self.scrollMenu = ScrollMenu()

  def addPrintbox(self, pb):
    self.printBoxes.append(pb)

  def display(self, optionsFlag):
    if optionsFlag == True:
      self.scrollMenu.display()
    else:
      for pb in self.printBoxes:
        pb.display()

  def setScrollMenu(self, ScrollMenu):
    self.scrollMenu = ScrollMenu

  def getScrollMenu(self):
    return self.scrollMenu

class Option:
  def __init__(self, name, value = float("NaN"), increment = float("NaN"), uplim = float("NaN"), lowlim = float("NaN"), length = 3):
    self.name = name
    self.tempName = name
    self.commands = []

    if not isNaN(value):
      self.value = value
      self.length = length
      self.increment = increment
      self.uplim = uplim
      self.lowlim = lowlim
      self.valueBox = Printbox(0, 0, length-1)
      self.incrementValue(0)

  def incrementValue(self, increment):
    self.value = self.value + increment
    if self.value > self.uplim:
      self.value = self.lowlim

    if self.value < self.lowlim:
      self.value = self.uplim

    self.valueBox.setMessage(str(self.value))
    empty = "               "
    spaceLeft = 15-len(self.tempName)-self.length
    if spaceLeft < 0:
      print("Not enough space between value and option name")
    else:
      self.name = self.tempName + empty[0:spaceLeft] + self.valueBox.getMessage() 

  def getValue(self):
    if hasattr(self, 'value'):
      return self.value

  def addCommand(self, command):
    self.commands.append(command)

  def execute(self):
    if len(self.commands) == 0:
      return False
    for command in self.commands:
      try:
        subprocess.run(command, shell=True, check=True)
      except subprocess.CalledProcessError:
        pass
    return True
    
class ScrollMenu(Menu):
  def __init__(self):
    self.l1 = Printbox(0, 0, 14)
    self.l2 = Printbox(1, 0, 15)
    self.index = 0
    self.selectorLine = 0
    self.selector = Printbox(0 , 15, 15)
    self.selectorIcon = "<"
    self.selector.setMessage(self.selectorIcon)
    self.options = [Option(" ")]

  def addOptions(self, option):
    self.options.insert(0, option)

  def select(self):
    return self.options[self.index + self.selectorLine]

  def setSelectorIcon(self, char):
    self.selectorIcon = char

  def setSelector(self, increment):
    #user wants to scroll down
    if increment > 0:
      #change index because cursor is at bottom
      if self.selectorLine == 1 and not len(self.options)-2 == self.index + self.selectorLine and len(self.options) > 1:
        self.index = self.index + increment
      #change cursor cause cursor is at top
      elif self.selectorLine == 0:
        self.selectorLine = 1
    
    #user wants to scroll up
    if increment < 0:
      #change cursor cause cursor is at bottom
      if self.selectorLine == 1:
        self.selectorLine = 0
      #change index cause cursor is already at top
      elif self.selectorLine == 0:
        self.index = self.index + increment

    #limit visual top bound
    if self.index < 0:
      self.index = 0

    #limit visual bottom bound
    if self.index > len(self.options)-2:
      self.index = len(self.options)-2
    
    self.selector.setMessage(" ")
    self.selector.display()
    self.selector.setMessage(self.selectorIcon)
    self.selector.setLine(self.selectorLine)
    self.l1.setMessage(self.options[self.index].name)
    self.l2.setMessage(self.options[self.index+1].name)

  def update(self, fileName):
    self.l1.setMessage(self.options[self.index].name)
    self.l2.setMessage(self.options[self.index+1].name) 

    values = []
    count = 1
    for option in self.options:
      value = option.getValue()
      if count < 7 and not isNaN(value) and not value == None:
        values.append("C" + str(count) + "=" + str(value) + '\n')
        count+=1

    with open(fileName,"w") as file:
      file.writelines(values)

    file.close()

  def display(self):
    self.l1.display()
    self.l2.display()
    self.selector.display()
