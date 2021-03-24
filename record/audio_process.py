#%%
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import argparse
import h5py
import librosa 
from utils import LogMelSpectrogram
from datetime import datetime
import subprocess

import tensorflow as tf
import numpy as np 
import sys
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)


from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
le.fit(["speech", "music", "noise"])


#%%
# args.filename = "/home/nickshu/gitrepos/Audio_Recording_General/data/20210322-192824-300593.wav"
# Parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("filename", help = "Audio file to process")
args = parser.parse_args()

# Obtain the path directories
file_id, ext = os.path.splitext(os.path.basename(args.filename))
parent = os.path.dirname(args.filename)

# Determine the feature destination paths
feat_file = os.path.join(parent, "features", file_id)+".h5"
if not os.path.exists(os.path.join(parent,"features")):
    os.makedirs(os.path.join(parent,"features"))

# Obtain the time characteristics
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

# Load the audio
audio, fs = librosa.load(args.filename, sr = None)

# Compute the Log Mel Spectrogram
logmel = LogMelSpectrogram(fs)
lms = logmel(audio)
lms40 = LogMelSpectrogram(fs, n_mels=40)(audio)

# Load the VAD
sys.path.append("/home/nickshu/Documents/experiments/voice_activity/saved_models/super-bird-20/1")
from model import LSTM_Attention as Model
vad_path = "/home/nickshu/Documents/experiments/voice_activity/saved_models/super-bird-20"
vad = Model(40,3)
vad.load_weights(os.path.join(vad_path,"1", "variables","variables")).expect_partial()
is_speech = vad(np.expand_dims(lms40.T,0),return_logits=False)
is_speech = str(le.inverse_transform([np.argmax(is_speech)])[0])

# Log the features
with h5py.File(feat_file,"w") as hdf:
    str_type = h5py.special_dtype(vlen=str)

    dgroup = hdf.create_group("data")
    logmelds = dgroup.create_dataset("logmelspec", data=lms)
    for k,v in logmel.__dict__.items():
        logmelds.attrs[k] = v
    
    for k,v in time_dict.items():
        dgroup.attrs[k] = v
    dgroup.attrs["sample_rate"] = fs
    
    # VAD Results
    dgroup.attrs["is_speech"] = is_speech
    dgroup.create_dataset("is_speech", data=is_speech, dtype=str_type)
# os.remove(args.filename)