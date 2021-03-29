import socket
import threading
import json
import pickle
from datetime import datetime

with open("server_info.json","rb") as f:
    server_info = json.load(f)

SERVER = socket.gethostbyname(socket.gethostname())
MAILMAN = server_info["MAILMAN"]
PROCESSOR = server_info["PROCESSOR"]
HEADER = server_info["HEADER"]
FORMAT = server_info["FORMAT"]
DISCONNECT_MSG = server_info["DISCONNECT_MSG"]
MAIL_ADDR   = (SERVER, MAILMAN)
PROC_ADDR   = (SERVER, PROCESSOR)

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
                print(datetime.now(),data["data"].shape)
                if data["node"] == "recorder":
                    send_to_processor(msg)
                conn.send("Message received.".encode(FORMAT))

def send_to_processor(msg):
    global proc
    msg_length = len(msg)
    header = str(msg_length).encode(FORMAT)
    header += b" "*(HEADER-len(header))
    proc.send(header)
    proc.send(msg)

def send_message(client,msg):
    header = get_header(msg)
    client.send(header)
    client.sendall(msg)
    print(client.recv(HEADER).decode(FORMAT))
def get_header(msg):
    msg_length = len(msg)
    header = str(msg_length).encode(FORMAT)
    header += b" "*(HEADER - len(header))
    return header

def send_text(client,text):
    msg = text.encode(FORMAT)
    send_message(client,msg)

proc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proc.connect(PROC_ADDR)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(MAIL_ADDR)
server.listen()
print(f"[LISTENING] Mailman Server is listening on {SERVER}")
while True:
    try:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args = (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")

    except KeyboardInterrupt:
        send_text(proc,DISCONNECT_MSG)
        break