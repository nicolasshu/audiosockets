from basesocket import ServerSocket
import pickle

class Processor(ServerSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self):
        self.bind_listen_accept(self.SERVER, self.PROCESSOR)

    def process_msg(self, msg):
        data = pickle.loads(msg)
        print(data["data"].shape)
        # TODO 
        # 1. Process data
        # 2. Save data
        # 3. Do other magic


info = "server_info.json"
server = Processor(info)
server.start()