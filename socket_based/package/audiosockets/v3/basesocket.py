import socket
import json
import pickle
import threading
import logging

class BaseSocket:
    """
    This is the base socket which others inherit from
    """
    def __init__(self, info):
        """Initialize the socket

        Args:
            info (str): Path to where the network information is located
        """
        # Load the network information
        self.load_network_info(info)

    def load_network_info(self, path):
        """Load the network info from a JSON file .

        Args:
            path (str): Path to where the network information is located
        """
        with open(path,"rb") as f:
            self.server_info = json.load(f)
        
        log_levels = {"debug": logging.DEBUG,
                      "info": logging.INFO,
                      "warning": logging.WARNING,
                      "error": logging.ERROR,
                      "critical": logging.CRITICAL}

        # Obtain the logging parameters
        level = self.server_info["logging_level"].lower()
        logging.basicConfig(format = self.server_info["logging_format"],
                            level = log_levels[level])
        
        # Establish the attributes to every parameter necessary
        logging.debug("Loading network info")
        self.SERVER = socket.gethostbyname(socket.gethostname())
        #self.SERVER = "192.168.1.14"
        self.PORT = self.server_info["PORT"]
        self.HEADER = self.server_info["HEADER"]
        self.FORMAT = self.server_info["FORMAT"]
        self.DISCONNECT_MSG = self.server_info["DISCONNECT_MSG"]

    def send_message(self,node,msg):
        """Send a message to a connection

        Args:
            node (socket): A socket to which to send a message
            msg (bytes str): A serialized message to send to a socket
        """
        # Obtain the header of the message which will be used to establish the
        # size of the message to be sent 
        header = self.get_header(msg)

        # Send the header containing the size of the data
        node.send(header)
        
        # Send the message itself
        node.sendall(msg)

        # Confirm that target received the message
        logging.info(node.recv(self.HEADER).decode(self.FORMAT))

    def get_header(self, msg):
        """Obtain the header for a message

        Args:
            msg (bytes str): A serialized message

        Returns:
            bytes str: A bytes string which will be the header of the message. 
                It will indicate the number of bytes that the message will 
                contain
        """
        # Obtain the length of the message
        msg_length = len(msg)

        # Create a header string to be sent
        header = str(msg_length).encode(self.FORMAT)
        header += b" "*(self.HEADER - len(header))
        return header
    
    def send_text(self, node, text):
        """Send a text to a socket

        Args:
            node (socket): A socket connection to send a text to
            text (str): A string to send to the socket
        """
        # Encode the text to the desired format
        msg = text.encode(self.FORMAT)

        # Send the text as a message
        self.send_message(node, msg)

    def send_obj(self, node, obj):
        """Send an object to a socket

        Args:
            node (socket): A socket connection to which send an object
            obj (obj): An object that can be pickled serialized 
        """
        # Serialize the object to a message
        msg = pickle.dumps(obj)

        # Send the object as a message
        self.send_message(node, msg)

    def get_number_of_bytes_from_header(self, conn):
        """Obtain the number of bytes from a header message

        Args:
            conn (socket): A socket connection to which receive a header from

        Returns:
            (int): An integer number of bytes read from the header indicating 
                the number of bytes that the message will contain
        """
        # Receive the header itself
        logging.debug("Obtaining the number of bytes for the incoming message")
        header = conn.recv(self.HEADER)

        # try:
        #     # Interpret the header to determine the number of bytes of the message
        #     msg_n_bytes = int(header.decode(self.FORMAT))
        #     logging.debug(f"The number of bytes for the incoming message is {msg_n_bytes}")

        #     return msg_n_bytes
        # except:
        #     print("This was not a n_bytes")
        #     return None

        # Interpret the header to determine the number of bytes of the message
        msg_n_bytes = int(header.decode(self.FORMAT))
        logging.debug(f"The number of bytes for the incoming message is {msg_n_bytes}")

        return msg_n_bytes

    def get_long_message(self, n_bytes, conn):
        """Return a long message from the socket. Sometimes, it is possible that
            a message being sent through a socket connection may not be complete. 
            For example, even though you set a socket to receive n_bytes, it is
            possible that, if n_bytes >> 1, then it may receive less than 
            n_bytes at a time until n_bytes has been sent. This method takes 
            care of that by looping over the receiving function of a socket 
            until one has received the full message

        Args:
            n_bytes (int): An integer number of bytes that a socket may receive
            conn (socket): A socket from which to receive a message

        Returns:
            (bytes str): A bytes string that contains the entire serialized 
                message
        """
        logging.debug("Compiling the message")
        # Initialize the list of messages and the number of expected bytes
        full_msg = []
        remaining = n_bytes

        # Loop until full message has been received
        while remaining > 0:
            # Receive the partial message and add it to your full_msg list
            partial_msg = conn.recv(n_bytes)
            full_msg.append(partial_msg)
            remaining -= len(partial_msg)

        # Compile the full message
        msg = b"".join(full_msg)
        logging.debug(f"Obtained a message with length {len(msg)}")

        # Return the full message
        return msg

    def confirm_message_received(self, conn):
        """Confirm that the message is received .

        Args:
            conn (socket): Socket connection to which send a confirmation message
        """
        # Send a confirmation message
        conn.send("Message received.".encode(self.FORMAT))



