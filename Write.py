#!/usr/bin/env python

import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

pin1 = -1

try:
    while(True):
        text = input('New Data: ')
        text = ''.join(text.split())
        pin1 = input('New Pin: ')
        pin2 = input('Enter again: ')
        if(pin1 == pin2):
            break
        else:
            print("pins do not match, please try again")

    print("Now place your tag to write")
    ID, text = reader.read()
    reader.write(text)
    print("Written")

    f = open("ID.txt", "a")
    f.write(str(ID) + ":" + pin1 + "\n")
    f.close()

finally:
    GPIO.cleanup()
