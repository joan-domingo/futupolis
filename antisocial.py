#!/usr/bin/python3

import time
import brickpi3

BP = brickpi3.BrickPi3()
MAX_POWER = 30

# call this function to turn off the motors and exit safely.
def SafeExit():
    # Unconfigure the sensors, disable the motors
    # and restore the LED to the control of the BrickPi3 firmware.
    BP.reset_all()

#Power motor A and D, forward or backward
def powerMotors(power):            
    try:
        if power > MAX_POWER:
            power = MAX_POWER
        elif power < -MAX_POWER:
            power = -MAX_POWER
    except IOError as error:
        print(error)
        power = 0

    #print('power', power)
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, power)
        
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
    print('turn around')
    list = []
    BP.set_motor_power(BP.PORT_A, MAX_POWER)
    BP.set_motor_power(BP.PORT_D, -MAX_POWER)
    for x in range(10):
        time.sleep(0.25)
        list.append(getDistance())

    print('turn to the best angle')
    pos = getPositionIndex(list)
    print(pos)
    time.sleep(pos * 0.25)
    stop()

def stop():
    print('stop')
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, 0)
    time.sleep(0.02)

def moveForward():
    print('move forward')
    BP.set_motor_power(BP.PORT_A + BP.PORT_D, MAX_POWER)
    
    print('check distance while going forward')
    for x in range(3):
        tempDist = getDistance()
        if tempDist < 50:
            stop()
            break
        time.sleep(1)
    
    stop()
    time.sleep(0.02)

def main():
    try:
        setUpBrickPi()
        initUltrasonicSensor()

        while True:
            distance = getDistance()
            print(distance)

            if distance < 50:
                turnAround()
                moveForward()
            
            time.sleep(1)

    except KeyboardInterrupt:
        SafeExit()

main()
