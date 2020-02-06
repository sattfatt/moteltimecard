#!/usr/bin/env/ python 

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


class RFID(SimpleMFRC522):
    def __init__(self):
        super().__init__()


    def read_fob(self):
        try:
            id, text = self.read()
            #print("ID: " + str(id))
            #print("Name: " + text)
            return id, text
        finally:
            GPIO.cleanup()

    def write_fob(self):
        try:
            # here we should have a visual indication that we want an input for name 
            text = input('Name: ')
            print("Place tag to write...")
            # here have another visual indication for placing the tag
            self.write(text)
            # here have a final visual indicator that the fob was written to
            print("Write successful")
        finally:
            GPIO.cleanup()
