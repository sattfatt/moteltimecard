#dfadfasdf!/usr/bin/env/ python -u


# hello chinmay
import sys
import datetime
import RFID as RFID
import LCD as screen
import time
import Write as Addkey
import pickle
import queue as Q
from threading import Thread
"""
-------------TODO---------------
1.) Test the time keeping on seperate branch code ( as well as logging) See if reading from the log files from the main thread causes issues
2.) simplify any unnecessary code
---------------------------------
"""
# management ID
MANAGEMENT_ID = 90698293795

# ID path
IDPATH  = "/home/pi/Documents/Motel6/Timecardsystem/moteltimecard/ID.txt"
TTPATH  = "/home/pi/Documents/Motel6/Timecardsystem/moteltimecard/time_tables.pkl"
TTLPATH = "/home/pi/Documents/Motel6/Timecardsystem/moteltimecard/tlogs/"

NIGHTSHIFTCUTOFF = (21, 30)

# initialize reader object
reader = RFID.RFID()

# initialize the time tables dictionary

time_tables = {}

# time interval for reading
time_interval = 1
#---------------only write in time_checker----------------
# end of day bool
isEndOfDay = False
# end of night shift bool
isEndOfNight = False
#---------------------------------------------------------
checked_day = False
checked_night = False
# end of night/day value
end_of_day_val = (22, 30)
end_of_day_reset = (22,31)

end_of_night_val = (6, 30)
end_of_night_reset = (6, 31)

time_between_reads = datetime.datetime.now()

max_checks_in_day = 6

tq = Q.Queue(2)


def time_checker():
    """This function calls the detect_end_of_day and detect_end_of_night
    functions. If they flip the isEndOfDay or isEndOfNight bools, it calls the
    end_of_day or end_of_night functions. Note that this function runs on its
    own thread as a daemon. It also sends a message to the main thread via
    Queue (if we want to display a message or something)"""
    while(True):
        global isEndOfDay
        global isEndOfNight
        ct = datetime.datetime.now()
        detect_end_of_day()
        detect_end_of_night()
        if isEndOfDay:
            # here we should log day shift to a file
            tq.put("dend")
            isEndOfDay = False
            print("End of day!")
            sys.stdout.flush()
            end_of_day()
        if isEndOfNight:
            # here we log the night shift to a file
            tq.put("nend")
            isEndOfNight = False
            print("End of night!")
            sys.stdout.flush()
            end_of_night()
        time.sleep(0.001)

def end_of_day():
    """this function is run when the end of day is detected. It creats a new
    dictionary from the time_tables dictionary and saves that to the TTLPATH
    directory. Lastly, it empties out the entries in the dictionary that are
    Day shifts thus resetting those employees """

    global time_tables
    day_time_tables = {key:value for (key, value) in time_tables.items() if value[0][1] == "D"}
    curdt = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    pickle.dump(day_time_tables, open(TTLPATH + curdt + "-D.pkl", "wb"))
    temp = {key:value for (key, value) in time_tables.items() if value[0][1] != "D"}
    time_tables = temp
    for i in time_tables:
        print(i)
        sys.stdout.flush()


def end_of_night():
    """same functionality as end_of_day but for the night shift"""
    global time_tables
    night_time_tables = {key:value for (key, value) in time_tables.items() if value[0][1] == "N"}
    curdt = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    pickle.dump(night_time_tables, open(TTLPATH + curdt + "-N.pkl", "wb"))
    temp = {key:value for (key, value) in time_tables.items() if value[0][1] != "N"}
    time_tables = temp
    for i in time_tables:
        print(i)
        sys.stdout.flush()


def fakelog():
    #day_time_tables = {key:value for (key, value) in time_tables.items() if value[0][1] == "D"}
    #print(i for i in day_time_tables.items())
    print("fake logging.......Done")
    sys.stdout.flush()


def detect_end_of_day():
    """This function detects the end of the day shift"""
    ct = datetime.datetime.now()
    global end_of_day_val
    global end_of_day_reset
    global checked_day
    if ct.hour >= end_of_day_reset[0] and ct.minute >= end_of_day_reset[1] and ct.second >= 0:
        checked_day = False
        #print("checked_day reset to False")

    if ct.hour == end_of_day_val[0] and ct.minute == end_of_day_val[1] and ct.second == 0 and not checked_day:
        global isEndOfDay
        isEndOfDay = True
        checked_day = True


def detect_end_of_night():
    """This function detects the end of the night shift"""
    ct = datetime.datetime.now()
    global end_of_night_val
    global end_of_night_reset
    global checked_night
    if ct.hour >= end_of_night_reset[0] and ct.minute >= end_of_night_reset[1] and ct.second >= 0:
        checked_night = False
        #print("checked_night reset to False")

    if ct.hour == end_of_night_val[0] and ct.minute == end_of_night_val[1] and ct.second == 0 and not checked_night:
        global isEndOfNight
        isEndOfNight = True
        checked_night = True


