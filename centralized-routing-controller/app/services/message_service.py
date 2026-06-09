import json


class MessageService:
    """
    Service for encoding and decoding JSON messages exchanged through TCP.

    Messages are encoded as UTF-8 JSON followed by a newline character.
    The newline works as a safe delimiter for TCP streams.
    """

    MESSAGE_DELIMITER = "\n"

    @staticmethod
    def decode_message(data):
        """
        Decode raw bytes into a UTF-8 string.
        """
        return data.decode("utf-8")

    @staticmethod
    def parse_json(message):
        """
        Parse one JSON message string into a Python dictionary.
        """
        clean_message = message.strip()

        return json.loads(clean_message)

    @staticmethod
    def build_json_message(data):
        """
        Build a JSON TCP message using newline as delimiter.
        """
        return (json.dumps(data) + MessageService.MESSAGE_DELIMITER).encode("utf-8")

    @staticmethod
    def split_messages(buffer):
        """
        Split a text buffer into complete JSON messages and remaining partial data.

        Returns:
            tuple: (complete_messages, remaining_buffer)
        """
        parts = buffer.split(MessageService.MESSAGE_DELIMITER)

        complete_messages = parts[:-1]
        remaining_buffer = parts[-1]

        return complete_messages, remaining_buffer