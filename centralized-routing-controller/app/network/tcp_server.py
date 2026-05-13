import socket
import threading

from app.network.client_handler import ClientHandler
from app.utils.constants import CONTROLLER_HOST, CONTROLLER_PORT


class TCPServer:
    def __init__(self, host=CONTROLLER_HOST, port=CONTROLLER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Controller server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()

            handler = ClientHandler(client_socket, client_address)
            client_thread = threading.Thread(target=handler.handle)
            client_thread.start()