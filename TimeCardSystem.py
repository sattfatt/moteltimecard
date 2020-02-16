#!/usr/bin/env/ python
# hello chinmay
import datetime
import RFID as RFID
import LCD as screen
import time
import Write as Addkey
"""
-------------NOTES---------------
1.) By default we should be reading (done)
2.) if certain criteria is met, we call the write function
3.) We need to keep track of the date and time for each read. (done)
4.) each read has to have a gap of 5 min or so between reads (pretty much done)
5.) at the end of the day the table of times has to be logged to a file with the date
6.) for the night shift we need to log the times differently (we could shift
the times back by 12 hours.
7.) we only log the 6am-2pm and 2pm-10pm shifts when end of day is triggered
8.) we log the 10pm-6am at 6 (night shift)
---------------------------------
"""
# management ID
MANAGEMENT_ID = 90698293795

# ID path
IDPATH = "/home/pi/Documents/Motel6/Timecardsystem/moteltimecard/ID.txt"

# initialize reader object
reader = RFID.RFID()

# initialize the time tables dictionary

time_tables = {}

# time interval for reading
time_interval = 1

# end of day bool
isEndOfDay = False
# end of night shift bool
isEndOfNight = False

# end of day value
end_of_day_val = (23,59)

end_of_night_val = (5,59)

time_between_reads = datetime.datetime.now()

max_checks_in_day = 6

time_tables = {}

def end_of_day():
    """at the end of the night shift  make sure to log the dictionary and reset the
    night shift dictionary entries."""
    fakelog()
    global time_tables
    time_tables = {}

def fakelog():
    print("fake logging.......Done")

def detect_end_of_day():
    """This function detects the end of the day shift"""
    current_time = datetime.datetime.now()
    if current_time.time().hour == end_of_day_val[0] and current_time.time().minute == end_of_day_val[1]:
        global isEndOfDay
        isEndOfDay = True

def detect_end_of_night():
    """This function detects the end of the night shift"""
    current_time = datetime.datetime.now()
    if current_time.time().hour == end_of_night_val[0] and current_time.time().minute == end_of_night_val[1]:
        global isEndOfNight
        isEndOfNight = True

def check_pin(ID, name):
    """this function asks for the user to enter a pin, if it matches with the
    pin on file, we return True else we return false"""
    #Pin = input("Enter Pin: ")
    Pin = screen.input_lcd("Pin:")
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    txt = txt.split("\n")
    for line in txt:
        data = line.split(":")
        if str(ID) == data[0] and Pin == data[1] and name == ''.join(data[2].split()):
            return True
    return False

def print_time_table():
    global time_tables
    print("*************New Table***************")
    for key, val in time_tables:
        print(str(key) + " " +  str(val) + ":")
        for t in time_tables[(key,val)]:
            print(str(t))
        print("------------------------------")

def time_table():

    """This function listens for an RFID signal, reads it, and adds the ID,
    data, and Time and appends it to the time_table dictionary. The dictionary
    is indexed by a tuple (ID,name) where ID is an int and name is a string"""

    global time_between_reads

    time_difference = datetime.datetime.now() - time_between_reads

    if time_difference.total_seconds() > time_interval:
        # this should block until something is read.
        ID, name = reader.read_fob()
        global MANAGEMENT_ID
        if(ID == MANAGEMENT_ID):
            manager_command()
            return
        name = ''.join(name.split())
        # here we look at the pin log file and check to see if their input pin
        # matches the fob ID. This is to ensure no accidental entries. if the
        # pin is incorrect we should abort logging and saving.
        if check_pin(ID, name) == False:
            screen.print_lcd("Incorrect Pin!", 1)
            print("Pin Does not match ID/name")
            time.sleep(5)
            return

        time_between_reads = datetime.datetime.now()

        # when we read we should keep note of the time between reads

        if (ID, name) in time_tables:
            if len(time_tables[(ID, name)]) < 6:
                time_tables[(ID, name)].append(datetime.datetime.now())
                # also log to excel file
                fakelog()
            else:
                screen.print_lcd("Checked in/out", 1)
                screen.print_lcd("6 times!", 2)
                time.sleep(5)
                print("max check in/out times reached for " + name + " today!")
                return

        else:
            time_tables[(ID, name)] = []
            time_tables[(ID, name)].append(datetime.datetime.now())
            # also log to excel file
            fakelog()
        # printing to the console
        print_time_table()
        screen.print_lcd(name, 1)
        screen.print_lcd(str(datetime.datetime.now().strftime("%H:%M")), 2)

        time.sleep(5)
# program start

# management functions
def manager_command():
    command = screen.input_lcd("Enter cmd (1-4):")

    if command == "1":
        confirm = screen.input_lcd("Clear? . cancel")
        if confirm == "":
            clear_time_data()
    elif command == "2":
        confirm = screen.input_lcd("Clear? . cancel")
        if confirm == "":
            clear_employee_table()
    elif command == "3":
        confirm = screen.input_lcd("add? . cancel")
        if confirm == "":
            add_employee()
    elif command == "4":
        confirm = screen.input_lcd("Remove? . cancel")
        if confirm == "":
            remove_employee()
    else:
        pass

def clear_time_data():
    """This function clears the time table dictionary for a fresh start"""
    global time_tables
    time_tables = {}
    print("data cleared!")
    screen.print_lcd("Cleared!", 1)
    time.sleep(2)

def clear_employee_table():
    """This function clears the ID.txt file which contains all the emplyees
    with their pins"""
    f = open(IDPATH,"w")
    f.write("")
    f.close()
    screen.print_lcd("Cleared", 1)
    screen.print_lcd("Employees", 2)
    time.sleep(2)

def add_employee():
    """This function allows for adding an employee to ID.txt"""
    Addkey.write_fob()
    screen.print_lcd("Added!", 1)
    time.sleep(2)

def remove_employee():
    identifier = screen.input_lcd_text("Employee: ")
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    data = txt.split("\n")
    for line in data:
        e = line.split(":")
        for item in e:
            if item == str(identifier):
                data.remove(line)
                screen.print_lcd("Removed!",1)
                time.sleep(2)
    f = open(IDPATH, "w")
    f.write("\n".join(data) + "\n")
    f.close()


if __name__ == "__main__":

    while(True):
        screen.lcd.lcd_clear()
        screen.print_lcd("Place Key...", 1)
        detect_end_of_day()
        detect_end_of_night()

        if(isEndOfDay):
            end_of_day()
            print("End of day shift reached!")
            isEndOfDay = False
        if(isEndOfNight):
            end_of_night()
            print("End of night shift reached!")
            isEndOfNight = False
        time_table()
