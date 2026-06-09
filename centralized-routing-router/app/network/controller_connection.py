from app.controllers.routing_table_controller import RoutingTableController
from app.network.tcp_client import TCPClient
from app.services.message_service import MessageService
from app.views.routing_table_view import RoutingTableView


class ControllerConnection:
    """
    Manages communication between one router and the controller.

    Sprint 1:
    - Send AUTH.
    - Send NEIGHBORS.

    Sprint 2:
    - Receive UPDATE_TABLE.
    - Store and display the routing table.
    """

    def __init__(self, router_config):
        self.router_config = router_config
        self.router_name = router_config["router_name"]
        self.client = TCPClient(
            router_config["controller_host"],
            router_config["controller_port"]
        )
        self.routing_table_controller = RoutingTableController(self.router_name)
        self.input_buffer = ""

    def start(self):
        """
        Execute the router communication flow.
        """
        try:
            self.client.connect()

            auth_ok = self._send_auth()

            if auth_ok:
                self._send_neighbors()
                self._listen_for_controller_messages()

        finally:
            self.client.close()

    def _send_auth(self):
        """
        Send AUTH message and wait for AUTH_OK.
        """
        auth_message = MessageService.build_auth_message(
            self.router_config["router_name"],
            self.router_config["router_host"],
            self.router_config["router_port"],
            self.router_config["router_token"]
        )

        self.client.send(MessageService.encode_message(auth_message))
        print("AUTH message sent to controller.")

        response = self._receive_one_message()

        if response is None:
            print("No AUTH response received from controller.")
            return False

        print(f"Response from controller: {response}")

        if response.get("type") == "AUTH_OK":
            return True

        print("AUTH failed. Router will stop.")
        return False

    def _send_neighbors(self):
        """
        Send NEIGHBORS message.
        """
        neighbors_message = MessageService.build_neighbors_message(
            self.router_config["router_name"],
            self.router_config["neighbors"]
        )

        self.client.send(MessageService.encode_message(neighbors_message))
        print("NEIGHBORS message sent to controller.")

    def _listen_for_controller_messages(self):
        """
        Listen for controller responses until UPDATE_TABLE is received.
        """
        while True:
            message = self._receive_one_message()

            if message is None:
                print("Controller closed the connection.")
                break

            print(f"Message from controller: {message}")

            message_type = message.get("type")

            if message_type == "NEIGHBORS_OK":
                continue

            if message_type == "UPDATE_TABLE":
                self._handle_update_table(message)
                break

            if message_type == "ERROR":
                print(f"Controller error: {message.get('message')}")
                break

    def _handle_update_table(self, message):
        """
        Store and display UPDATE_TABLE received from controller.
        """
        result = self.routing_table_controller.apply_update_table_message(message)
        print(f"Routing table update result: {result}")

        if result.get("type") == "UPDATE_TABLE_OK":
            routing_table = self.routing_table_controller.get_current_routing_table()
            RoutingTableView.display(routing_table)

    def _receive_one_message(self):
        """
        Receive one complete newline-delimited JSON message.
        """
        while True:
            messages, self.input_buffer = MessageService.split_messages(
                self.input_buffer
            )

            if messages:
                raw_message = messages[0]
                remaining_messages = messages[1:]

                if remaining_messages:
                    self.input_buffer = (
                        MessageService.MESSAGE_DELIMITER.join(remaining_messages)
                        + MessageService.MESSAGE_DELIMITER
                        + self.input_buffer
                    )

                return MessageService.parse_json(raw_message)

            data = self.client.receive()

            if not data:
                return None

            self.input_buffer += MessageService.decode_message(data)