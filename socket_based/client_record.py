import queue
import sounddevice as sd
import datetime
import matplotlib.pyplot as plt 
import numpy as np
import socket
import json
import argparse
import pickle

# Prepare Client Socket
with open("server_info.json","rb") as f:
    server_info = json.load(f)
SERVER = socket.gethostbyname(socket.gethostname())
MAILMAN = server_info["MAILMAN"]
ADDR = (SERVER, MAILMAN)
HEADER = server_info["HEADER"]
FORMAT = server_info["FORMAT"]
DISCONNECT_MSG = server_info["DISCONNECT_MSG"]

# Prepare Audio Recording
parser = argparse.ArgumentParser()
parser.add_argument("-l","--list_devices", action="store_true",help="Show list of all devices")
parser.add_argument('-d', '--device', type=int, default = 7, help='input device (numeric ID or substring)')
parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
args = parser.parse_args()

if args.samplerate is None:
    device_info = sd.query_devices(args.device, 'input')
    args.samplerate = device_info['default_samplerate']

q = queue.Queue()

interval = 2 # seconds

def send_message(client,msg):
    # print("get-header")
    header = get_header(msg)
    # print('send-header')
    client.send(header)
    # print('send-msg')
    client.sendall(msg)
    # print('sent-msg')
    print(client.recv(HEADER).decode(FORMAT))

def send_audio_data(client,data,fs):
    # print('send-audio-data')
    audio_data = {"node": "recorder", "data": data, "fs": fs}
    msg = pickle.dumps(audio_data)
    send_message(client,msg)

def send_text(client,text):
    msg = text.encode(FORMAT)
    send_message(client,msg)

def get_header(msg):
    msg_length = len(msg)
    header = str(msg_length).encode(FORMAT)
    header += b" "*(HEADER - len(header))
    return header

def queue_cb(data, frames, times, status):
    q.put(data.copy())

with sd.InputStream(samplerate=args.samplerate, device = args.device, channels = args.channels, callback=queue_cb):
    print('#' * 80+'\npress Ctrl+C to stop the recording\n'+'#' * 80)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)
        
        start_time = datetime.datetime.now()
        data = []
        while True:
            try:
                dt = datetime.datetime.now() - start_time
                data.append(q.get())
                if dt.seconds >= interval:
                    start_time = datetime.datetime.now()
                    collected_audio = np.concatenate(data,axis=0)
                    data = []
                    send_audio_data(client,collected_audio,args.samplerate)
                    # raise KeyboardInterrupt
            except KeyboardInterrupt:
                send_text(client,DISCONNECT_MSG)
                break
            except Exception as e:
                print(e)