def check_pin(ID, name):
    """this function asks for the user to enter a pin, if it matches with the
    pin on file, we return True else we return false"""
    # Pin = input("Enter Pin: ")
    Pin = screen.input_lcd("Pin " + str(name))
    if Pin == "*":
        return -1
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    txt = txt.split("\n")
    for line in txt:
        data = line.split(":")
        if str(ID) == data[0] and Pin == data[1] and name == ''.join(data[2].split()):
            return 1
    return 0


def print_time_table():
    global time_tables
    print("*************New Table***************")
    sys.stdout.flush()
    for key, val in time_tables:
        print(str(key) + " " + str(val) + ":")
        sys.stdout.flush()
        for t in time_tables[(key, val)]:
            print(str(t[0]) + t[1])
            sys.stdout.flush()
        print("------------------------------")
        sys.stdout.flush()


def time_table():
    """This function listens for an RFID signal, reads it, and adds the ID,
    data, and Time and appends it to the time_table dictionary. The dictionary
    is indexed by a tuple (ID,name) where ID is an int and name is a string.
    The values of the dict are lists of tuples where the first value is the
    in/out time and the seconds is N or D for nightshift or dayshift. We also
    pickle the dict every time a new time is logged so that on power loss we
    can resume seamlessly."""

    global time_between_reads
    global time_interval
    time_difference = datetime.datetime.now() - time_between_reads

    if time_difference.total_seconds() > time_interval:
        time_between_reads = datetime.datetime.now()
        ID, name = reader.read_fob()
        print("here")
        sys.stdout.flush()
        #ID, name = reader.read_no_block()
        if(not ID or not name):
            return

        global MANAGEMENT_ID
        if (ID == MANAGEMENT_ID):
            manager_command()
            screen.lcd.lcd_clear()
            screen.print_lcd("Place Key...", 1)
            return
        name = ''.join(name.split())
        # here we look at the pin log file and check to see if their input pin
        # matches the fob ID. This is to ensure no accidental entries. if the
        # pin is incorrect we should abort logging and saving.
        check = check_pin(ID, name)
        if check == 0:
            screen.print_lcd("Incorrect Pin!", 1)
            print("Pin Does not match ID/name")
            sys.stdout.flush()
            time.sleep(5)
            screen.lcd.lcd_clear()
            screen.print_lcd("Place Key...", 1)
            return
        elif check == -1:
            manager_command()
            screen.lcd.lcd_clear()
            screen.print_lcd("Place Key...", 1)
            return

        time_between_reads = datetime.datetime.now()

        day_night = "D"
        if datetime.datetime.now().hour >= NIGHTSHIFTCUTOFF[0] and datetime.datetime.now().minute >= \
                NIGHTSHIFTCUTOFF[1]:
            day_night = "N"
        # this means if someone checks in/out we are in the night shift
        else:
            day_night = "D"

        if (ID, name) in time_tables:
            if len(time_tables[(ID, name)]) < 6:
                time_tables[(ID, name)].append((datetime.datetime.now(), day_night))
                # also log to excel file
                fakelog()
                save_time_table()
            else:
                screen.print_lcd("Checked in/out", 1)
                screen.print_lcd("6 times!", 2)
                time.sleep(5)
                print("max check in/out times reached for " + name + " today!")
                sys.stdout.flush()
                screen.lcd.lcd_clear()
                screen.print_lcd("Place Key...", 1)
                return

        else:
            time_tables[(ID, name)] = []
            time_tables[(ID, name)].append((datetime.datetime.now(), day_night))
            # also log to excel file
            fakelog()
            save_time_table()
        # printing to the console
        io = ["In", "Out"]
        print_time_table()
        screen.print_lcd(
            name , 1)
        screen.print_lcd(str(datetime.datetime.now().strftime("%H:%M") + " " + day_night + " " + io[(len(time_tables[(ID, name)]) - 1) % 2] + " " + str(len(time_tables[(ID, name)]))), 2)

        time.sleep(5)
        screen.lcd.lcd_clear()
        screen.print_lcd("Place Key...", 1)
        return

# program start

# management functions
def manager_command():
    """This function displays a menu on the LCD and based on the selection
    calls a management function."""
    # command = screen.input_lcd("Enter cmd (1-4):")
    commands = ["Display-Times", "Add-Employee", "Remove-Employee", "Clear-Time Data", "Clear-Employee Data",
                "Change-Pin"]
    selected = screen.input_select_command_list(commands)
    if selected == commands[3]:
        confirm = screen.input_lcd("Clear? . cancel")
        if confirm == "":
            clear_time_data()
    elif selected == commands[4]:
        confirm = screen.input_lcd("Clear? . cancel")
        if confirm == "":
            clear_employee_table()
    elif selected == commands[1]:
        confirm = screen.input_lcd("add? . cancel")
        if confirm == "":
            add_employee()
    elif selected == commands[2]:
        confirm = screen.input_lcd("Remove? . cancel")
        if confirm == "":
            remove_employee()
    elif selected == commands[5]:
        confirm = screen.input_lcd("Change? . cancel")
        if confirm == "":
            change_pin()
    elif selected == commands[0]:
        confirm = screen.input_lcd("Display? . cancel")
        if confirm == "":
            display_times()


