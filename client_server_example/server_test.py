import socket
import threading
import json
import pickle

with open("server_info.json","rb") as f:
    server_info = json.load(f)

SERVER = socket.gethostbyname(socket.gethostname())
PORT   = server_info["PORT"]
HEADER = server_info["HEADER"]
FORMAT = server_info["FORMAT"]
ADDR   = (SERVER, PORT)

def handle_client(conn,addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    with conn:
        while connected:
            msg_n_bytes = int(conn.recv(HEADER).decode(FORMAT))
            if msg_n_bytes:
                pkl_serial = conn.recv(msg_n_bytes)
                data = pickle.loads(pkl_serial)
                print(data)
                conn.send("Message received.".encode(FORMAT))
                connected = False


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args = (conn,addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")

        except KeyboardInterrupt:
            break