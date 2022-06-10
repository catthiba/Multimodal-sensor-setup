# For pretty printing XDF stream info
import json
import pprint

import pyxdf
import numpy as np
import pandas as pd



# Import XDF file
# This can be done iteratively by looping through files in  folder with e.g. glob
#fpath = '/home/cathrine/Documents/master/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/psycopy_only.xdf'
#fpath = '/home/cathrine/Documents/master/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/kate_psychopy_short_successfull_withiut_ecg.xdf'
#fpath = '/home/cathrine/Documents/master/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/martin_psychopy_short.xdf'
#fpath = '/Users/trollexperiment/Documents/cathrine/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/eeg_test1.xdf'
fpath = '/home/cathrine/Documents/master/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/ecg21.xdf'
outpath = 'ecg21.csv'

streams, fileheader = pyxdf.load_xdf(fpath)
print("Found {} streams:".format(len(streams)))
for idx, stream in enumerate(streams): 
    name = stream["info"]["name"][0]
    print(idx, name)

# Set to true to view streams in console
flag_pprint = False
#streams.pop(4) - pupil capture
#streams.pop(4) - nirstar triggers



# Extract labels and all channel data for each stream. Assuming each channel has label metadata.
for stream in streams:
    name = stream['info']['name'][0]
    print(f'Stream name: {name}')
    

    # Pretty print channel info and stream info
    if flag_pprint:
        pprint.pprint(json.loads(json.dumps(stream['info']['desc'][0]['channels'][0]['channel'])))
        pprint.pprint(json.loads(json.dumps(stream['info'])))
    
    #print('info:', stream['info']) 
    print('annet: ', stream['info']['channels'], stream['info']['sample_rate'], stream['info']['datatype'], stream['info']['streamType'])

    # Extract all labels
    labels = [ch['label'][0] for ch in stream['info']['desc'][0]['channels'][0]['channel']]
    print('labels:', labels)
    # Generate data as dictionary with label as key
    data = {labels[i]: np.asarray(stream['time_series'])[:,i] for i in range(len(labels))}
    print('data: ', data)
    data['timestamp'] = stream['time_stamps']
    print('data: ', data)


    # Convert to Pandas dataframe
    df = pd.DataFrame(data)

    # Export to csv
    df.to_csv(f"{name}_{outpath}", index=False)