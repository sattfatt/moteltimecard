import lcddriver
import termios, fcntl, sys, os
import readchar as rc
# initialize lcd Driver
lcd = lcddriver.lcd()
lcd.lcd_clear()

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
