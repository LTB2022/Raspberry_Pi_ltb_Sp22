 # Integrated_SM_Revx
# rev x contains the Raspberry Pi 4 python code state machine, RTC, SD card wrtiting
# and output to the m4express that controls the epaper screen

# pylint: disable=global-statement,stop-iteration-return,no-self-use,useless-super-delegation

import time as t
import csv
import serial
import gpiozero
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.relativedelta import relativedelta
#import pytz                     #Olson time zone (tz) database


###############################################################################

# Set to false to disable testing/tracing code
TESTING = False

################################################################################
# Setup hardware

# Input Pins
switch_1 = gpiozero.Button(5, pull_up=True)
switch_2 = gpiozero.Button(6, pull_up=True)

# Output Pins
home_scrn = gpiozero.DigitalOutputDevice(17,active_high=True, initial_value=False)
profile1_scrn = gpiozero.DigitalOutputDevice(27, active_high=True, initial_value=False)
track1_scrn = gpiozero.DigitalOutputDevice(22, active_high=True, initial_value=False)
focus1_scrn = gpiozero.DigitalOutputDevice(23, active_high=True, initial_value=False)
profile2_scrn = gpiozero.DigitalOutputDevice(25, active_high=True, initial_value=False)
voicenote_scrn = gpiozero.DigitalOutputDevice(13, active_high=True, initial_value=False)
record_scrn = gpiozero.DigitalOutputDevice(19, active_high=True, initial_value=False)

#################################################################################################
# Setting up the Real Time Clock and set the initial time

# Creates object I2C that connects the I2C module to pins SCL and SDA
#myI2C = busio.I2C(board.SCL, board.SDA)
# Creates an object that can access the RTC and communicate that information along using I2C.
#rtc = adafruit_pcf8523.PCF8523(myI2C)

if True:   # change to True if you want to write the time!
# Note this code is in a loop and will continue to use this statement
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    #   t is a time object
    #t = time.struct_time((2022,  4,   18,   11,  22,  0,    0,   -1,    -1))
    t = time.localtime()    #Use the actual time set in the Pi
    print("Setting time to:", t)     # uncomment for debugging
    #rtc.datetime = t
    #print()

################################################################################
#Python Time functions
now = datetime.now().time() # the datetime library method of displaying the current time vs time library
print("now =", now)
print('\n')

################################################################################
# Creates a file and writes name inside a text file along the path.
#with open("/home/pi/Desktop/Python_ltb/stamp.csv", "a") as f:
    #f.write("Date, Time In, Time Out , Total, Voice Note\r\n")
#print("Logging column names into the filesystem\n")

################################################################################
# Support functions

# Code tracing feature located in the "pressed" method of the "StateMachine" Class
def log(s):
    """Print the argument if testing/tracing is enabled."""
    if TESTING:
        print(s)


################################################################################
# State Machine, Manages states

