import socket

from test_support import ControllerDatabaseTestCase

from app.network.tcp_server import TCPServer
from app.utils.constants import CONTROLLER_HOST, CONTROLLER_PORT


class TestControllerConnection(ControllerDatabaseTestCase):
    """
    Sprint 1 controller network configuration tests.

    This file does not start the infinite TCP server loop because that belongs
    to the guided/manual integration test. Here we verify that the server can
    be created using configurable host and port values.
    """

    def test_controller_host_and_port_are_loaded_from_config(self):
        self.assertIsInstance(CONTROLLER_HOST, str)
        self.assertNotEqual(CONTROLLER_HOST.strip(), "")

        self.assertIsInstance(CONTROLLER_PORT, int)
        self.assertGreater(CONTROLLER_PORT, 0)

    def test_tcp_server_can_be_created_with_configurable_address(self):
        server = TCPServer(host="127.0.0.1", port=0)

        try:
            self.assertEqual(server.host, "127.0.0.1")
            self.assertEqual(server.port, 0)
            self.assertIsInstance(server.server_socket, socket.socket)
        finally:
            server.server_socket.close()


if __name__ == "__main__":
    import unittest
    unittest.main()