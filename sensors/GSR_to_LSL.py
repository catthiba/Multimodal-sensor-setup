# TABLE OF CONTENT
#-----------------------------------------------
# 1     Required modules
# 2     GSR_to_LSL
# 2.1   Initialize contact with GSR sensor unit
# 2.2   Define GSR setup
# 2.2.1 Send the set sensors command
# 2.2.2 Enable the internal expansion board power
# 2.2.3 Define stream info, displayed in LabRecorder  
# 2.2.4 Create stream info                            
# 2.2.5 Create stream outlet
# 2.2.6 Send the set sampling rate command
# 2.2.7 Send start streaming command
# 2.2.8 Read incoming data


# 1 Required modules
#--------------------
import struct
from pylsl import StreamInfo, StreamOutlet
from ShimmerCommands import ShimmerCommands

# 2 GSR_to_LSL
#------------------
class GSR_to_LSL:
   # 2.1 Initialize contact with GSR sensor unit
   def __init__(self, comX):
      self.ser = ShimmerCommands.serial_connect(self, comX)
      self.GSR_setup()

   # 2.2 Define GSR setup
   def GSR_setup(self):
      # 2.2.1 Send the set sensors command
      self.ser.write(struct.pack('BBBB', 0x08 , 0x04, 0x01, 0x00))  #GSR and PPG
      ShimmerCommands.wait_for_ack(self)   
      print( "sensor setting, done.")

      # 2.2.2 Enable the internal expansion board power
      self.ser.write(struct.pack('BB', 0x5E, 0x01))
      ShimmerCommands.wait_for_ack(self)
      print( "enable internal expansion board power, done.")

      # 2.2.3 Define stream info, displayed in LabRecorder 
      name = 'Shimmer_GSR'
      ID = 'Shimmer_GSR'
      channels = 1
      sample_rate = 50
      datatype = 'float32'
      streamType = 'GSR'
      print("Creating LSL stream for GSR. \nName: %s\nID: %s\n" %(name, ID))

      # 2.2.4 Create stream info
      info_gsr = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)

      # 2.2.5 Create stream outlet
      chns = info_gsr.desc().append_child("channels")
      ch = chns.append_child("channel")
      ch.append_child_value("label", "CH1")
      outlet_gsr = StreamOutlet(info_gsr)

      # 2.2.6 Send the set sampling rate command
      sampling_freq = 50
      clock_wait = (2 << 14) / sampling_freq
      self.ser.write(struct.pack('<BH', 0x05, int(clock_wait)))
      ShimmerCommands.wait_for_ack(self)

      # 2.2.7 Send start streaming command
      self.ser.write(struct.pack('B', 0x07))
      ShimmerCommands.wait_for_ack(self)
      print( "start command sending, done.")

      # 2.2.8 Read incoming data and push to LSL stream
      ddata = ""
      numbytes = 0
      framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)
      print( "Packet Type\tTimestamp\tGSR\tPPG")
      try:
         while True:
            while numbytes < framesize:
               ddata = self.ser.read(framesize)
               numbytes = len(ddata)
            
            data = ddata[0:framesize]
            ddata = ddata[framesize:]
            numbytes = len(ddata)

            # read basic packet information
            (packettype) = struct.unpack('B', data[0:1])
            (timestamp0, timestamp1, timestamp2) = struct.unpack('BBB', data[1:4])
            # print('packettype', packettype)

            # read packet payload
            (PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])

            # get current GSR range resistor value
            Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
            if(Range == 0):
               Rf = 40.2   # kohm
            elif(Range == 1):
               Rf = 287.0  # kohm
            elif(Range == 2):
               Rf = 1000.0 # kohm
            elif(Range == 3):
               Rf = 3300.0 # kohm

            # convert GSR to kohm value
            gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
            GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)

            # convert PPG to milliVolt value
            PPG_mv = PPG_raw * (3000.0/4095.0)
            timestamp = timestamp0 + timestamp1*256 + timestamp2*65536

            #print( "0x%02x\t\t%5d,\t%4d,\t%4d" % (packettype[0], timestamp, GSR_ohm, PPG_mv))
            #print("Sending GSR data...")

            # push data to LSL stream
            gsr_chunk = []
            gsr_chunk.append(GSR_ohm)
            outlet_gsr.push_chunk(gsr_chunk)
         
      except: ShimmerCommands.stop_stream(self)
