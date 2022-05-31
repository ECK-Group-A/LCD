import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
from Printbox import *
lcd = rgb1602.RGB1602(16,2)

class Menu:
  def __init__(self):
    self.printBoxes = []

  def addPrintbox(self, pb):
    self.printBoxes.append(pb)

  def display(self):
    for pb in self.printBoxes:
      pb.display()


