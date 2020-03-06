# Description

This is a basic time card service that runs on a raspberry pi using python. 
The hardware is a cheap RFID reader, a lcd 16 digit screen, and a number pad.

# Operation

## Day/Night shift detection

Day/Night is detected by checking if the first check in time is before 9:30 pm (21:30).

## Automatic functions

At 10:30 the day shift entries are logged and cleared to tlogs folder.
At 6:30 the night shift entried are logged and cleared.

