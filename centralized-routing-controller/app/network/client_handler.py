from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.routing_controller import RoutingController
from app.controllers.topology_controller import TopologyController
from app.services.message_service import MessageService


class ClientHandler:
    """
    Handles one TCP client connected to the controller.

    Sprint 1:
    - AUTH
    - NEIGHBORS

    Sprint 2:
    - After NEIGHBORS, the controller calculates routing tables and sends
      UPDATE_TABLE to the router that sent the topology information.
    """

    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.router_registry_controller = RouterRegistryController()
        self.topology_controller = TopologyController()
        self.routing_controller = RoutingController()
        self.input_buffer = ""

    def handle(self):
        """
        Receive and process messages from a connected router.
        """
        print(f"Client connected from {self.client_address}")

        try:
            while True:
                data = self.client_socket.recv(4096)

                if not data:
                    print(f"Client disconnected: {self.client_address}")
                    break

                self.input_buffer += MessageService.decode_message(data)
                messages, self.input_buffer = MessageService.split_messages(
                    self.input_buffer
                )

                for raw_message in messages:
                    self._process_raw_message(raw_message)

        except ConnectionAbortedError:
            print(f"Connection aborted by client: {self.client_address}")

        except ConnectionResetError:
            print(f"Connection reset by client: {self.client_address}")

        finally:
            self.client_socket.close()

    def _process_raw_message(self, raw_message):
        """
        Parse one raw JSON message and route it to the correct handler.
        """
        if raw_message.strip() == "":
            return

        print(f"Raw message received: {raw_message}")

        try:
            parsed_message = MessageService.parse_json(raw_message)
            print(f"Parsed JSON message: {parsed_message}")

            message_type = parsed_message.get("type")

            if message_type == "AUTH":
                self._handle_auth(parsed_message)

            elif message_type == "NEIGHBORS":
                self._handle_neighbors(parsed_message)

            else:
                self._send_error("Unsupported message type")

        except Exception as error:
            print(f"Error processing JSON message: {error}")
            self._send_error(str(error))

    def _handle_auth(self, parsed_message):
        """
        Handle AUTH message from a router.
        """
        response_data = self.router_registry_controller.register_router(parsed_message)
        self._send_message(response_data)

    def _handle_neighbors(self, parsed_message):
        """
        Handle NEIGHBORS message and send UPDATE_TABLE when possible.
        """
        response_data = self.topology_controller.register_neighbors(parsed_message)
        self._send_message(response_data)

        if response_data.get("type") == "NEIGHBORS_OK":
            self._send_update_table(parsed_message)

    def _send_update_table(self, parsed_message):
        """
        Calculate routing tables and send the corresponding table to this router.
        """
        router_id = parsed_message.get("router_id")

        if router_id is None:
            self._send_error("Cannot send UPDATE_TABLE because router_id is missing.")
            return

        generated_response = self.routing_controller.calculate_and_store_routing_tables()

        if generated_response.get("type") != "ROUTING_TABLES_STORED":
            self._send_message(generated_response)
            return

        routing_tables = generated_response.get("routing_tables", {})
        router_table = routing_tables.get(router_id)

        if router_table is None:
            update_message = {
                "type": "UPDATE_TABLE",
                "router_id": router_id,
                "table": {
                    "source_router": router_id,
                    "entries": []
                },
                "message": "No routing table was generated for this router."
            }
        else:
            update_message = {
                "type": "UPDATE_TABLE",
                "router_id": router_id,
                "table": router_table
            }

        self._send_message(update_message)
        print(f"UPDATE_TABLE sent to router {router_id}: {update_message}")

    def _send_error(self, message):
        """
        Send a standard ERROR response to the connected router.
        """
        error_response = {
            "type": "ERROR",
            "message": message
        }

        self._send_message(error_response)

    def _send_message(self, response_data):
        """
        Send one JSON message to the connected router.
        """
        response_bytes = MessageService.build_json_message(response_data)
        self.client_socket.sendall(response_bytes)
        print(f"Response sent: {response_data}")