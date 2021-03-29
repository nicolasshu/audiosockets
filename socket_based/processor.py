import time
start = time.time()
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)
from basesocket import ServerSocket
import pickle
from utils import LogMelSpectrogram
import numpy as np
import sys
from sklearn.preprocessing import LabelEncoder

def load_model():

    le = LabelEncoder()
    le.fit(["speech", "music", "noise"])

    sys.path.append("/home/nickshu/Documents/experiments/voice_activity/saved_models/super-bird-20/1")
    from model import LSTM_Attention as Model
    vad_path = "/home/nickshu/Documents/experiments/voice_activity/saved_models/super-bird-20"
    vad = Model(40,3)
    vad.load_weights(os.path.join(vad_path,"1", "variables","variables")).expect_partial()
    return vad,le


def speech_music_noise(lms):
    global vad, le
    is_speech = vad(np.expand_dims(lms.T,0),return_logits=False)
    is_speech = str(le.inverse_transform([np.argmax(is_speech)])[0])
    return is_speech
class Processor(ServerSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self):
        self.bind_listen_accept(self.SERVER, self.PROCESSOR)

    def process_msg(self, msg):
        data = pickle.loads(msg)
        audio = data["data"]
        fs = data["fs"]
        # TODO 
        # 1. Process data
        spec,ts = LogMelSpectrogram(fs,n_mels=40)(audio, return_time=True)
        result = speech_music_noise(spec)

        # 2. Save data
        # 3. Do other magic

if __name__ == '__main__':

    vad, le = load_model()
    print("Time to load model: ", time.time()-start)
    start = time.time()

    # ~ 0.77sec
    # X = np.random.randn(40,200)
    # print(speech_music_noise(X))
    # print("Time to pass model: ", time.time()-start)
    
    info = "server_info.json"
    server = Processor(info)
    server.start()