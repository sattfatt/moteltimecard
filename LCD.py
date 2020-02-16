import lcddriver
import termios, fcntl, sys, os
import readchar as rc
# initialize lcd Driver
lcd = lcddriver.lcd()
lcd.lcd_clear()
character_list = ['a','b','c','d','e','f','g','h', 'i', 'j', 'k', 'l', 'm','n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def print_lcd(string, line):
    if(len(string) <= 16):
        lcd.lcd_display_string(string, line)

def input_lcd(string):
    lcd.lcd_clear()
    lcd.lcd_display_string(string, 1)
    input_char = []
    while(True):
        c = rc.readchar()
#        print(repr(c))
       # c = get_char_keyboard()
        if (c == '\x7f'):
            if len(input_char) > 0:
                input_char.pop()
            lcd.lcd_display_string("                ",2)
            lcd.lcd_display_string(input_char, 2)
        elif (c == '\n' or c == '\r'):
            break
        else:
            input_char.append(c)
            lcd.lcd_display_string("                ",2)
            lcd.lcd_display_string(input_char, 2)
            #print(input_char)
    lcd.lcd_clear()
    return ''.join(input_char)

def input_lcd_text(string):
    lcd.lcd_clear()
    lcd.lcd_display_string(string, 1)
    index = 0
    input_array = ['a']
    while(True):
        c = rc.readchar()
        if c == "8":
            if index < len(character_list) - 1:
                index = index + 1
            input_array[-1] = character_list[index]
            lcd.lcd_display_string("                ", 2)
            lcd.lcd_display_string(input_array, 2)
        elif c == "2":
            if index > 0:
                index = index - 1
            input_array[-1] = character_list[index]
            lcd.lcd_display_string("                ", 2)
            lcd.lcd_display_string(input_array, 2)
        elif c == "6":
            index = 0
            input_array.append(character_list[index])
            lcd.lcd_display_string("                ", 2)
            lcd.lcd_display_string(input_array, 2)
        elif c == '\x7f':
            if len(input_array) > 1:
                input_array.pop()
            lcd.lcd_display_string("                ", 2)
            lcd.lcd_display_string(input_array, 2)
        elif c == "\n" or c == "\r":
            lcd.lcd_clear()
            return ''.join(input_array)


def get_char_keyboard():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    c = None
    try:
        c = sys.stdin.read(1)
    except IOError: pass

    termios.tcsetattr(fd, termios.TCSADRAIN, oldterm)
    return c
