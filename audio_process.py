#%%

%load_ext autoreload
%autoreload 2

#%%

import argparse
import os
import h5py
import time 
import librosa 
from utils import LogMelSpectrogram
from datetime import datetime

import matplotlib.pyplot as plt

# parser = argparse.ArgumentParser()
# parser.add_argument("filename", help = "Audio file to process")
# args = parser.parse_args()
def args():
    return 0

args.filename = "20210322-173002-514922.wav"
#%%

file_id, ext = os.path.splitext(os.path.basename(args.filename))
grandfather = os.path.dirname(os.path.dirname(args.filename))

feat_file = os.path.join(grandfather, "features", file_id)+".h5"
if not os.path.exists(os.path.join(grandfather,"features")):
    os.makedirs(os.path.join(grandfather,"features"))

dt = datetime.strptime(file_id,"%Y%m%d-%H%M%S-%f")
time_dict = {"year": dt.year, 
             "month":dt.month, 
             "day":dt.day, 
             "hour":dt.hour, 
             "min":dt.minute, 
             "sec":dt.second, 
             "microsecond":dt.microsecond, 
             "timestamp":dt.timestamp()
            }
#%%
audio, fs = librosa.load(args.filename, sr = None)

logmel = LogMelSpectrogram(fs)
lms = logmel(audio)
with h5py.File(feat_file,"w") as hdf:
    logmelds = hdf.create_dataset("logmelspec", data=lms)
    for k,v in logmel.__dict__.items():
        logmelds.attrs[k] = v
    for k,v in time_dict.items():
        logmelds.attrs[k] = v


# %%
