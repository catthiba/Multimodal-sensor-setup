# TABLE OF CONTENT  
#------------------------------------------------------------
# 1.  Required modules
# 2.  ShimmerCommands
# 2.1 Initialize class
# 2.2 Function: conenct to sensor unit
# 2.3 Function: wait for acknowledge respnse from sensor unit
# 2.4 Function: stop stream of data from sensor unit


# 1. Required modules
#---------------------
import sys, struct, serial


# 2. ShimmerCommands
#--------------------
class ShimmerCommands:

    # 2.1 Initialize class
    def __init__(self, comX):
        self.ser = self.serial_connect(comX)

    # 2.2 Function: conenct to sensor unit
    def serial_connect(self, comX):
        if len(sys.argv) < 2:
            print( "no device specified")
            print( "You need to specify the serial port of the device you wish to connect to")
            print( "example:")
            print( "   aAccel5Hz.py Com12")
            print( "or")
            print( "   aAccel5Hz.py /dev/rfcomm0")
        else:
            self.ser = serial.Serial(comX, 115200)
            self.ser.flushInput()
            print( "port opening, done.")
        return self.ser

    # 2.3 Function: wait for acknowledge respnse from sensor unit
    def wait_for_ack(self):
        ddata = ""
        ack = struct.pack('B', 0xff)
        while ddata != ack:
            ddata = self.ser.read(1)	  
        return

    # 2.4 Function: stop stream of data from sensor unit
    def stop_stream(self):
        KeyboardInterrupt()
        #send stop streaming command
        self.ser.write(struct.pack('B', 0x20))
        print( "stop command sent, waiting for ACK_COMMAND")
        ShimmerCommands.wait_for_ack(self)
        print( "ACK_COMMAND received.")
        #close serial port
        self.ser.close()
        print( "All done")