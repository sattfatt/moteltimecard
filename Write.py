#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import TimeCardSystem as tc

from mfrc522 import SimpleMFRC522
def write_fob():
    reader = SimpleMFRC522()

    pin1 = -1

    isReplaced = False

    try:
        while(True):
            #text = input('New Data: ')
            #text = tc.screen.input_lcd("New Data:")
            text = tc.screen.input_lcd_text("Name:")
            text = ''.join(text.split())
            #pin1 = input('New Pin: ')
            pin1 = tc.screen.input_lcd("New Pin:")
            #pin2 = input('Enter again: ')
            pin2 = tc.screen.input_lcd("Enter again:")
            if(pin1 == pin2):
                break
            else:
                print("pins do not match, please try again")

        print("Now place your key next to reader")
        tc.screen.lcd.lcd_clear()
        tc.screen.print_lcd("Place Key", 1)
        ID, name = reader.read()

        f = open(tc.IDPATH, "r")
        data = f.read();
        f.close()
        data = data.split("\n")
        # check if the ID of the fob already exists in ID.txt and remove it
        for i, line in enumerate(data):
            a = line.split(":")
            if a[0] == str(ID):
                data.remove(data[i])

        while("" in data):
            data.remove("")

        data.append(str(ID) + ":" + pin1 + ":" + text)

        f = open(tc.IDPATH, "w")
        print(repr(data))
        f.write('\n'.join(data) + '\n')
        f.close()
        reader.write(text)
        print("written")
    # todo FIX.

    finally:
        GPIO.cleanup()
