import socket


class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to controller at {self.host}:{self.port}")

    def send(self, data):
        self.client_socket.sendall(data)

    def receive(self, buffer_size=1024):
        return self.client_socket.recv(buffer_size)

    def close(self):
        self.client_socket.close()