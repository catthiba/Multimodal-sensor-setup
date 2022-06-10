# TABLE OF CONTENT
#-----------------------------------------------
# 1         Required modules
# 2         ECG_to_LSL
# 2.1       Initialize ECG sensor
# 2.1.1     Initialize contact with ECG sensor unit
# 2.1.2     Set configuration parameters
# 2.2       Define ECG setup
# 2.2.1     Set Sample rate 
# 2.2.2     Request daughter Boa
# 2.2.3     Send Set sensor command 
# 2.2.4     Set configuration bytes                           
# 2.2.5     Set calibration factor
# 2.2.6     Configure Chip1 and Chip2 
# 2.2.7     Send start streaming command
# 2.2.8     Define stream info, displayed in LabRecorder  
# 2.2.9     Create stream info                            
# 2.2.10    Create stream outlet
# 2.2.11    Read incoming data and push to LSL stream


# 1 Required modules
#--------------------
import sys, struct, serial, time
from pylsl import StreamInfo, StreamOutlet
from ShimmerCommands import ShimmerCommands

# 2 ECG_to_LSL
#------------------
class ECG_to_LSL:
   # 2.1 Initialize ECG sensor
    def __init__(self, comX):
        # 2.1.1 Initialize contact with ECG sensor unit
        self.ser = ShimmerCommands.serial_connect(self, comX)
        # 2.1.2 Set configuration parameters
        self.exgconfigGain = {	#decimal
            'GAIN_1':  0x15, #21
            'GAIN_2':  0x25, #37
            'GAIN_3':  0x35, #53
            'GAIN_4':  0x45, #69
            'GAIN_6':  0x05, #5
            'GAIN_8':  0x55, #55
            'GAIN_12': 0x65  #101
        }

        self.exgGain = {
            'GAIN_1':  1, #used
            'GAIN_2':  2,
            'GAIN_3':  3,
            'GAIN_4':  4, #Recommended 
            'GAIN_6':  6, #Default
            'GAIN_8':  8,
            'GAIN_12': 12
        }

        self.exg_24bit = [0x18, 0x00, 0x00]
        self.exg_16bit = [0x18, 0x00, 0x00] #[0x00, 0x00, 0x18]

        self.samplingFrequency 	= 512 						# frequency in Hz
        self.exgRes_24bit 		= False						# 24bit if True, else 16bit
        self.exgGainValue 		= self.exgconfigGain['GAIN_4'] 	# sets a gain of 1


        # The internal sampling rate of the ADS1292R chips needs to be set based on the Shimmers sampling rate
        if (self.samplingFrequency<=125):
            self.exgSamplingRate = 0x00 # 125Hz
        elif (self.samplingFrequency<=250):
            self.exgSamplingRate = 0x01 # 250Hz
        elif (self.samplingFrequency<=500):
            self.exgSamplingRate = 0x02 # 500Hz
        elif (self.samplingFrequency<=1000):
            self.exgSamplingRate = 0x03 # 1000Hz
        elif (self.samplingFrequency<=2000):
            self.exgSamplingRate = 0x04 # 2000Hz
        elif (self.samplingFrequency<=4000):
            self.exgSamplingRate = 0x05 # 4000Hz
        else:
            self.exgSamplingRate = 0x02 # 500Hz

        # Chip 1 configuration
        self.chip1Config = [self.exgSamplingRate, 0xA3, 0x10, self.exgGainValue, self.exgGainValue, 0x00, 0x00, 0x00, 0x02, 0x01]

        # Chip 2 configuration
        self.chip2Config = [self.exgSamplingRate, 0xA3, 0x10, self.exgGainValue, self.exgGainValue, 0x00, 0x00, 0x00, 0x02, 0x01]

        self.serNumber = 0
        self.srRev = 0
        self.ECG_setup()

    # 2.2 Define ECG setup

    # 2.2.1 Set Sample rate 
    def setSamplingRateHz(self, rate=512):
        # send the set sampling rate command
        sampling_freq = rate #Hz
        clock_wait = (2 << 14) / sampling_freq
        self.ser.write(struct.pack('<BH', 0x05, int(clock_wait)))
        ShimmerCommands.wait_for_ack(self)
        print ("Freq sent...")
    
    # 2.2.2 Request daughter Board
    def requestDaughterCard(self):
        #get the daughter card ID byte (SR number)
        print("Requesting Daughter Card ID and Revision number...")
        self.ser.write(struct.pack('BBB', 0x66, 0x02,0x00))
        ShimmerCommands.wait_for_ack(self)

        ddata = list(struct.unpack(4*'B', self.ser.read(4)))
        self.srNumber = ddata[2]
        self.srRev = ddata[3]

        print ("Device: SR%d-%d" % (self.srNumber, self.srRev))

    # 2.2.3 Send Set sensor command 
    def setSensors(self):
        self.ser.write(struct.pack('BBBB', 0x08, 0x18, 0x00, 0x00))  #exg1 and exg2
        ShimmerCommands.wait_for_ack(self)
        print ("Sensor Enabling done...")

    # 2.2.4 Set configuration bytes 
    def setConfigBytes(self):
        if self.exgRes_24bit:
            sensors = [0x08] + self.exg_24bit
        else:
            sensors = [0x08] + self.exg_16bit
        self.ser.write(sensors)
        ShimmerCommands.wait_for_ack(self)
        time.sleep(2)

    # 2.2.5 Set calibration factor 
    def  setCalFactor(self):
        if self.exgRes_24bit:
            exgCalFactor = (((2.42*1000)/self.exgGain['GAIN_4'])/(pow(2,23)-1))
        else:
            exgCalFactor = (((2.42*1000)/self.exgGain['GAIN_4'])/(pow(2,23)-1)) #exgCalFactor = (((2.42*1000)/(self.exgGain['GAIN_4']*2))/(pow(2,15)-1))

        if(self.srNumber == 47 and self.srRev >= 4):
            self.chip1Config[1] |= 8 # Config byte for CHIP1 in SR47-4
        return exgCalFactor

    # 2.2.6 Configure Chip1 and Chip2 
    def configureChips(self):
        # Configure Chip 1
        chip1Config = [0x61, 0x00, 0x00, 0x0A] + self.chip1Config
        self.ser.write(chip1Config)
        ShimmerCommands.wait_for_ack(self)

        # Configure Chip 2 
        chip2Config = [0x61, 0x01, 0x00, 0x0A] + self.chip2Config
        self.ser.write(chip2Config)
        ShimmerCommands.wait_for_ack(self)
        print ("Configuration sent...")

    # 2.2.7 Send start streaming command
    def startStraming(self):
        # send start streaming command
        self.ser.write(struct.pack('B', 0x07))
        ShimmerCommands.wait_for_ack(self)
        print ("Start sent...")

    def setupLSLStream(self):
        # 2.2.8 Define stream info, displayed in LabRecorder 
        name = 'Shimmer_ECG'
        ID = 'Shimmer_Ecg'
        channels = 4
        sample_rate = self.samplingFrequency
        datatype = 'float32'
        streamType = 'ECG'
        print("Creating LSL stream for ECG. \nName: %s\nID: %s\n" %(name, ID))

        # 2.2.9 Create stream info
        info_ecg = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)

        # 2.2.10 Create stream outlet
        chns = info_ecg.desc().append_child("channels")
        for label in ["C1CH1", "C1CH2", "C2CH1", "C2CH2"]:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)
        outlet_ecg = StreamOutlet(info_ecg)
        return outlet_ecg

 
    
    def ECG_setup(self):
        self.requestDaughterCard()
        self.setSensors()
        self.setSamplingRateHz(self.samplingFrequency)
        self.setConfigBytes()
        exgCalFactor = self.setCalFactor()
        self.configureChips()
        self.startStraming() 
        outlet_ecg = self.setupLSLStream()

        # 2.2.11 Read incoming data and push to LSL stream
        ddata = ""
        numbytes = 0
        framesize = (18 if self.exgRes_24bit else 14) # 1byte packet type + 3byte timestamp + 14byte ExG data

        print ("Packet Type,\tTimestamp, \tChip1 Status, \tChip1 Channel 1,2 (mv), \tChip2 Status, \tChip2 Channel 1,2 (mV)")
        try:
            while True:
                while numbytes < framesize:
                    ddata = self.ser.read(framesize)
                    numbytes = len(ddata)
                
                data = ddata[0:framesize]
                ddata = ddata[framesize:]
                numbytes = len(ddata)

                (packettype,) = struct.unpack('B', data[0:1])
                
                (ts0, ts1, ts2, c1status) = struct.unpack('BBBB', data[1:5])
                
                timestamp = ts0 + ts1*256 + ts2*65536
                # 24-bit signed values MSB values are tricky, as struct only supports 16-bit or 32-bit
                # pad with zeroes at LSB end and then shift the result
                
                if self.exgRes_24bit:
                    # chip 1
                    c1ch1 = struct.unpack('>i', (data[5:8]))[0] >> 8
                    c1ch2 = struct.unpack('>i', (data[8:11] + '\0'))[0] >> 8

                    # status byte
                    (c2status,) = struct.unpack('B', data[11:12])

                    # chip 2
                    c2ch1 = struct.unpack('>i', (data[12:15] + '\0'))[0] >> 8
                    c2ch2 = struct.unpack('>i', (data[15:framesize] + '\0'))[0] >> 8
                else:
                    # chip 1
                    c1ch1 = struct.unpack('>h', data[5:7])[0]
                    c1ch2 = struct.unpack('>h', data[7:9])[0]

                    # status byte
                    (c2status,) = struct.unpack('B', data[9:10])

                    # chip 2
                    c2ch1 = struct.unpack('>h', data[10:12])[0]
                    c2ch2 = struct.unpack('>h', data[12:framesize])[0]

                # Calibrate exg channels:
                c1ch1 *= exgCalFactor
                c1ch2 *= exgCalFactor
                c2ch1 *= exgCalFactor
                c2ch2 *= exgCalFactor

                #print ("0x%02x,\t\t%5d,\t0x%02x,\t\t%2.4f,%2.4f,\t\t%s0x%02x,\t\t%2.4f,%2.4f" % \
                #(packettype, timestamp, c1status, c1ch1, c1ch2, "\t" if c1ch1>0 else "", c2status, c2ch1, c2ch2))
                #print("Sending ECG data...")
 

                ecg_data = [c1ch1, c1ch2, c2ch1, c2ch2]
                ecg_chunk = []
                ecg_chunk.append(ecg_data)
                outlet_ecg.push_chunk(ecg_chunk)
        except: ShimmerCommands.stop_stream(self)
