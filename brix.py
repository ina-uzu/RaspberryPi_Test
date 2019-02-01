import serial
import string
import time
import RPi.GPIO as GPIO

BAUD_RATE = 22800
READ_RATE = 1
DATA_LENGTH =13

#Can be changed
ADDR = 0x01
CRC_L = 0x44
CRC_H = 0x0C

READ_CMD = [chr(ADDR),chr(0x3), chr(0x00) ,chr(0x00),chr(0x00),chr(0x08), chr(CRC_L), chr(CRC_H)]
READ_CMD_STR = ''.join(READ_CMD)

class BRIX :
    #CODE
    ser = serial.Serial("/dev/ttyS0", BAUD_RATE, timeout=1)

    def readData(self):
        self.ser.write(READ_CMD_STR) 
        res = []
        data=[]
        time.sleep(1) 
        for i in range(DATA_LENGTH):
            tmp = self.ser.read(1)
            try :
                data.append(ord(tmp))
                #print(ord(tmp))
            except :
                #print(0)
                data.append(0)
        
        temp = data[3]
        for i in range(3):
            temp = temp << 4
            temp = data[i+4]

        res.append(float(temp))

        temp = data[7]
        for i in range(3):
            temp = temp << 4
            temp = data[i+8]
        res.append(float(temp))

