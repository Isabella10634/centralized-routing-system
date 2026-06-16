import json
import time

from app.controllers.metric_controller import MetricController
from app.controllers.routing_table_controller import RoutingTableController
from app.network.tcp_client import TCPClient
from app.services.message_service import MessageService
from app.services.metric_service import MetricService
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

    Sprint 3:
    - Send periodic HEARTBEAT messages.
    - Send periodic METRICS messages with queue information.
    """

    HEARTBEAT_INTERVAL_SECONDS = 5
    METRICS_INTERVAL_HEARTBEATS = 2

    def __init__(self, router_config):
        self.router_config = router_config
        self.router_name = router_config["router_name"]
        self.client = TCPClient(
            router_config["controller_host"],
            router_config["controller_port"]
        )
        self.routing_table_controller = RoutingTableController(self.router_name)
        self.metric_controller = MetricController(self.router_name)
        self.input_buffer = ""
        self.heartbeat_count = 0

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
        Listen for controller responses.

        After UPDATE_TABLE is received, the router starts sending periodic
        HEARTBEAT and METRICS messages.
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
                self._heartbeat_and_metrics_loop()
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

    def _heartbeat_and_metrics_loop(self):
        """
        Send periodic HEARTBEAT and METRICS messages to the controller.

        Stop with CTRL + C when running manual tests.
        """
        print("")
        print("Starting HEARTBEAT/METRICS loop. Press CTRL + C to stop this router.")

        try:
            while True:
                self._send_heartbeat()

                if self.heartbeat_count % self.METRICS_INTERVAL_HEARTBEATS == 0:
                    self._send_metrics()

                time.sleep(self.HEARTBEAT_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("")
            print(f"HEARTBEAT/METRICS loop stopped manually for {self.router_name}.")

    def _send_heartbeat(self):
        """
        Send one HEARTBEAT message and wait for HEARTBEAT_OK.
        """
        heartbeat_message = {
            "type": "HEARTBEAT",
            "router_id": self.router_name
        }

        heartbeat_json = json.dumps(heartbeat_message)
        self.client.send(MessageService.encode_message(heartbeat_json))

        print(f"HEARTBEAT sent by {self.router_name}.")

        response = self._receive_one_message()

        if response is None:
            raise ConnectionError("Controller closed the connection during HEARTBEAT.")

        print(f"HEARTBEAT response: {response}")

        if response.get("type") != "HEARTBEAT_OK":
            raise ConnectionError("Unexpected HEARTBEAT response received.")

        self.heartbeat_count += 1

    def _send_metrics(self):
        """
        Send one METRICS message and wait for METRICS_OK.

        Metrics follow the project document:
        - queue_size
        - packets_forwarded
        - packets_discarded
        """
        metric_snapshot = self.metric_controller.get_current_metric()

        metrics_message = MetricService.build_metrics_message(
            self.router_name,
            metric_snapshot
        )

        metrics_json = json.dumps(metrics_message)
        self.client.send(MessageService.encode_message(metrics_json))

        print(f"METRICS sent by {self.router_name}: {metrics_message}")

        response = self._receive_one_message()

        if response is None:
            raise ConnectionError("Controller closed the connection during METRICS.")

        print(f"METRICS response: {response}")

        if response.get("type") != "METRICS_OK":
            raise ConnectionError("Unexpected METRICS response received.")

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