class StateMachine(object):

    def __init__(self):                             # Needed constructor
        self.state = None
        self.states = {}


    def add_state(self, state):                     # "add state" attribute, adds states to the machine
        self.states[state.name] = state

    def go_to_state(self, state_name):              # "go to state" attribute, facilittes transition to other states. Prints confirmation when "Testing = True"
        if self.state:
            log('Exiting %s\n' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.enter(self)

    def pressed(self):                              # "button pressed" attribute. Accessed at the end of each loop, applies a pause and prints confirmaiton if setup.
        if self.state:
            log('Updating %s' % (self.state.name))
            self.state.pressed(self)
            #print("'StateMachine' Class occurrence")  # Use this print statement to understand how the states transition here to update the state in the serial monitor
            t.sleep(.50)                             # Critial pause needed to prevent the serial monitor from being "flooded" with data and crashing



################################################################################
# States

# Abstract parent state class: I'm not 100% sure that this state is the "parent class" for the states below.
# So far "StateMachine" appears to be the parent class, some clarification is needed to indentify how a class is called by "super().__init__()" (aka "Inheritance")

class State(object):


    def __init__(self):         # Constructor. Sets variables for the class, in this instance only, "self". Note machine variable below in the "enter" attribute

        @property
        def name(self):             # Attribute. Only the name is returned in states below. The State object shouldn't be called and returns nothing
            return ''

    def enter(self, machine):   # Class Attribute. Does what is commanded when the state is entered
        pass

    def exit(self, machine):    # Class Attribute. Does what is commanded when exiting the state
        pass

    def pressed(self, machine): # Class Attribute. Does what is commanded when a button is pressed
        print("'State' Class occurrence")   #This hasn't been called yet, I used this as a test to investigate the "inheritance" of child classes below.

########################################
# This state is active when powered on and other states return here
class Home(State):

    def __init__(self):
        super().__init__()          # Child class inheritance

    @property
    def name(self):
        return 'Home'

    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        home_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Home State ####')
        print('Placeholder to display date and time\n')

    def exit(self, machine):

        State.exit(self, machine)
        home_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:                                         #
            machine.go_to_state('Profile 1')
        if switch_2.is_pressed:
            machine.go_to_state('Profile 2')


########################################
# The "Profile 1" state. Either choose to track a task or use a focus timer.
class Profile1(State):

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile 1'

    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        profile1_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Profile 1 State ####')
        print('Placeholder to display date and time\n')

    def exit(self, machine):

        State.exit(self, machine)
        profile1_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Tracking1')
        if switch_2.is_pressed:
            machine.go_to_state('Focus Timer 1')

########################################
# The "Tracking 1" state. Begin tracking task 1 in this state
class Tracking1(State):

    #Declare global variables for Tracking1 State
    global month_in, day_in, year
    global hour_in, min_in, sec_in
    global hour_out, min_out, sec_out

    # Intitalize the global variables within "Tracking1"
    month_in = 0
    day_in = 0
    year_in = 0

    hour_in = 0
    min_in = 0
    sec_in = 0

    hour_out = 0
    min_out = 0
    sec_out = 0


    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Tracking1'

    def enter(self, machine):

        time_in = datetime.now()
        global month_in, day_in, year_in
        global hour_in, min_in, sec_in
        global hour_out, min_out, sec_out


        State.enter(self, machine)

        # Components of the "time in" stamp
        month_in = time(now.month)
        day_in = date(now.day)
        year_in = t.tm_year

        hour_in = t.tm_hour
        min_in = t.tm_min
        sec_in = t.tm_sec

        #Screen Placeholders
        track1_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Tracking Task 1 State ####')
        print('Placeholder: Display date and time')
        print('Placeholder: Display counter for tracked time')

        print('Logging a START time to .csv file\n')
         # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/Python_ltb/stamp.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("%d/%d/%d, " % (month_in, day_in, year_in)) #Prints data about to be written to the SD card
            f.write("%d/%d/%d, " % (month_in, day_in, year_in))    # Common U.S. date format

            print("%d:%02d:%02d, " % (hour_in, min_in, sec_in)) #Prints to the serial monitor the data about to be written to the SD card
            f.write("%d:%02d:%02d, " % (hour_in, min_in, sec_in))  # "Time in" written to file
            #led.value = False  # turn off LED to indicate we're done

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()


    def exit(self, machine):

        t = time.localtime()
        global month_in, day_in, year_in
        global hour_in, min_in, sec_in
        global hour_out, min_out, sec_out

        # Track the previous variables
        print('Date in: ' + str(month_in) + '/' + str(day_in) + '/' + str(year_in))
        print('Time in: ' + str(hour_in) + ':' + str(min_in) + ':' + str(sec_in))


        State.exit(self, machine)

        # Components of the "time out" stamp
        hour_out = t.tm_hour
        min_out = t.tm_min
        sec_out = t.tm_sec

        #NOTE: The likelyhood for negative data below. Correct data types when the variables function in this scope
        delta_hour = hour_out - hour_in # Calculate hour difference
        delta_min = min_out - min_in  # Calculate min difference
        delta_sec = sec_out - sec_in # Calculate sec difference

        print('Logging a STOP time to .csv\n')    #
        # appending timestamp to file, Use "a" to append file, "w" will overwrite data in the file, "r" will read lines from the file.
        with open("/home/pi/Desktop/Python_ltb/stamp.csv", "a") as f:
            #led.value = True    # turn on LED to indicate writing entries
            print("%d:%02d:%02d, " % (hour_out, min_out, sec_out)) #Prints to the serial monitor the data about to be written to the SD card
            print('\n') # Prints a blank line
            f.write("%d:%02d:%02d, " % (hour_out, min_out, sec_out))  # "Time in" written to file
            f.write("%d:%02d:%02d, " % (delta_hour, delta_min, delta_sec))  # "Time in" written to file
            f.write("'Speech to text voice note'\r\n")
            #led.value = False  # turn off LED to indicate we're done

            print('Change in time: ' + str(delta_hour) + ':' + str(delta_min) + ':' + str(delta_sec) + '\n')
            print("%d:%02d:%02d, " % (delta_hour, delta_min, delta_sec)) #

            # Read out all lines in the .csv file to verify the last entry
            #with open("/sd/stamp.csv", "r") as f:
            #print("Printing lines in file:")
            #line = f.readline()
            #while line != '':
            #print(line)
            #line = f.readline()

        #Check that the variable values remain
        print('Track the variable values on exit')
        print('Date in: ' + str(month_in) + '/' + str(day_in) + '/' + str(year_in))
        print('Time in: ' + str(hour_in) + ':' + str(min_in) + ':' + str(sec_in))
        print('Time out: ' + str(hour_out) + ':' + str(min_out) + ':' + str(sec_out) + '\n')

        track1_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Voice Note')
        if switch_2.is_pressed:
            machine.go_to_state('Voice Note')

########################################
# The "Focus Timer 1" state. Begin the focus timer here
class FocusTimer1(State):

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Focus Timer 1'


    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        focus1_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Focus Timer 1 State ####')
        print('Plateholder: Display Focus Timer counting down')
        print('Placeholder: Display date and time\n')


    def exit(self, machine):

        State.exit(self, machine)
        focus1_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:                   # Either button press results in a transition to the "Home" state
            machine.go_to_state('Home')
        if switch_2.is_pressed:                   # Question: Perhaps a transition to "Profile1" is more appropriate?
            machine.go_to_state('Home')
    # Experiment clearing the screen before transitioning, perhaps load the next screen here? OR in "exit"

########################################
# The "Profile 2" state. Implement at a later date. Any button press in this state causes a transition to the "Home" state.
class Profile2(State):

    def __init__(self):
        super().__init__()
        self.State = State()


    @property
    def name(self):
        return 'Profile 2'

    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        profile2_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Profile 2 State ####')
        print('Placeholder to display Profile 2 Screen, date and time\n')

    def exit(self, machine):

        State.exit(self, machine)
        profile2_scrn.value = False    # output low signal to the epaper microcontroller


    def pressed(self, machine):

        if switch_1.is_pressed:
            machine.go_to_state('Home')     # Either button press returns to "Home" state, further profiles will be implemented in the future
        if switch_2.is_pressed:
            machine.go_to_state('Home')


########################################
# The "Voice Note" state. A placeholder state that has an option to record a voice note or return to the "home" state
class VoiceNote(State):

    def __init__(self):
        super().__init__()
        self.State = State()

    @property
    def name(self):
        return 'Voice Note'

    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        voicenote_scrn.value = True    # output high signal to the epaper microcontroller
        print('#### Voice Note State ####')
        print('Placeholder: "Yes or No" to record a note\n')


    def exit(self, machine):

        State.exit(self, machine)
        voicenote_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:                   # Yes button results in a transition to the "Record" state
            machine.go_to_state('Record')
        if switch_2.is_pressed:                   # No button results in a transition to the "Home" state
            machine.go_to_state('Home')   # APPEND AN EMPTY ENTRY INTO THE SPREADSHEET HERE, then go gine


########################################
# The "Record Note" state. A placeholder state that will record a note then transition to the "home" state
# Constains an easter egg photo
class Record(State):

    def __init__(self):
        super().__init__()
        self.State = State()

    @property
    def name(self):
        return 'Record'

    def enter(self, machine):

        State.enter(self, machine)

        #Screen Placeholders
        record_scrn.value = True    # output high signal to the epaper microcontroller #Easter egg
        print('#### Record Note State ####')
        print('"Placeholder: Second Semester Functionality"\n')

    def exit(self, machine):

        State.exit(self, machine)
        record_scrn.value = False    # output low signal to the epaper microcontroller

    def pressed(self, machine):

        if switch_1.is_pressed:
            #print('Put Easter Egg photo here?\n')
            machine.go_to_state('Home') # Return "Home"
        if switch_2.is_pressed:
            machine.go_to_state('Home') # Return "Home"



################################################################################
# Create the state machine

LTB_state_machine = StateMachine()          # Defines the state machine
LTB_state_machine.add_state(Home())         # Adds the listed states to the machine (Except for the class, "State"
LTB_state_machine.add_state(Profile1())
LTB_state_machine.add_state(Tracking1())
LTB_state_machine.add_state(FocusTimer1())
LTB_state_machine.add_state(Profile2())
LTB_state_machine.add_state(VoiceNote())
LTB_state_machine.add_state(Record())

LTB_state_machine.go_to_state('Home')   #Starts the state machine in the "Home" state

while True:
    switch_1.value               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    switch_2.value               #Checks the switch 1 state each time the loop executes, necessary for button state changes
    LTB_state_machine.pressed()     #Transitions to the StateMachine attrubute, "pressed". Doesn't do much there other than report the current state