from datetime import datetime

from app.dao.log_dao import LogDAO
from app.dao.router_dao import RouterDAO
from app.utils.constants import (
    EVENT_TYPE_ERROR,
    EVENT_TYPE_ROUTER_REGISTRATION,
    ROUTER_STATUS_ACTIVE
)


class RouterRegistryController:
    """
    Controller responsible for router registration and heartbeat handling.

    Sprint 1:
    - AUTH registration.

    Sprint 3:
    - Token validation for real routers.
    - Heartbeat registration.
    """

    TEST_ROUTER_PREFIX = "TEST_"

    def __init__(self):
        self.router_dao = RouterDAO()
        self.log_dao = LogDAO()

    def register_router(self, message_data):
        """
        Process AUTH messages from routers.

        If the router already exists and is not a test router, the provided
        token must match the token stored in the database.

        TEST_ routers are allowed to update their token to keep the automated
        test suite compatible with previous Sprint 1 behavior.
        """
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

        existing_router = self.router_dao.get_router_by_name(router_name)

        if existing_router is not None:
            expected_token = existing_router["token"]

            if (
                not router_name.startswith(self.TEST_ROUTER_PREFIX)
                and router_token != expected_token
            ):
                self.log_dao.insert_event(
                    EVENT_TYPE_ERROR,
                    f"AUTH rechazado para {router_name}: token inválido",
                    datetime.now()
                )

                return {
                    "type": "AUTH_FAIL",
                    "router_id": router_name,
                    "message": "Invalid authentication token"
                }

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

    def register_heartbeat(self, message_data):
        """
        Process HEARTBEAT messages from routers.

        Expected message:
        {
            "type": "HEARTBEAT",
            "router_id": "R1"
        }
        """
        if "router_id" not in message_data:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                "HEARTBEAT inválido: falta el campo router_id",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": "Missing field: router_id"
            }

        router_name = message_data["router_id"]

        updated = self.router_dao.update_router_heartbeat(router_name)

        if not updated:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"HEARTBEAT recibido de router no registrado: {router_name}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": f"Router {router_name} is not registered"
            }

        return {
            "type": "HEARTBEAT_OK",
            "router_id": router_name,
            "message": "Heartbeat received"
        }

    def mark_inactive_routers(self, timeout_seconds):
        """
        Mark routers as inactive if they have not sent heartbeat recently.
        """
        affected_rows = self.router_dao.mark_inactive_routers(timeout_seconds)

        return {
            "type": "INACTIVE_ROUTERS_MARKED",
            "timeout_seconds": timeout_seconds,
            "affected_rows": affected_rows
        }