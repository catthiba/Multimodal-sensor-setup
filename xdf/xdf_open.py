from os.path import abspath, join, dirname
import logging
import pyxdf
import sys

import struct
import itertools
import gzip
from xml.etree.ElementTree import fromstring
from collections import OrderedDict, defaultdict
import logging
from pathlib import Path

import numpy as np

fpath = '/home/cathrine/Documents/master/project-thesis/LabRecordings/sub-P001/ses-S001/eeg/kate_psychopy_short_successfull_withiut_ecg.xdf'


streams, fileheader = pyxdf.load_xdf(fpath)

print("Found {} streams:".format(len(streams)))
for ix, stream in enumerate(streams):
    msg = "Stream {}: {} - type {} - uid {} - shape {} at {} (effective {}) Hz"
    print(msg.format(
        ix + 1, stream['info']['name'][0],
        stream['info']['type'][0],
        stream['info']['uid'][0],
        (int(stream['info']['channel_count'][0]), len(stream['time_stamps'])),
        stream['info']['nominal_srate'][0],
        stream['info']['effective_srate'])
    )
    if any(stream['time_stamps']):
        
        duration = stream['time_stamps'][-1] - stream['time_stamps'][0]
        
        #print('streaminfo: ', stream['time_stamps'][0])
        print("\tDuration: {} s".format(duration))
print("Done.")


#print(pyxdf.load_xdf(fpath))
