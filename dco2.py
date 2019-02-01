import serial

START =chr(0x23)
END = chr(0x21)
WRITE = chr(0x57)
READ = chr(0x52)
ZERO_CAL = chr(0x31)
SPAN_CAL = chr(0x32)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

READ_CMD = [ START, WRITE, READ, chr(0x30), chr(0x35), END]
CAL_ZERO_CMD = [ START, WRITE, ZERO_CAL, chr(0x33), chr(0x34), END]

#IT MUST BE CHANGED!!!
CAL_SPAN_CMD = [ START, WRITE, ZERO_CAL,  chr(0x33), chr(0x34), END]

class DCO2:
    # Open usb serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) 
    
    def send_cal_cmd(self):
         self.ser.write(''.join(CAL_ZERO_CMD))
    
    def send_read_cmd(self) :
        self.ser.write(''.join(READ_CMD))
        data = []
        
        if self.ser.inWaiting() > 0 :
            while True :
		tmp = self.ser.read(1)
                if tmp =="\n":
			break;
		data.append(tmp)

        return ''.join(data[2:]).replace(' ppm\r', '')
	
