##########################################
# ===== Ultrasonic Sensor =====
'''
This file contains class file for ultrasonic sensor.

Author: Aiden Corke
'''
##########################################

# ===== Imports =====
import sys
import time
from smbus2 import SMBus, i2c_msg

# ===== Class =====
class UltrasonicSensor:
    # === Parameters ===
    __units = {"mm":0, "cm":1}
    __dist_reg = 0

    __RGB_MODE = 2
    __RGB1_R = 3
    __RGB1_G = 4
    __RGB1_B = 5
    __RGB2_R = 6
    __RGB2_G = 7
    __RGB2_B = 8

    __RGB1_R_BREATHING_CYCLE = 9
    __RGB1_G_BREATHING_CYCLE = 10
    __RGB1_B_BREATHING_CYCLE = 11
    __RGB2_R_BREATHING_CYCLE = 12
    __RGB2_G_BREATHING_CYCLE = 13
    __RGB2_B_BREATHING_CYCLE = 14   
     

    # === Class Attributes ===
    def __init__(self):
        self.i2c_addr = 0x77
        self.i2c = 1
        self.Pixels = [0,0]
        self.RGBMode = 0
        self.numPixels = 2

    # === Functions ===
    
    def __getattr(self, attr):
        '''This function checks if attribute matches criteria.'''
        if attr in self.__units:
            return self.__units[attr]
        if attr == "Distance":
            return self.getDistance()
        else:
            raise AttributeError('Unknown attribute : %s'%attr)

    def setRBGMode(self, mode):
        '''This function sets the RGB mode.'''
        try:
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, self.__RGB_MODE, mode)
        except BaseException as e:
            print(e)
    
    def setPixelColor(self, index, rgb):      
        '''This function sets the colour of the ultrasonic sensor'''  
        color = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
        try:
            if index != 0 and index != 1:
                return 
            start_reg = 3 if index == 0 else 6
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg, 0xFF & (color >> 16))
                bus.write_byte_data(self.i2c_addr, start_reg+1, 0xFF & (color >> 8))
                bus.write_byte_data(self.i2c_addr, start_reg+2, 0xFF & color)
                self.Pixels[index] = color
        except BaseException as e:
            print(e)        

    def getPixelColor(self, index):
        '''This function extracts the colour setting of the sensor.'''
        if index != 0 and index != 1:
            raise ValueError("Invalid pixel index", index)
        return ((self.Pixels[index] >> 16) & 0xFF,
                (self.Pixels[index] >> 8) & 0xFF,
                self.Pixels[index] & 0xFF)    

    def setBreathCycle(self, index, rgb, cycle):
        '''This function sets the sensor's colours to cycle'''
        try:
            if index != 0 and index != 1:
                return
            if rgb < 0 or rgb > 2:
                return
            start_reg = 9 if index == 0 else 12
            cycle = int(cycle / 100)
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg + rgb, cycle)
        except BaseException as e:
            print(e)
            
    def startSymphony(self):
        '''This function sets the sensor's colour cycle to a symphony.'''
        self.setRGBMode(1)
        self.setBreathCycle(1,0, 2000)
        self.setBreathCycle(1,1, 3300)
        self.setBreathCycle(1,2, 4700)
        self.setBreathCycle(2,0, 4600)
        self.setBreathCycle(2,1, 2000)
        self.setBreathCycle(2,2, 3400)

    def getDistance(self,range_limit=5000):
        '''This function extracts the distance measurement from the sensor.'''
        dist = 99999
        try:
            with SMBus(self.i2c) as bus:
                msg = i2c_msg.write(self.i2c_addr, [0,])
                bus.i2c_rdwr(msg)
                read = i2c_msg.read(self.i2c_addr, 2)
                bus.i2c_rdwr(read)
                dist = int.from_bytes(bytes(list(read)), byteorder='little', signed=False)
                
                # If distance exceeds range limit it caps the value to the limit
                if dist > range_limit:
                    dist = range_limit
        except BaseException as e:
            print(e)
        return dist

if __name__ == '__main__':
    s = UltrasonicSensor()
    
    # Set sensor to cycle through colours while active
    s.setRGBMode(0)
    s.setPixelColor(0, (0, 0, 0))
    s.setPixelColor(1, (0, 0, 0))
    time.sleep(0.1)
    s.setPixelColor(0, (255, 0, 0))
    s.setPixelColor(1, (255, 0, 0))
    time.sleep(1)
    s.setPixelColor(0, (0, 255, 0))
    s.setPixelColor(1, (0, 255, 0))
    time.sleep(1)
    s.setPixelColor(0, (0, 0, 255))
    s.setPixelColor(1, (0, 0, 255))
    time.sleep(1)
    s.startSymphony()
    while True:
        time.sleep(0.1)
        print(s.getDistance())