#!/usr/bin/python3

import time
import brickpi3
import random

BP = brickpi3.BrickPi3()
POWER = 50
MIN_DIST = 50 #cm

# call this function to turn off the motors and exit safely.
def SafeExit():
    # Unconfigure the sensors, disable the motors
    # and restore the LED to the control of the BrickPi3 firmware.
    BP.reset_all()

#Power motor A and D, forward or backward
def powerMotors():
    #print('power motors', power)
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, POWER)
        
    # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
    time.sleep(0.02)

#Steering motor C, turn left or right
def steeringMotor(position):
    try:
        target = BP.get_motor_encoder(BP.PORT_C) # read motor C's position
    except IOError as error:
        print(error)

    #print("turn to ", position)
    BP.set_motor_position(BP.PORT_C, position)
        
    # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
    time.sleep(0.02)

def setUpBrickPi():
    # setup motors
    try:
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
        BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D))
    except IOError as error:
        print(error)
    
    # make sure voltage is high enough
    if BP.get_voltage_battery() < 7:
        print("Battery voltage below 7v, too low to run motors reliably. Exiting.")
        SafeExit()

    # setup ultrasonic sensor
    BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)

def getDistance():
    return BP.get_sensor(BP.PORT_1) # distance is in CM from 0 to 255

def initUltrasonicSensor():
    value = 0
    while value == 0:
        try:
            value = getDistance()
        except:
            pass
        time.sleep(1)  # it takes a few seconds until the ultrasonic sensor starts emitting

def getPositionIndex(list):
    maxValue = max(list)
    return list.index(maxValue)
    
def turnAround():
    #print('turn around')
    tempDistance = 0
    turningTime = 0

    #random turn to left or right
    randomValue = random.randint(0,1)
    if randomValue == 0:
        BP.set_motor_power(BP.PORT_A, POWER)
        BP.set_motor_power(BP.PORT_D, -POWER)
    else:
        BP.set_motor_power(BP.PORT_A, -POWER)
        BP.set_motor_power(BP.PORT_D, POWER)

    while tempDistance < 60:
        if turningTime > 2:
            break
        try:
            tempDistance = getDistance()
            turningTime += 0.1
            time.sleep(0.1)
            #print(tempDistance, turningTime)
        except:
            pass

def stop():
    #print('stop')
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, 0)
    time.sleep(0.02)

def moveForward():
    #print('move forward')
    powerMotors()
    
    #print('check distance while going forward')
    for x in range(30):
        tempDist = getDistance()
        if tempDist < MIN_DIST:
            stop()
            break
        time.sleep(0.1)
    
    stop()
    time.sleep(0.02)

def runAway():
    turnAround()
    moveForward()

def main():
    try:
        setUpBrickPi()
        initUltrasonicSensor()

        while True:
            distance = getDistance()
            #print(distance)

            if distance < MIN_DIST:
                runAway()
            
            time.sleep(0.02)

    except KeyboardInterrupt:
        SafeExit()

main()
