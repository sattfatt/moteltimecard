#!/usr/bin/env/ python
# hello chinmay
import datetime
import RFID as RFID

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

def end_of_day():
    """at the end of the day make sure to log the dictionary and reset the
    day shift dictionary entries."""
    fakelog()
    global time_tables
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

def check_pin(ID):
    """this function asks for the user to enter a pin, if it matches with the
    pin on file, we return True else we return false"""
    Pin = input("Enter Pin: ")
    f = open("ID.txt", "r")
    txt = f.read()
    f.close()
    txt = txt.split("\n")
    for line in txt:
        data = line.split(":")
        if ID == data[0] and Pin == data[1]:
            return True
    return False


def time_table():

    """This function listens for an RFID signal, reads it, and adds the ID,
    data, and Time and appends it to the time_table dictionary. The dictionary
    is indexed by a tuple (ID,name) where ID is an int and name is a string"""

    global time_between_reads

    time_difference = datetime.datetime.now() - time_between_reads

    if time_difference.total_seconds() > time_interval:
        # this should block until something is read.
        ID, name = reader.read_fob()
        name = ''.join(name.split())
        # here we look at the pin log file and check to see if their input pin
        # matches the fob ID. This is to ensure no accidental entries. if the
        # pin is incorrect we should abort logging and saving.
        if check_pin(ID) == False:
            return

        time_between_reads = datetime.datetime.now()

        # when we read we should keep note of the time between reads

        if (ID, name) in time_tables:
            if len(time_tables[(ID, name)]) < 6:
                time_tables[(ID, name)].append(datetime.datetime.now())
            else:
                print("max check in/out times reached for " + name + " today!")
                return

        else:
            time_tables[(ID, name)] = []
            time_tables[(ID, name)].append(datetime.datetime.now())

        # printing to the console
        print("*************New Table***************")
        for key, val in time_tables:
            print(str(key) + " " +  str(val) + ":")
            for t in time_tables[(key,val)]:
                print(str(t))
            print("------------------------------")

# program start

if __name__ == "__main__":

    while(True):

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
        else:
            time_table()


