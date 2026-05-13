import json

from app.network.tcp_client import TCPClient
from app.services.message_service import MessageService


class ControllerConnection:
    def __init__(self, router_config):
        self.router_config = router_config
        self.client = TCPClient(
            router_config["controller_host"],
            router_config["controller_port"]
        )

    def start(self):
        self.client.connect()

        auth_message = MessageService.build_auth_message(
            self.router_config["router_name"],
            self.router_config["router_host"],
            self.router_config["router_port"],
            self.router_config["router_token"]
        )

        self.client.send(MessageService.encode_message(auth_message))
        print("AUTH message sent to controller.")

        response = self.client.receive()
        decoded_response = response.decode("utf-8")
        parsed_response = json.loads(decoded_response)

        print(f"Response from controller: {parsed_response}")

        if parsed_response.get("type") == "AUTH_OK":
            neighbors_message = MessageService.build_neighbors_message(
                self.router_config["router_name"],
                self.router_config["neighbors"]
            )
            self.client.send(MessageService.encode_message(neighbors_message))
            print("NEIGHBORS message sent to controller.")

        self.client.close()