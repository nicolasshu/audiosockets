#%%
import queue
import sounddevice as sd
import datetime
import time
import argparse
import numpy as np
from basesocket import ClientSocket
import logging



class RecordSocket(ClientSocket):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.connect(self.SERVER, self.PORT)
        except ConnectionRefusedError:
            
            print("Trying to connect")
            time.sleep(1)
            self.__init__(*args, **kwargs)
    def send_audio_data(self, data, fs):
        audio_data = {"node": "recorder", 
                      "data": data, 
                      "fs": fs,
                      "ts": datetime.datetime.now()
                    }
        self.send_obj(self.client, audio_data)

def queue_cb(data, frames, times, status):
    q.put(data.copy())

if __name__ == "__main__":
    # Prepare Audio Recording
    parser = argparse.ArgumentParser()
    parser.add_argument("-l","--list_devices", action="store_true",help="Show list of all devices")
    parser.add_argument('-d', '--device', type=int, default = 7, help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
    parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
    parser.add_argument('-T', '--samplingperiod', type=float, default=0.5, help='sampling period in seconds')
    args = parser.parse_args()

    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    info = "server_info.json"
    recorder = RecordSocket(info)

    interval = args.samplingperiod # seconds
    interval *= 1000
    q = queue.Queue()

    with sd.InputStream(samplerate=args.samplerate, device = args.device, channels = args.channels, callback=queue_cb):
        print('#' * 34+'\npress Ctrl+C to stop the recording\n'+'#' * 34)
        start_time = datetime.datetime.now()
        data = []
        while True:
            try:
                dt = datetime.datetime.now() - start_time
                data.append(q.get())
                if dt.microseconds/1000 >= interval:
                    start_time = datetime.datetime.now()
                    collected_audio = np.concatenate(data,axis=0)
                    data = []
                    recorder.send_audio_data(collected_audio,args.samplerate)
                    logging.info(f"Send audio data")
            except KeyboardInterrupt:
                recorder.send_text(recorder.client,recorder.DISCONNECT_MSG)
                logging.info("\nDisconnected from server")
                break
            except Exception as e:
                print(e)
