import os
import socket
import ssl
import threading

from app.network.client_handler import ClientHandler
from app.utils.constants import CONTROLLER_HOST, CONTROLLER_PORT


class TCPServer:
    """
    TLS-enabled TCP server used by the centralized controller.

    Sprint 3 / FR-10:
    - Uses TLS over TCP.
    - Each router connection is wrapped in an SSL context before being
      passed to ClientHandler.
    """

    def __init__(self, host=CONTROLLER_HOST, port=CONTROLLER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssl_context = None

    def start(self):
        """
        Start the TLS server and accept router connections.
        """
        self.ssl_context = self._create_ssl_context()

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Controller TLS server listening on {self.host}:{self.port}")

        while True:
            raw_client_socket, client_address = self.server_socket.accept()

            try:
                tls_client_socket = self.ssl_context.wrap_socket(
                    raw_client_socket,
                    server_side=True
                )

                handler = ClientHandler(tls_client_socket, client_address)
                client_thread = threading.Thread(target=handler.handle)
                client_thread.daemon = True
                client_thread.start()

            except ssl.SSLError as error:
                print(f"TLS handshake failed from {client_address}: {error}")
                raw_client_socket.close()

    def _create_ssl_context(self):
        """
        Create the SSL context using the local certificate and private key.
        """
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        certificate_path = os.path.join(base_path, "certificates", "server.crt")
        private_key_path = os.path.join(base_path, "certificates", "server.key")

        if not os.path.exists(certificate_path):
            raise FileNotFoundError(
                f"TLS certificate not found: {certificate_path}"
            )

        if not os.path.exists(private_key_path):
            raise FileNotFoundError(
                f"TLS private key not found: {private_key_path}"
            )

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            certfile=certificate_path,
            keyfile=private_key_path
        )

        return context