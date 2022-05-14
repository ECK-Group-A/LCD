import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
import time
lcd = rgb1602.RGB1602(16,2)

class Menu:
  def __init__(self, name, state):
    self.name = name
    self.state = state

  def display(self):
    if len(self.name) <= 16:    #print menu name
        lcd.setCursor(0,0)
        lcd.printout(self.name)
    if self.state == 0:
        lcd.setCursor(0,1)
        lcd.printout("Failed!")
        lcd.setRGB(255,0,0)
    if self.state == 1:
        lcd.setCursor(0,1)
        lcd.printout("Running!")
        lcd.setRGB(0,255,0)
