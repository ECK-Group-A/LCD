import sys
sys.path.append('.')
import RPi.GPIO as GPIO
import rgb1602
lcd = rgb1602.RGB1602(16,2)

#custom symbol
filledSelector = [
  0b00010,
  0b00110,
  0b01110,
  0b11110,
  0b01110,
  0b00110,
  0b00010,
  0b00000
]
lcd.customSymbol(0, filledSelector)

#replaces unneeded characters with custom ones
charDict = {
  "*": 0
}

class Printbox:
    def __init__(self, line, begin, end):
        if begin > 15 or end > 15:
            print("box out of bounds")
            return
        if begin < 0 or end < 0:
            print("box out of bounds")
            return
        if line < 0 or line > 1:
            print("line index can only be 0 or 1")
            return
        self.line = line
        self.begin = begin
        self.end = end
        self.message = ""
        self.empty = "                "

    def setMessage(self, message):
        if not isinstance(self.message, str):
            print("message not a string")
            return
        self.message = message + self.empty

    def setLine(self, line):
        self.line = line

    def getLine(self):
        return self.line

    def getMessage(self):
        return self.message[0:self.end+1]

    def display(self): 
        strings = []
        message = self.message[0:self.end+1]
        lcd.setCursor(self.begin, self.line)
        for key, val in charDict.items():
            if message.find(key)!=-1:
                strings = self.message[0:self.end+1].split(key)
                lcd.printout(strings[0])
                lcd.write(val)
                lcd.printout(strings[1])
            else:
                lcd.printout(message)

        