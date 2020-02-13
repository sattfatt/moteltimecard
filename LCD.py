import lcddriver
import termios, fcntl, sys, os
# initialize lcd Driver
lcd = lcddriver.lcd()
lcd.lcd_clear()

def print_lcd(string, line):
    if(len(string) <= 16):
        lcd.lcd_clear()
        lcd.lcd_display_string(string, line)

def input_lcd(string):
    lcd.lcd_clear()
    lcd.lcd_display_string(string, 1)

    while(True):
        input_char = get_char_keyboard()
        print(input_char)
        if (input_char == "-"):
            break
        lcd.lcd_display_string(input_char, 2)

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

    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return c
