import os
import socket
import ssl


class TCPClient:
    """
    TLS-enabled TCP client used by each router to communicate with the controller.

    Sprint 3 / FR-10:
    - Connects to the controller using TLS.
    - Validates the controller certificate using server.crt.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None
        self.ssl_context = self._create_ssl_context()

    def connect(self):
        """
        Connect to the controller using TLS.
        """
        self.client_socket = self.ssl_context.wrap_socket(
            self.raw_socket,
            server_hostname="NETCORE-CA"
        )

        self.client_socket.connect((self.host, self.port))
        print(f"Connected to controller using TLS at {self.host}:{self.port}")

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
        Close the TLS socket.
        """
        if self.client_socket is not None:
            self.client_socket.close()
        else:
            self.raw_socket.close()

    def _create_ssl_context(self):
        """
        Create the SSL context used by the router.

        The router trusts the controller certificate stored in:
        certificates/server.crt
        """
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        certificate_path = os.path.join(base_path, "certificates", "server.crt")

        if not os.path.exists(certificate_path):
            raise FileNotFoundError(
                f"Controller TLS certificate not found: {certificate_path}"
            )

        context = ssl.create_default_context(cafile=certificate_path)

        return context