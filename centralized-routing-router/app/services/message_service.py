import json


class MessageService:
    """
    Service for building, encoding and parsing JSON messages used by the router.
    """

    MESSAGE_DELIMITER = "\n"

    @staticmethod
    def build_auth_message(router_name, router_host, router_port, router_token):
        """
        Build AUTH message.
        """
        message = {
            "type": "AUTH",
            "router_id": router_name,
            "ip": router_host,
            "port": router_port,
            "token": router_token
        }

        return json.dumps(message)

    @staticmethod
    def build_neighbors_message(router_name, neighbors):
        """
        Build NEIGHBORS message.
        """
        message = {
            "type": "NEIGHBORS",
            "router_id": router_name,
            "neighbors": neighbors
        }

        return json.dumps(message)

    @staticmethod
    def encode_message(message):
        """
        Encode one JSON message using newline as TCP delimiter.
        """
        return (message + MessageService.MESSAGE_DELIMITER).encode("utf-8")

    @staticmethod
    def decode_message(data):
        """
        Decode raw bytes into text.
        """
        return data.decode("utf-8")

    @staticmethod
    def parse_json(message):
        """
        Parse one JSON message.
        """
        return json.loads(message.strip())

    @staticmethod
    def split_messages(buffer):
        """
        Split buffered TCP text into complete messages and remaining partial data.
        """
        parts = buffer.split(MessageService.MESSAGE_DELIMITER)

        complete_messages = parts[:-1]
        remaining_buffer = parts[-1]

        return complete_messages, remaining_buffer