from datetime import datetime

from app.dao.router_dao import RouterDAO
from app.dao.topology_dao import TopologyDAO
from app.dao.log_dao import LogDAO
from app.utils.constants import (
    LINK_STATUS_ACTIVE,
    EVENT_TYPE_TOPOLOGY_UPDATE,
    EVENT_TYPE_ERROR
)


class TopologyController:
    # Controlador encargado de procesar el mensaje NEIGHBORS.
    def __init__(self):
        self.router_dao = RouterDAO()
        self.topology_dao = TopologyDAO()
        self.log_dao = LogDAO()

    def register_neighbors(self, message_data):
        required_fields = ["router_id", "neighbors"]

        for field in required_fields:
            if field not in message_data:
                self.log_dao.insert_event(
                    EVENT_TYPE_ERROR,
                    f"NEIGHBORS inválido: falta el campo {field}",
                    datetime.now()
                )
                return {
                    "type": "ERROR",
                    "message": f"Missing field: {field}"
                }

        router_name = message_data["router_id"]
        neighbors = message_data["neighbors"]

        origin_router = self.router_dao.get_router_by_name(router_name)

        if not origin_router:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Router origen no encontrado: {router_name}",
                datetime.now()
            )
            return {
                "type": "ERROR",
                "message": f"Router {router_name} not registered"
            }

        origin_router_id = origin_router["id"]

        # Por cada vecino, se busca el router destino y se guarda el enlace.
        for neighbor in neighbors:
            neighbor_name = neighbor["neighbor_id"]
            cost = neighbor["cost"]

            destination_router = self.router_dao.get_router_by_name(neighbor_name)

            if destination_router:
                destination_router_id = destination_router["id"]
                self.topology_dao.save_link(
                    origin_router_id,
                    destination_router_id,
                    cost,
                    LINK_STATUS_ACTIVE
                )

        self.log_dao.insert_event(
            EVENT_TYPE_TOPOLOGY_UPDATE,
            f"Topología actualizada para router {router_name}",
            datetime.now()
        )

        return {
            "type": "NEIGHBORS_OK",
            "router_id": router_name,
            "message": "Neighbors stored successfully"
        }