#%%
import queue
import sounddevice as sd
import datetime
import time
import argparse
import numpy as np
from .basesocket import ClientSocket
import logging


# Define a recording socket
class RecorderSocket(ClientSocket):
    def __init__(self, *args,**kwargs):
        """Initialize a recording socket

        Args:
            args: Arguments to be passed to ClientSocket
            kwargs" Keyword arguments to be passed to ClientSocket
        """
        # Initialize base socket
        super().__init__(*args, **kwargs)
        try:
            # Try to connect to the server
            self.connect(self.SERVER, self.PORT)

            # Prepare Audio Recording
            parser = argparse.ArgumentParser()
            parser.add_argument("-l","--list_devices", action="store_true",help="Show list of all devices")
            parser.add_argument('-d', '--device', type=int, default = 7, help='input device (numeric ID or substring)')
            parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
            parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
            parser.add_argument('-T', '--samplingperiod', type=float, default=0.5, help='sampling period in seconds')
            self.args = parser.parse_args()

            # If a sample rate is not established, obtain the 
            # sampling rate from the chosen recording device
            if self.args.samplerate is None:
                device_info = sd.query_devices(self.args.device, 'input')
                self.args.samplerate = device_info['default_samplerate']

            # Define the sampling perior of sending the data
            self.interval = self.args.samplingperiod # seconds
            self.interval *= 1000

            # Create a queue object
            self.q = queue.Queue()

        except ConnectionRefusedError:
            # If you can't connect, keep trying to connect once a second
            logging.info("Trying to connect")
            time.sleep(1)
            self.__init__(*args, **kwargs)

    def send_audio_data(self, data, fs):
        # Compile the data to be sent
        audio_data = {"node": "recorder",               # Type of the node
                      "data": data,                     # The data desired
                      "fs": fs,                         # The sampling frequency
                      "ts": datetime.datetime.now()     # The current time
                    }

        # Send the object
        self.send_obj(self.client, audio_data)

    def queue_cb(self,data, frames, times, status):
        # Put the current stream of data into a queue
        self.q.put(data.copy())

    def start(self):
        # Initialize a stream of audio
        with sd.InputStream(samplerate=self.args.samplerate, device = self.args.device, channels = self.args.channels, callback=self.queue_cb):
            print('#' * 34+'\npress Ctrl+C to stop the recording\n'+'#' * 34)
            start_time = datetime.datetime.now()

            # Initialize an accumulated list of data
            data = []
            while True:
                try:
                    # Compute the time delta
                    dt = datetime.datetime.now() - start_time

                    # Add the chunk of data collected so far to a list
                    data.append(self.q.get())

                    # For every {samplingperiod},
                    if dt.microseconds/1000 >= self.interval:
                        # Create a new start time
                        start_time = datetime.datetime.now()

                        # Compile all of the data and 
                        # reset the accumulated list of data
                        collected_audio = np.concatenate(data,axis=0)
                        data = []

                        # Send the audio data to the server
                        self.send_audio_data(collected_audio,self.args.samplerate)
                        logging.info(f"Send audio data")
                except KeyboardInterrupt:
                    # If you choose to kill the process, send a disconnecting 
                    # message to the server and break out
                    self.send_text(self.client,self.DISCONNECT_MSG)
                    logging.info("\nDisconnected from server")
                    break
                except Exception as e:
                    print(e)

if __name__ == "__main__":

    # Obtain the Network Information
    info = "server_info.json"
    recorder = RecorderSocket(info)
    recorder.start()
