#%%
import json
import socket
import pickle
import threading
from basesocket import ServerSocket
import logging

class Mailman(ServerSocket):
    def __init__(self, *args, **kwargs):
        # Initialize a server socket
        super().__init__(*args,**kwargs)

        # Create a dictionary which will map name of processors to the socket 
        # of the processor sockets
        self.processors = {}

    def start(self):
        # Bind, listen, and accept new connections
        self.bind_listen_accept(self.SERVER, self.PORT)
        # Here, every new connection will be handled in a different thread via 
        # the handle_client() method. By default, it will treat every new 
        # connection as an equal client. Instead, we will treat different 
        # clients differently (i.e. recorders and processors)
        

    def handle_client(self, conn, addr):
        # Start handling this new client
        logging.debug(f"A new connection appeared from {addr}")
        connected = True
        data = {}
        while connected:
            # Obtain the header, and determine the number of bytes of the 
            # incoming data message
            n_bytes = self.get_number_of_bytes_from_header(conn)
            if n_bytes:
                # If you have a non-zero byte object coming,
                # parse the full serialized message
                msg = self.get_long_message(n_bytes, conn)

                # If the message is a disconnecting message,
                if msg == self.DISCONNECT_MSG.encode(self.FORMAT):
                    logging.info(f"Disconnecting from {addr}")
                    
                    # If we have a "name" key in the data that has been 
                    # previously parsed, then it must be a processor
                    if "name" in data:
                        # Remove the processor from the list of processors
                        del self.processors[data["name"]]
                        logging.debug(f"Removing {data['name']} from list of processors")
                        logging.debug(f"Now there are {len(self.processors)} processors")

                    # Send back a message saying that you're disconnected
                    conn.send("Disconnected\n".encode(self.FORMAT))

                    # Close the connection and break out of the loop
                    conn.close()
                    break
                
                # If it is not a disconnecting message, parse the serialized 
                # pickled message into a Python data structure
                data = pickle.loads(msg)
                logging.debug("Serialized the data")

                # If this client/node is a proper node,
                logging.debug("Checking whether client is accepted")
                if "node" in data.keys():
                    # Yay! This is a proper node
                    logging.debug("Client has been accepted")

                    if data["node"] == "recorder":
                        # If this node is a recorder
                        logging.debug("Client is a recorder")

                        # Send a confirming message back to the recorder
                        logging.debug("Confirming to client that a message was received")
                        self.confirm_message_received(conn)

                        # Send the data to every processor associated with the server
                        logging.debug("Sending data to every current processor")
                        for proc_name, proc_conn in self.processors.items():
                            # Serialize your data to a message
                            logging.debug(f"Sending data to {proc_name}")
                            msg = pickle.dumps(data)
                            header = self.get_header(msg)

                            # Send the size of the data
                            proc_conn.send(header)

                            # Send the message itself
                            proc_conn.sendall(msg)
                            logging.debug(f"Sent data to {proc_name}")
                    
                    elif data["node"] == "processor":
                        # If this node is a processor, add this processor to 
                        # the list of processors associated with the server
                        logging.info(f"New client is a processor. Adding {data['name']} to list of processors")
                        self.processors[data["name"]] = conn

                        # Confirm back that the client socket has been connected
                        logging.info(f"Now there are {len(self.processors)} processors")
                        conn.send("Connection has been established".encode(self.FORMAT))
                        logging.debug(f"Sent {data['name']} a confirmation message")

                else:
                    # If the client is not a proper node, send a notification 
                    # back stating that the client has not been properly set up
                    logging.info(f"The connection from {addr} is not a proper node. Sending message back warning the user")
                    conn.send("Whoops not a node.".encode(self.FORMAT))
            
            logging.info(f"There are currently {threading.activeCount()-1} active connections")
            logging.info(f"There are currently {len(self.processors)} processors")

if __name__ == "__main__":
    server = Mailman("server_info.json")
    server.start()
