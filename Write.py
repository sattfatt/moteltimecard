#!/usr/bin/env python

import RPi.GPIO as GPIO

from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

pin1 = -1

isReplaced = False

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

    print("Now place your key next to reader")

    ID, name = reader.read()

    f = open("ID.txt", "r")
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

    f = open("ID.txt", "w")
    print(repr(data))
    f.write('\n'.join(data) + '\n')
    f.close()
    reader.write(text)
    print("written")

# todo FIX.

finally:
    GPIO.cleanup()
