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
---------------------------------
"""
# initialize reader object

reader = RFID.RFID()

# initialize the time tables dictionary

time_tables = {}

# time interval for reading
time_interval = 1

# initialize id
ID = 0

# end of day bool
isEndOfDay = False

time_between_reads = datetime.datetime.now()

def end_of_day():
    """
    at the end of the day make sure to log the dictionary and reset the
    dictionary.
    """
    fakelog()
    global time_tables
    time_tables = {}

def fakelog():
    print("fake logging.......Done")


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
        time_between_reads = datetime.datetime.now()

        # when we read we should keep note of the time between reads

        if (ID, name) in time_tables:
            time_tables[(ID, name)].append(datetime.datetime.now())

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
        time_table()