def clear_time_data():
    """This function clears the time table dictionary for a fresh start"""
    global time_tables
    time_tables = {}
    save_time_table()
    print("data cleared!")
    sys.stdout.flush()
    screen.print_lcd("Cleared!", 1)
    time.sleep(2)


def clear_employee_table():
    """This function clears the ID.txt file which contains all the emplyees
    with their pins"""
    f = open(IDPATH, "w")
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
    # identifier = screen.input_lcd_text("Employee: ")
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    data = txt.split("\n")
    employees = []
    for line in data:
        e = line.split(":")
        if len(e) == 3:
            employees.append(e[2])
    identifier = screen.input_select_command_list(employees)
    for line in data:
        e = line.split(":")
        for item in e:
            if item == str(identifier):
                data.remove(line)
                screen.print_lcd("Removed!", 1)
                time.sleep(2)
    newdata = [i for i in data if i]
    f = open(IDPATH, "w")
    f.write("\n".join(newdata) + "\n")
    f.close()


def display_times():
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    data = txt.split("\n")
    employees = []
    ids = {}
    for line in data:
        e = line.split(":")
        if len(e) == 3:
            employees.append(e[2])
            ids[e[2]] = e[0]
    name = screen.input_select_command_list(employees)
    print(time_tables)
    sys.stdout.flush()
    try:
        shift = time_tables[(int(ids[name]), name)][0][1]
        io = ["In", "Out"]
        timelist = time_tables[(int(ids[name]), name)]
        timelist = [str(i[0].strftime("%H:%M:%S")) for i in timelist]
        timelist = [i + " " + str(io[ind % 2] + " " + str(ind + 1) + " " +shift) for ind, i in enumerate(timelist)]
        screen.input_select_command_list(timelist)
    except:
        screen.print_lcd("Error!", 1)
        screen.print_lcd("No Data", 2)
        time.sleep(2)


def change_pin():
    f = open(IDPATH, "r")
    txt = f.read()
    f.close()
    data = txt.split("\n")
    newpin = ""
    employees = []
    for line in data:
        e = line.split(":")
        if len(e) == 3:
            employees.append(e[2])
    print(employees)
    sys.stdout.flush()
    name = screen.input_select_command_list(employees)
    # name = screen.input_lcd_text("Name:")
    while (True):
        newpin = screen.input_lcd("New Pin:")
        newpin2 = screen.input_lcd("Enter Again:")
        if newpin == newpin2:
            break
        else:
            screen.lcd.lcd_clear()
            screen.print_lcd("No Match", 1)
            screen.print_lcd("Try Again", 2)
            time.sleep(2)
    for line in data:
        e = line.split(":")
        if len(e) == 3:
            if name == e[2]:
                e[1] = newpin
                data.remove(line)
                newline = ":".join(e)
                data.append(newline)
                newdata = [i for i in data if i]
                print(newdata)
                sys.stdout.flush()
                f = open(IDPATH, "w")
                f.write("\n".join(newdata) + "\n")
                f.close()
                screen.lcd.lcd_clear()
                screen.print_lcd("Pin Changed!", 1)
                time.sleep(2)
                return
    screen.lcd.lcd_clear()
    screen.print_lcd("Does Not", 1)
    screen.print_lcd("Exist!", 2)
    time.sleep(2)

#------END OF Management Functions----------------------
def save_time_table():
    cur_time = datetime.datetime.now()
    global time_tables
    pickle.dump(time_tables, open(TTPATH, "wb"))


def load_time_table():
    return pickle.load(open(TTPATH, "rb"))


if __name__ == "__main__":
    # start the time keeper thread
    time_check_thread = Thread(target=time_checker)
    time_check_thread.daemon = True
    time_check_thread.start()
    try:
        time_tables = load_time_table()
    except:
        print("failed to open " + TTPATH)
        sys.stdout.flush()
    screen.lcd.lcd_clear()
    screen.print_lcd("Place Key...", 1)
    while (True):
        # handling the messages from the time checker thread.
        #while(not tq.empty()):
        #    msg = tq.get()
        #    if msg == "dend":
        #        print("End of the Day shift reached!")
        #    elif msg == "nend":
        #        print("End of the Night shift reached!")

        time_table()
        time.sleep(0.0001)
