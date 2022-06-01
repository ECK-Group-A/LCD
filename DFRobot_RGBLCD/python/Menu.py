import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
from Printbox import *
lcd = rgb1602.RGB1602(16,2)


class Menu:
  def __init__(self):
    self.printBoxes = []
    self.optionsMenu = Option("")

  def addPrintbox(self, pb):
    self.printBoxes.append(pb)

  def display(self, optionsFlag):
    if optionsFlag == True:
      self.optionsMenu.display()
    else:
      for pb in self.printBoxes:
        pb.display()

  def setOptionsMenu(self, ScrollMenu):
    self.optionsMenu = ScrollMenu

  def getOptionsMenu(self):
    return self.optionsMenu

class Option:
  def __init__(self, name):
    self.name = name
    self.commands = []

  def addCommand(self, command):
    commands.append(command)

  def execute(self):
    for command in self.commands:
      try:
        subprocess.run(command, shell=True, check=True)
      except subprocess.CalledProcessError:
        pass

class ScrollMenu:
  def __init__(self):
    self.l1 = Printbox(0, 0, 14)
    self.l2 = Printbox(1, 0, 15)
    self.selector = Printbox(0 , 15, 15)
    self.selector.setMessage("<")
    self.options = [Option(" ")]
    self.index = 0
 
  def addOptions(self, option):
    self.options.insert(0, option)

  def setSelector(self, increment):
    self.index = self.index + increment
    if self.index < 0:
      self.index = 0
    if self.index > len(self.options)-2:
      self.index = len(self.options)-2
    self.l1.setMessage(self.options[self.index].name)
    self.l2.setMessage(self.options[self.index+1].name)
    print("items: " + str(len(self.options)) + " index: " + str(self.index))

  def display(self):
    self.l1.display()
    self.l2.display()
    self.selector.display()