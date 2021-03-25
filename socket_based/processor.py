import socket
import json
import threading
import pickle

with open("server_info.json","rb") as f:
    server_info = json.load(f)

SERVER = socket.gethostbyname(socket.gethostname())
PROCESSOR = server_info["PROCESSOR"]
HEADER = server_info["HEADER"]
FORMAT = server_info["FORMAT"]
PROC_ADDR = (SERVER, PROCESSOR)
DISCONNECT_MSG = server_info["DISCONNECT_MSG"]

def handle_client(conn,addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    with conn:
        while connected:
            msg_n_bytes = int(conn.recv(HEADER).decode(FORMAT))
            rest = msg_n_bytes
            if msg_n_bytes:
                all_msg = []
                while rest > 0:
                    msg = conn.recv(msg_n_bytes)
                    all_msg.append(msg)
                    rest -= len(msg)
                msg = b"".join(all_msg)
                if msg == DISCONNECT_MSG.encode(FORMAT):
                    conn.send("Disconnected".encode(FORMAT))
                    break
                data = pickle.loads(msg)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(PROC_ADDR)
    server.listen()
    print(f"[LISTENING] Processing Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args = (conn,addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")

        except KeyboardInterrupt:
            break