class ClientSocket(BaseSocket):
    def __init__(self, *args, **kwargs):
        """Initialize the client socket

        Args:
            args: Arguments to be passed to BaseSocket
            kwargs" Keyword arguments to be passed to BaseSocket
        """
        super().__init__(*args, **kwargs)

        # Create a client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self,ip,port):
        """Connect to a remote host located at {ip}:{port}

        Args:
            ip (str): An IP address to connect to
            port (str): A port number to connect to
        """
        # Connect the client to a server with the address {ip}:{port}
        self.client.connect((ip,port))

class ServerSocket(BaseSocket):
    def __init__(self, *args, **kwargs):
        """Create the server socket and initialize it.

        Args:
            args: Arguments to be passed to BaseSocket
            kwargs" Keyword arguments to be passed to BaseSocket
        """
        # Initialize the base socket
        super().__init__(*args, **kwargs)

        # Create a server socket
        logging.info("Creating server socket")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info("Successfully created server socket")

    def bind_listen_accept(self, ip, port):
        """Bind the socket to the address {ip}:{port}, listen for new 
            connections, accept them, and deploy them to different threads

        Args:
            ip (str): An IP address to connect to
            port (str): A port number to connect to
        """
        # Bind your socket to an address
        logging.info(f"Binding socket to {ip}:{port}")
        self.server.bind((ip,port))

        # Start listening at the port
        logging.info(f"Successfully binded the socket to {ip}:{port}")
        self.server.listen()
        logging.info(f"Server is listening to the port {ip}:{port}")

        # Continuously listen for new connections
        while True:
            try:
                # Block until receiving a new connection
                conn, addr = self.server.accept()

                # Deploy a new thread which will handle the new connection
                thread = threading.Thread(target = self.handle_client, args = (conn, addr))
                thread.start()
                logging.info(f"There are currently {threading.activeCount()-1} active connections")

            except KeyboardInterrupt:
                logging.info("\nQuitting the server")
                self.exit()
                break
            
    def exit(self):
        """Method to be overwritten in case one wishes to perform an action 
            prior to quitting the server
        """
        # 
        pass 
    
    def handle_client(self, conn, addr):
        """Handle a connection to a client .

        Args:
            conn (socket): Socket of the client
            addr (tuple): Address bound to the socket of the client
        """
        print(f"[NEW CONNECTION] {addr} connected")
        connected = True
        while connected:
            # Obtain the number of bytes that the message will contain
            n_bytes = self.get_number_of_bytes_from_header(conn)
            if n_bytes:
                # Obtain the full message
                msg = self.get_long_message(n_bytes, conn)

                # If the client has asked to disconnect, then send a 
                # confirmation message back to the client and break out of the 
                # while loop
                if msg == self.DISCONNECT_MSG.encode(self.FORMAT):
                    conn.send("Disconnected\n".encode(self.FORMAT))
                    break

                # Process the message in whichever way you prefer
                self.process_msg(msg)

                # Send a confirmation message to the client confirming that 
                # you've received the message
                self.confirm_message_received(conn)

        # Close the connection
        conn.close()

    def process_msg(self,msg):
        """Dummy method to process the message. Inherit this class and overwrite
            the method in order to do something new with it!

        Args:
            msg (bytes str): Message to process
        """
        return msg
