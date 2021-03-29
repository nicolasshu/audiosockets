#%%
import queue
import sounddevice as sd
import datetime
import time
import numpy as np
import pickle
from basesocket import ClientSocket
import logging


class BaseProcessor(ClientSocket):
    def __init__(self, name, *args,**kwargs):
        # Initialize a processor socket
        super().__init__(*args, **kwargs)
        # Establish the name of the processor
        self.name = name
        try:
            # Try to connect to the server
            self.connect(self.SERVER, self.PORT)
        except ConnectionRefusedError:
            # If you can't connect, keep trying every second
            print("Trying to connect")
            time.sleep(1)
            self.__init__(*args, **kwargs)

    def start(self):
        # Create a base object to identify yourself
        start_obj = {"node": "processor", "name": self.name}

        # Send the object to the server
        self.send_obj(self.client, start_obj)

        while True:
            try:
                # Obtain the header message and determine the number of bytes 
                # of the object that is being sent
                n_bytes = self.get_number_of_bytes_from_header(self.client)
                if n_bytes:
                    # If you have a non-zero byte object coming, 
                    # parse the full serialized message
                    msg = self.get_long_message(n_bytes, self.client)

                    # Compile the serialized message
                    data = pickle.loads(msg)
                    logging.debug(f"Received data of shape {data['data'].shape}")

                    # Process the data in whichever way you prefer
                    self.process_data(data)

            except KeyboardInterrupt:
                # If you wish to disconnect, send a disconnecting 
                # message to the server
                self.send_text(self.client,self.DISCONNECT_MSG)
                logging.info("Disconnected from server")
                break

    def process_data(self,data):
        # Inherit and then do something new here!
        print(data)

if __name__ == "__main__":
    info = "server_info.json"
    processor = BaseProcessor(info)
    processor.start()