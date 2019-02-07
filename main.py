#!/usr/bin/python

import io         # used to create file streams
from io import open
import fcntl      # used to access I2C parameters like addresses

from datetime import datetime
from pytz import timezone

import time       # used for sleep delay and timestamps
import string     # helps parse strings
import serial
from smbus import SMBus

from dco2 import DCO2
from do import AtlasI2C
from brix import BRIX

from kafka import KafkaProducer
import simplejson as json

DEVICE_ID = 1
SERVER_ADR = 'localhost:9092'
TOPIC_NAME = 'hello-kafka'

# I2C addresses
DO_ADDR = 100
PH_ADDR = 99

# Instance of each class that controls the sensor
device_do = AtlasI2C() 	# For DO
device_ph = AtlasI2C()	# For pH
device_dco2 = DCO2()	# For DCO2
device_brix = BRIX()	# For Brix 

# Reading cycle time limit 
MINIMUM_DELAY = 3.0

# Get all sensor's data & send to the server
def read_all_data():
    do_val = device_do.query("R")
    ph_val = device_ph.query("R")
    dco2_val = device_dco2.send_read_cmd() 
    brix_val = device_brix.readData()
    
    # Send json format data to server
    timestamp =str(time.time()).split('.')[0] 
    data = {'created_time' : timestamp , 'device_id' : DEVICE_ID, 'do' : do_val, 'ph' : ph_val, 'dco2' : dco2_val, 'brix_temp' : brix_val[0], 'brix_brix': brix_val[1] }    
    send_all_data(data)
    
    # Print the data
    print("DO " + do_val + " ppm")
    print("pH " + ph_val + " ppm")
    print("DCO2 " + dco2_val + " ppm")
    print("Brix-Temp "+ str(brix_val[0]) + " °C")
    print("Brix-Brix " + str(brix_val[1]) + " %Brix") 
    print("")

# Perform remote calibration 
def calibration_all():
    # IT MUST BE CHANGED!!!!!!!!!!!!!!!!!!!!
    print("DO done" + device_do.query("Cal,0"))
    device_dco2.send_cal_cmd()
    print("")

# Conncect to a kafka producer 
def connect_kafka_producer():
    _producer = None
    try :
        _producer = KafkaProducer(bootstrap_servers= [SERVER_ADR], api_version = (0,10))
    except Exception as e :
        print('Exception while connecting kafka')
        print(e)
    return _producer 

# Send sensor's data to the server
def send_all_data(data):
    kafka_producer = connect_kafka_producer()
    try:
        kafka_producer.send(TOPIC_NAME, json.dumps(data).encode('utf-8'))
        kafka_producer.flush()
    except Exception as e:
        print('Exception in publishing message')
        print(e)
    if kafka_producer is not None:
        kafka_producer.close()

# Initial setting - I2C addresses of DO/PH sensor 
def init_setting() :
    device_do.set_i2c_address(DO_ADDR)
    device_ph.set_i2c_address(PH_ADDR)

def main():
	
	init_setting()
	real_raw_input = vars(__builtins__).get('raw_input', input)
        
        print("Welcome!")
        print("1. Read ")
        print("2. Cont_read , n")
        print("3. Cal")
        print("4. Quit")
        print("")

	# Get Command 
	while True:
		user_cmd = real_raw_input("Enter command: ")
		
		# Quit
		if user_cmd.upper() =="QUIT"  or user_cmd=="4":
			break
			
                # Read all data
		elif user_cmd.upper() =="READ" or user_cmd=="1":
			try:
				read_all_data()
			except IOError as e:
				print("Read failed")
				print(e)
				
		# Remote Calibration
                elif user_cmd.upper() =="CAL" or user_cmd=="3":
			try:
				calibration_all()
			except IOError as e:
				print("Calibration failed")
				print(e)

		# Continuous reading mode 
		elif user_cmd.upper().startswith("CONT_READ") or user_cmd.startswith("2"):
                        delaytime = float(user_cmd.split(',')[1])

			# Check for polling time being too short
			# Change it to the minimum delay time if too short
			if delaytime < MINIMUM_DELAY:
				print("Polling time is shorter than timeout, setting polling time to %0.2f" % MINIMUM_DELAY)
				delaytime = MINIMUM_DELAY

			print("%0.2f seconds, press ctrl-c to stop reading" % delaytime)

			try:
				while True:
					read_all_data()
					time.sleep(delaytime-MINIMUM_DELAY)
			except KeyboardInterrupt: 		
				# Catch the ctrl-c command, which stops reading
				print("Continuous Reading stopped")
		else:
			print( "Please input valid command.")
			
if __name__ == '__main__':
	main()

