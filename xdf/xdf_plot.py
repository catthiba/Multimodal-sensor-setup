
import pyxdf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

fpath = '/Users/trollexperiment/Documents/cathrine/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/ecg_test2.xdf'

streams, header = pyxdf.load_xdf(fpath)

for idx, stream in enumerate(streams): 
    name = stream["info"]["name"][0]
    print(idx, name)




for stream in streams:
    
    y = np.array(stream['time_series'])
    name = stream["info"]["name"][0]
    print(name)

    if isinstance(y, list):
        print('her isinstance')

        # list of strings, draw one vertical line for each marker
        for timestamp, marker in zip(np.array(stream['time_stamps']), y):
            print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
            plt.axvline(x=timestamp)
            print(f'Marker "{marker[0]}" @ {timestamp:.2f}s')
    elif isinstance(y, np.ndarray):
        # numeric streams, draw as lines
        print('x: ', np.array(stream['time_stamps']), 'y: ', y)
        plt.plot(np.array(stream['time_stamps']), y)
    else:
        raise RuntimeError('Unknown stream format')
    
    plt.title(name)
    plt.xlabel("Time stamps")
    plt.savefig('plots/%s.png' % name )
    plt.show()