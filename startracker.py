'''
Program to run DIY star tracker
Created by Jacob Sommer 2019-10-28
'''
import math
from time import sleep
import RPi.GPIO as GPIO
import os
from blynklib import Blynk
from dotenv import load_dotenv
load_dotenv()

TPI = 20.0 # tpi of the screw
BASE = 15.125 + .415 # length of board plus extra length measured from end of board to hinge when its at 90 degrees (inches)
STARTING_HEIGHT = 1.23 # length of screw in inches between the two boards (measure with calipers, best when at least an inch)
STARTING_ANGLE = math.atan(STARTING_HEIGHT / BASE) # the smallest it can close
STEPS = 512 # 11.25 degree rotation 360/11.25=32 64:1 gear ratio 32*64=2048 divide by 4 2048/4=512
ROTATION_RATE = 2.0 * math.pi / 86164.0905 # rotation rate of earth in radians per second using the mean sidereal day (24 hours - 4 minutes + 4 seconds = 86164.0905 s)
# https://en.wikipedia.org/wiki/Sidereal_time - 23 hrs 56 minutes 4.0905 seconds
MOON_ORBIT_RATE = 2.0 * math.pi / 2360591.6 # moon orbit rate measured as angular velocity around earth in radians per second
MAX_ANGLE = math.radians(35) # the widest it can open

# define the ports the IN1-4 for the motor board are connected to
# based on the number coming after GPIO ex: IN1 is connected to port 11/GPIO17 which is 17
IN1 = 6
IN2 = 13
IN3 = 19
IN4 = 26
DELAY = 0.001 # delay between outputs sent to the pins

# Blynk
blynk = Blynk(os.getenv('STARTRACKER_BLYNK_API_KEY'))

# set up GPIO
def setupGPIO():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(IN1, GPIO.OUT)
  GPIO.setup(IN2, GPIO.OUT)
  GPIO.setup(IN3, GPIO.OUT)
  GPIO.setup(IN4, GPIO.OUT)
  GPIO.output(IN1, False)
  GPIO.output(IN2, False)
  GPIO.output(IN3, False)
  GPIO.output(IN4, False)

# motor methods
def Step1():
  GPIO.output(IN4, True)
  sleep(DELAY)
  GPIO.output(IN4, False)

def Step2():
  GPIO.output(IN4, True)
  GPIO.output(IN3, True)
  sleep(DELAY)
  GPIO.output(IN4, False)
  GPIO.output(IN3, False)

def Step3():
  GPIO.output(IN3, True)
  sleep(DELAY)
  GPIO.output(IN3, False)

def Step4():
  GPIO.output(IN2, True)
  GPIO.output(IN3, True)
  sleep(DELAY)
  GPIO.output(IN2, False)
  GPIO.output(IN3, False)

def Step5():
  GPIO.output(IN2, True)
  sleep(DELAY)
  GPIO.output(IN2, False)

def Step6():
  GPIO.output(IN1, True)
  GPIO.output(IN2, True)
  sleep(DELAY)
  GPIO.output(IN1, False)
  GPIO.output(IN2, False)

def Step7():
  GPIO.output(IN1, True)
  sleep(DELAY)
  GPIO.output(IN1, False)

def Step8():
  GPIO.output(IN4, True)
  GPIO.output(IN1, True)
  sleep(DELAY)
  GPIO.output(IN4, False)
  GPIO.output(IN1, False)

def left(step):
  for i in range(step):   
    Step1()
    Step2()
    Step3()
    Step4()
    Step5()
    Step6()
    Step7()
    Step8()
  
def right(step):
  for i in range(step):
    Step8()
    Step7()
    Step6()
    Step5()
    Step4()
    Step3()
    Step2()
    Step1()

class StarTracker:
  def __init__(self):
    self.angle = STARTING_ANGLE # radians
    self.current_height = STARTING_HEIGHT # inches
    self.totalSteps = 0
    self.secElapsed = 0
    self.running = False
    self.paused = False
    self.resetting = False
    self.lunar = False # in moon tracking mode or not
  
  def spin(self):
    '''
    Calculates how much the motor needs to step then rotates it
    '''
    # calculate how much to spin motor
    h = math.tan(self.angle) * BASE # tan angle = h/base
    diff = h - self.current_height # calculate how much higher the screw needs to move
    numRot = TPI * diff # number of rotations motor has to make
    print('Angle: ', math.degrees(self.angle))
    self.spinMotor(numRot) # spin the motor by the calculated number of rotations

  def spinMotor(self, numRot):
    '''
    Steps the motor to meet specified number of rotations
    '''
    numSteps = math.floor(STEPS * numRot) # calculate number of steps by multiplying the number of steps per rotation by the number of rotations needed to be made
    numRot = numSteps / STEPS # calculate new numRot to account for rounding error
    diff = numRot / TPI # calculate actual difference in height - num rotations / (rotation/inch)
    self.current_height += diff # add this difference in height to current_height
    self.totalSteps += numSteps # keep track of total steps for resetting
    print('Height:', self.current_height)
    print('Steps: ', numSteps)
    left(numSteps)

  def loop(self):
    '''
    Main program loop
    '''
    setupGPIO() # set up the GPIO pins
    left(11) # first one never works so do it before
    sleep(1)
    while self.running and self.angle < MAX_ANGLE:
      blynk.run() # make sure blynk is running while the loop is running
      if self.paused: # if its paused, don't spin
        continue

      self.angle += ROTATION_RATE # increment angle by rotation rate of earth in radians per second
      if self.lunar:
        self.angle += MOON_ORBIT_RATE
      self.spin()
      self.secElapsed += 1
      blynk.virtual_write(2, math.degrees(tracker.angle)) # write to angle value in Blynk
      blynk.virtual_write(3, tracker.current_height) # write to height value in Blynk
      blynk.virtual_write(4, tracker.secElapsed / 60.0) # write to time (minutes) value in Blynk
      sleep(1) # wait 1 second
    
    print('Resetting...')
    print('Total Steps: ', self.totalSteps)
    blynk.virtual_write(0, 0) # make start button display OFF
    right(self.totalSteps) # reset screw height back to start position
    GPIO.cleanup() # clean up GPIO
    # reset all variables
    self.running = False
    self.paused = False
    self.angle = STARTING_ANGLE
    self.current_height = STARTING_HEIGHT
    self.totalSteps = 0
    self.secElapsed = 0
    self.resetting = False
    print('Done')

  def reset(self):
    '''
    Reset everything by toggling some variables to trigger the reset
    '''
    self.resetting = True
    self.running = False


tracker = StarTracker()

@blynk.handle_event('write V0')
def onStart(pin, value):
  if tracker.resetting: # if it is resetting, don't mess with anything
    return

  if int(value[0]) == 1: # if value changed to on (start it or resume it)
    if tracker.running: # if it is running and user sets it to ON they want to unpause it
      tracker.paused = False
    else: # if it is not running, user is trying to turn it on
      tracker.running = True
      tracker.loop()
  else: # if value changed to off (pause it)
    tracker.paused = True

@blynk.handle_event('write V1')
def onReset(pin, value):
  if tracker.running and not tracker.resetting:
    tracker.reset()

@blynk.handle_event('write V5')
def onLunarToggle(pin, value):
  tracker.lunar = int(value[0]) == 1
 
while True:
  blynk.run()
