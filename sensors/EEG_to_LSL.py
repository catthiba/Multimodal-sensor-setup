# TABLE OF CONTENT
#-----------------------------------------------
# 1     Required modules
# 2     GSR_to_LSL
# 2.1   Initialize contact with EEG sensor unit
# 2.2   Define EEG setup
# 2.2.1 Get EEG and AUX channels
# 2.2.2 Define stream info, displayed in LabRecorder
# 2.2.3 Create eeg stream info
# 2.2.4 Create aux stream info                      
# 2.2.5 Create stream outlet
# 2.2.6 Read incoming data and push to LSL stream


# 1 Required modules
#--------------------
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from pylsl import StreamInfo, StreamOutlet

# 2 EEG_to_LSL
#------------------
class EEG_to_LSL:
    # 2.1 Initialize contact with EEG sensor unit
    def __init__(self, comX):
        BoardShim.enable_dev_board_logger()
        self.params = BrainFlowInputParams()
        self.params.serial_port = comX
        self.EEG_setup()

    # 2.2 Define EEG setup
    def EEG_setup(self):
        board = BoardShim(BoardIds.CYTON_BOARD.value, self.params) # added cyton board id here
        srate = board.get_sampling_rate(BoardIds.CYTON_BOARD.value)
        board.prepare_session()
        board.start_stream()
        #board.config_board('/2')  # enable analog mode only for Cyton Based Boards!    # added from example in docs

        # 2.2.1 Get EEG and AUX channels 
        eeg_chan = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        aux_chan = BoardShim.get_accel_channels(BoardIds.CYTON_BOARD.value)
        print('EEG channels:')
        print(eeg_chan)
        print('Accelerometer channels')
        print(aux_chan)

        # 2.2.2 Define stream info, displayed in LabRecorder 
        name = 'OpenBCIEEG'
        ID = 'OpenBCIEEG'
        channels = 8
        sample_rate = 250
        datatype = 'float32'
        streamType = 'EEG'
        print(f"Creating LSL stream for EEG. \nName: {name}\nID: {ID}\n")

        # 2.2.3 Create eeg stream info
        info_eeg = StreamInfo(name, streamType, channels, sample_rate, datatype, ID)
        chns = info_eeg.desc().append_child("channels")
        for label in ["AFp1", "AFp2", "C3", "C4", "P7", "P8", "O1", "O2"]:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)

        # 2.2.4 Create aux stream info
        info_aux = StreamInfo('OpenBCIAUX', 'AUX', 3, 250, 'float32', 'OpenBCItestAUX')
        chns = info_aux.desc().append_child("channels")
        for label in ["X", "Y", "Z"]:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)

        # 2.2.5 Create stream outlets
        outlet_aux = StreamOutlet(info_aux)
        outlet_eeg = StreamOutlet(info_eeg)

        # 2.2.6 Read incoming data and push to LSL stream
        while True:
            data = board.get_board_data() # this gets data continiously

            # don't send empty data
            if len(data[0]) < 1 : continue
            
            eeg_data = data[eeg_chan]
            aux_data = data[aux_chan]
            #print(eeg_data)
            #print(aux_data)

            # push eeg data to LSL stream
            eegchunk = []
            for i in range(len(eeg_data[0])):
                eegchunk.append((eeg_data[:,i]).tolist())
            outlet_eeg.push_chunk(eegchunk)
            # push aux data to LSL stream
            auxchunk = []
            for i in range(len(aux_data[0])):
                auxchunk.append((aux_data[:,i]).tolist())
            outlet_aux.push_chunk(auxchunk)
