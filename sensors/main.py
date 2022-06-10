# TABLE OF CONTENT
#-----------------------------------------------
# 1     Required modules
# 2     Main method
# 2.1   Set comport to GSR, ECG, and EEG
# 2.2   Enable concurrent streaming of data
# 2.3   Start concurrent running of streams


# 1 Required modules
#--------------------
import threading
import sys
from ECG_to_LSL import ECG_to_LSL
from EEG_to_LSL import EEG_to_LSL
from GSR_to_LSL import GSR_to_LSL


# 2 Main method
#------------------
def main():
    # 2.1 Set comport to GSR, ECG, and EEG
    comX = sys.argv[1]      # GSR 
    comY = sys.argv[2]      # ECG
    comUSB = 'Com3'         # EEG

    # 2.2 Enable concurrent streaming of data
    gsr = threading.Thread(target=GSR_to_LSL, args=(comX, ))
    ecg = threading.Thread(target=ECG_to_LSL, args=(comY,))
    eeg = threading.Thread(target=EEG_to_LSL, args=(comUSB,))
    
    # 2.3 Start concurrent running of streams
    gsr.start()
    ecg.start()
    eeg.start()



if __name__ == "__main__":
    main()
