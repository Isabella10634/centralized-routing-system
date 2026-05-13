from datetime import datetime

from app.dao.router_dao import RouterDAO
from app.dao.log_dao import LogDAO
from app.utils.constants import (
    ROUTER_STATUS_ACTIVE,
    EVENT_TYPE_ROUTER_REGISTRATION,
    EVENT_TYPE_ERROR
)


class RouterRegistryController:
    # Controlador encargado de procesar el mensaje AUTH.
    def __init__(self):
        self.router_dao = RouterDAO()
        self.log_dao = LogDAO()

    def register_router(self, message_data):
        # Validación mínima del mensaje AUTH.
        required_fields = ["router_id", "ip", "port", "token"]

        for field in required_fields:
            if field not in message_data:
                self.log_dao.insert_event(
                    EVENT_TYPE_ERROR,
                    f"AUTH inválido: falta el campo {field}",
                    datetime.now()
                )
                return {
                    "type": "AUTH_FAIL",
                    "message": f"Missing field: {field}"
                }

        router_name = message_data["router_id"]
        router_ip = message_data["ip"]
        router_port = message_data["port"]
        router_token = message_data["token"]

        # Si el router ya existe, se actualiza. Si no, se inserta.
        if self.router_dao.router_exists(router_name):
            self.router_dao.update_router_info(
                router_name,
                router_ip,
                router_port,
                router_token,
                ROUTER_STATUS_ACTIVE
            )
        else:
            self.router_dao.insert_router(
                router_name,
                router_ip,
                router_port,
                router_token,
                ROUTER_STATUS_ACTIVE
            )

        self.log_dao.insert_event(
            EVENT_TYPE_ROUTER_REGISTRATION,
            f"Router {router_name} registrado/actualizado correctamente",
            datetime.now()
        )

        return {
            "type": "AUTH_OK",
            "router_id": router_name,
            "message": "Router registered successfully"
        }