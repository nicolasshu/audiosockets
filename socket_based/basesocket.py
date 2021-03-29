import socket
import json
import pickle
import threading

class BaseSocket:
    def __init__(self, info):
        self.load_network_info(info)

    def load_network_info(self, path):
        with open(path,"rb") as f:
            self.server_info = json.load(f)
        # self.SERVER = socket.gethostbyname(socket.gethostname())
        self.SERVER = "192.168.1.14"
        self.PORT = self.server_info["PORT"]
        self.HEADER = self.server_info["HEADER"]
        self.FORMAT = self.server_info["FORMAT"]
        self.DISCONNECT_MSG = self.server_info["DISCONNECT_MSG"]

    def send_message(self,node,msg):
        header = self.get_header(msg)
        node.send(header)
        node.sendall(msg)

        # Confirm that target received the message
        print(node.recv(self.HEADER).decode(self.FORMAT))

    def get_header(self, msg):
        msg_length = len(msg)
        header = str(msg_length).encode(self.FORMAT)
        header += b" "*(self.HEADER - len(header))
        return header
    
    def send_text(self, node, text):
        msg = text.encode(self.FORMAT)
        self.send_message(node, msg)

    def send_obj(self, node, obj):
        msg = pickle.dumps(obj)
        self.send_message(node, msg)

    def get_number_of_bytes_from_header(self, conn):
        header = conn.recv(self.HEADER)
        print(header)
        msg_n_bytes = int(header.decode(self.FORMAT))
        return msg_n_bytes

    def get_long_message(self, n_bytes, conn):
        full_msg = []
        remaining = n_bytes
        while remaining > 0:
            partial_msg = conn.recv(n_bytes)
            full_msg.append(partial_msg)
            remaining -= len(partial_msg)
        msg = b"".join(full_msg)
        return msg

    def confirm_message_received(self, conn):
        conn.send("Message received.".encode(self.FORMAT))



class ClientSocket(BaseSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self,ip,port):
        self.client.connect((ip,port))

class ServerSocket(BaseSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind_listen_accept(self, ip, port):
        self.server.bind((ip,port))
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        while True:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target = self.handle_client, args = (conn, addr))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")

            except KeyboardInterrupt:
                self.exit()
                break
            
    def exit(self):
        pass 
    
    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected")
        connected = True
        while connected:
            n_bytes = self.get_number_of_bytes_from_header(conn)
            if n_bytes:
                msg = self.get_long_message(n_bytes, conn)
                if msg == self.DISCONNECT_MSG.encode(self.FORMAT):
                    conn.send("Disconnected\n".encode(self.FORMAT))
                    break
                self.process_msg(msg)
                self.confirm_message_received(conn)
        conn.close()


    def process_msg(self,msg):
        return msg