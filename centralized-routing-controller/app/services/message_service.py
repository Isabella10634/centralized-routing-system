import json


class MessageService:
    # Servicio simple para codificar y decodificar mensajes JSON.
    @staticmethod
    def decode_message(data):
        return data.decode("utf-8")

    @staticmethod
    def parse_json(message):
        return json.loads(message)

    @staticmethod
    def build_json_message(data):
        return json.dumps(data).encode("utf-8")