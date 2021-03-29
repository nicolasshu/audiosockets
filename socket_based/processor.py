#%%
import queue
import sounddevice as sd
import datetime
import time
import numpy as np
import pickle
from basesocket import ClientSocket

class ProcessorSocket(ClientSocket):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.connect(self.SERVER, self.PORT)
        except ConnectionRefusedError:
            
            print("Trying to connect")
            time.sleep(1)
            self.__init__(*args, **kwargs)

    def start(self):
        start_obj = {"node": "processor", "name": "VAD"}
        self.send_obj(self.client, start_obj)
        c = 0
        while True:
            try:
                n_bytes = self.get_number_of_bytes_from_header(self.client)
                if n_bytes:
                    msg = self.get_long_message(n_bytes, self.client)
                    data = pickle.loads(msg)
                    print(data)
                # self.confirm_message_received(self.client)
                print(datetime.datetime.now())
            except KeyboardInterrupt:
                
                self.send_text(self.client,self.DISCONNECT_MSG)
                print("Disconnected")
                break

if __name__ == "__main__":
    info = "server_info.json"
    processor = ProcessorSocket(info)
    processor.start()