from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.topology_controller import TopologyController
from app.services.message_service import MessageService


class ClientHandler:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.router_registry_controller = RouterRegistryController()
        self.topology_controller = TopologyController()

    def handle(self):
        print(f"Client connected from {self.client_address}")

        try:
            while True:
                data = self.client_socket.recv(1024)

                if not data:
                    print(f"Client disconnected: {self.client_address}")
                    break

                decoded_message = MessageService.decode_message(data)
                print(f"Raw message received: {decoded_message}")

                try:
                    parsed_message = MessageService.parse_json(decoded_message)
                    print(f"Parsed JSON message: {parsed_message}")

                    message_type = parsed_message.get("type")

                    if message_type == "AUTH":
                        response_data = self.router_registry_controller.register_router(parsed_message)
                        response_bytes = MessageService.build_json_message(response_data)
                        self.client_socket.sendall(response_bytes)
                        print(f"Response sent: {response_data}")

                    elif message_type == "NEIGHBORS":
                        response_data = self.topology_controller.register_neighbors(parsed_message)
                        response_bytes = MessageService.build_json_message(response_data)
                        self.client_socket.sendall(response_bytes)
                        print(f"Response sent: {response_data}")

                    else:
                        error_response = {
                            "type": "ERROR",
                            "message": "Unsupported message type"
                        }
                        self.client_socket.sendall(MessageService.build_json_message(error_response))
                        print(f"Response sent: {error_response}")

                except Exception as error:
                    print(f"Error parsing JSON message: {error}")

        except ConnectionAbortedError:
            print(f"Connection aborted by client: {self.client_address}")

        except ConnectionResetError:
            print(f"Connection reset by client: {self.client_address}")

        finally:
            self.client_socket.close()