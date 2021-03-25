from basesocket import ServerSocket
import pickle
import socket

class Mailman(ServerSocket):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add a processor
        self.processor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.processor.connect((self.SERVER, self.PROCESSOR))

        # Add more processors here 
        # ...
    def start(self):
        self.bind_listen_accept(self.SERVER, self.MAILMAN)

    def process_msg(self,msg):
        data = pickle.loads(msg)
        print(data["data"].shape, data["fs"])
        # Send message to a processor
        self.send_message(self.processor, msg)

        # Add more processors here 
        # ...
    def exit(self):
        self.send_text(self.processor,self.DISCONNECT_MSG)

info = "server_info.json"
mailman = Mailman(info)
mailman.start()