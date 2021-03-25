import socket
import json

import numpy as np
import pickle

with open("server_info.json","rb") as f:
    server_info = json.load(f)

SERVER = socket.gethostbyname(socket.gethostname())
PORT = server_info["PORT"]
ADDR = (SERVER, PORT)
HEADER = server_info["HEADER"]
FORMAT = server_info["FORMAT"]

def send():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(ADDR)


        a = np.random.randn(4,2)

        # Create the data dictionary and serialize the object to a pickle format
        my_data = {"node": "some_process", "audio": a, "fs": 16000}
        pkl_serial = pickle.dumps(my_data)

        # Obtain the length of the object serialized
        msg_length = len(pkl_serial)

        # Create a header message in bytes
        header = str(msg_length).encode(FORMAT)

        # Pad the header message to have the complete number of bytes necessary
        header += b" "*(HEADER - len(header))

        # Send the number of bytes the server should expect
        client.send(header)

        # Send the data over to the server
        client.send(pkl_serial)

        print(client.recv(HEADER).decode(FORMAT))

send()
input()
send()
input()
send()