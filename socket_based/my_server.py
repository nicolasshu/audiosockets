#%%
import json
import socket
import pickle
import threading
from basesocket import ServerSocket
import logging
#%%

config = "%(asctime)s - %(message)s"
logging.basicConfig(format=config, level=logging.DEBUG)

class Mailman(ServerSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.processors = {}

    def start(self):
        self.bind_listen_accept(self.SERVER, self.PORT)


    def handle_client(self, conn, addr):
        logging.debug(f"A new connection appeared from {addr}")
        connected = True
        data = {}
        while connected:
            n_bytes = self.get_number_of_bytes_from_header(conn)
            if n_bytes:
                msg = self.get_long_message(n_bytes, conn)
                if msg == self.DISCONNECT_MSG.encode(self.FORMAT):
                    logging.info(f"Disconnecting from {addr}")
                    if "name" in data:
                        del self.processors[data["name"]]
                        logging.debug(f"Removing {data['name']} from list of processors")
                        logging.debug(f"Now there are {len(self.processors)} processors")
                    conn.send("Disconnected\n".encode(self.FORMAT))
                    conn.close()
                    break
                
                data = pickle.loads(msg)
                logging.debug("Serialized the data")

                logging.debug("Checking whether client is accepted")
                if "node" in data.keys():
                    logging.debug("Client has been accepted")
                    if data["node"] == "recorder":
                        logging.debug("Client is a recorder")
                        logging.debug("Confirming to client that a message was received")
                        self.confirm_message_received(conn)
                        logging.debug("Sending data to every current processor")
                        for proc_name, proc_conn in self.processors.items():
                            logging.debug(f"Sending data to {proc_name}")
                            msg = pickle.dumps(data)
                            header = self.get_header(msg)
                            proc_conn.send(header)
                            proc_conn.sendall(msg)
                            logging.debug(f"Sent data to {proc_name}")
                    if data["node"] == "processor":
                        logging.info(f"New client is a processor. Adding {data['name']} to list of processors")
                        self.processors[data["name"]] = conn
                        logging.info(f"Now there are {len(self.processors)} processors")
                        conn.send("Connection has been established".encode(self.FORMAT))
                        logging.debug(f"Sent {data['name']} a confirmation message")

                else:
                    logging.info(f"The connection from {addr} is not a proper node. Sending message back warning the user")
                    conn.send("Whoops not a node.".encode(self.FORMAT))
            
            logging.info(f"There are currently {threading.activeCount()-1} active connections")
            logging.info(f"There are currently {len(self.processors)} processors")

server = Mailman("server_info.json")
server.start()

# Receive all of the connections

# If a connection is a recorder set it elsewhere, but it connection is 
# a processor, then save it to a list


# Keep receiving connections
# If receive connections, send it to a thread:
    # Identify the type of connection
    # If connection is a processor, save it to a location in memory
    # If the connection is a recorder, process it as before
    

# connection_proc
# Save this connection to a location in memory. Don't close it

# connection_recorder
# While connected

