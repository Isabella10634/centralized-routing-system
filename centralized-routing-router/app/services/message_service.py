import json


class MessageService:
    @staticmethod
    def build_auth_message(router_name, router_host, router_port, router_token):
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
        message = {
            "type": "NEIGHBORS",
            "router_id": router_name,
            "neighbors": neighbors
        }
        return json.dumps(message)

    @staticmethod
    def encode_message(message):
        return message.encode("utf-8")