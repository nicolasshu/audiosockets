import json
import socket
import pickle
import threading
from basesocket import ServerSocket

class Mailman(ServerSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.processors = {}

    def start(self):
        self.bind_listen_accept(self.SERVER, self.PORT)


    def handle_client(self, conn, addr):
        print("new")
        print(f"[NEW CONNECTION] {addr} connected")
        connected = True
        data = {}
        while connected:
            print("Step 1: Get number of bytes")
            n_bytes = self.get_number_of_bytes_from_header(conn)
            print(f"\tGot number of bytes: {n_bytes}")
            if n_bytes:
                print("Step 2: Get long message")
                msg = self.get_long_message(n_bytes, conn)
                print(f"\tGot long message with length {len(msg)}")
                if msg == self.DISCONNECT_MSG.encode(self.FORMAT):
                    if "name" in data:
                        del self.processors[data["name"]]
                    print("Deleted", self.processors)
                    conn.send("Disconnected\n".encode(self.FORMAT))
                    break
                print("Step 3: Pickling the data: ",end="")
                data = pickle.loads(msg)
                print("Pickled!")
                print("Step 4: Do we have a 'node' key?", end =" ")
                if "node" in data.keys():
                    print(f"Yes! It is '{data['node']}'")
                    if data["node"] == "recorder":
                        print("Step 5: Confirm to the client that we received the message")
                        # print(f"{addr}: ",data.keys())
                        self.confirm_message_received(conn)
                        # print("Sending data to procs...")
                        # print("************")
                        # print(self.processors)
                        # print("************")
                        print("Step 6: For every proc, send the data")
                        for proc_name, proc_conn in self.processors.items():
                            print(f"Step 6a: Sending data to {proc_name}")
                            msg = pickle.dumps(data)
                            header = self.get_header(msg)
                            proc_conn.send(header)
                            proc_conn.sendall(msg)
                            # print(f"\t[{proc_name}]",proc_conn.recv(self.HEADER).decode(self.FORMAT))
                            print(f"Step 6ab: Sent data to {proc_name}")
                    if data["node"] == "processor":
                        print("Step 5: A new processor. Adding it to the list")
                        self.processors[data["name"]] = conn
                        print(f"\tDone! Now we have {len(self.processors)} processors")
                        print("Step 6: Confirm to the processor that we received the message")
                        self.confirm_message_received(conn)

                else:
                    conn.send("Whoops not a node.".encode(self.FORMAT))
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1} | {len(self.processors)}")
            

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

