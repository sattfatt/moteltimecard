#!/usr/bin/env/ python
# hello chinmay
import datetime
import RFID as RFID
import LCD as screen
import time
import Write as Addkey
import pickle

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
TTPATH = "/home/pi/Documents/Motel6/Timecardsystem/moteltimecard/time_tables.pkl"

NIGHTSHIFTCUTOFF = (21, 30)

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
end_of_day_val = (23, 59)

end_of_night_val = (5, 59)

time_between_reads = datetime.datetime.now()

max_checks_in_day = 6


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
    for key, val in time_tables:
        print(str(key) + " " + str(val) + ":")
        for t in time_tables[(key, val)]:
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
        if (ID == MANAGEMENT_ID):
            manager_command()
            return
        name = ''.join(name.split())
        # here we look at the pin log file and check to see if their input pin
        # matches the fob ID. This is to ensure no accidental entries. if the
        # pin is incorrect we should abort logging and saving.
        check = check_pin(ID, name)
        if check == 0:
            screen.print_lcd("Incorrect Pin!", 1)
            print("Pin Does not match ID/name")
            time.sleep(5)
            return
        elif check == -1:
            manager_command()
            return

        time_between_reads = datetime.datetime.now()

        day_night = "D"
        if datetime.datetime.now().time().hour > NIGHTSHIFTCUTOFF[0] and datetime.datetime.now().hour > \
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
            name + " " + io[(len(time_tables[(ID, name)]) - 1) % 2] + " " + str(len(time_tables[(ID, name)])), 1)
        screen.print_lcd(str(datetime.datetime.now().strftime("%H:%M")), 2)

        time.sleep(5)


# program start

# management functions
def manager_command():
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
    try:
        io = ["In", "Out"]
        timelist = time_tables[(int(ids[name]), name)]
        timelist = [str(i[0].strftime("%H:%M:%S")) for i in timelist]
        timelist = [i[0] + " " + str(io[ind % 2] + " " + str(ind + 1)) for ind, i in enumerate(timelist)]
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


def save_time_table():
    cur_time = datetime.datetime.now()
    global time_tables
    pickle.dump(time_tables, open(TTPATH, "wb"))


def load_time_table():
    return pickle.load(open(TTPATH, "rb"))


if __name__ == "__main__":

    while (True):
        screen.lcd.lcd_clear()
        screen.print_lcd("Place Key...", 1)
        detect_end_of_day()
        detect_end_of_night()
        if (isEndOfDay):
            # end_of_day()
            print("End of day shift reached!")
            isEndOfDay = False
        if (isEndOfNight):
            # end_of_night()
            print("End of night shift reached!")
            isEndOfNight = False
        try:
            time_tables = load_time_table()
        except:
            print("failed to open " + TTPATH)
            pass
        time_table()
