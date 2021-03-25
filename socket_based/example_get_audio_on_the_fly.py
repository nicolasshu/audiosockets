import queue
import sounddevice as sd
import datetime
import matplotlib.pyplot as plt 
import numpy as np

import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-l","--list_devices", action="store_true",help="Show list of all devices")
parser.add_argument('-d', '--device', type=int, help='input device (numeric ID or substring)')
parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
args = parser.parse_args()
q = queue.Queue()

report_every = 5 # seconds

def queue_cb(data, frames, times, status):
    q.put(data.copy())

with sd.InputStream(samplerate=args.samplerate, device = args.device, channels = args.channels, callback=queue_cb):
    print('#' * 80,'\npress Ctrl+C to stop the recording\n','#' * 80)

    start_time = datetime.datetime.now()
    all_data = []
    while True:
        try:
            end_time = datetime.datetime.now()
            dt = end_time - start_time
            data = q.get()
            all_data.append(data)
            if dt.seconds >= report_every:
                my_dat = np.concatenate(all_data,axis=0)
                print(datetime.datetime.now(), my_dat.shape)
                all_data = []
                start_time = datetime.datetime.now()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)