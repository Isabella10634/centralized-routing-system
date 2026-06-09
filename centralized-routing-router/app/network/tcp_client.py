import socket


class TCPClient:
    """
    Simple TCP client used by the router to communicate with the controller.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """
        Connect to the controller.
        """
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to controller at {self.host}:{self.port}")

    def send(self, data):
        """
        Send raw bytes to the controller.
        """
        self.client_socket.sendall(data)

    def receive(self, buffer_size=4096):
        """
        Receive raw bytes from the controller.
        """
        return self.client_socket.recv(buffer_size)

    def close(self):
        """
        Close the TCP socket.
        """
        self.client_socket.close()