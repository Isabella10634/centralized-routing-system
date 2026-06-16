from datetime import datetime

from app.dao.log_dao import LogDAO
from app.dao.router_dao import RouterDAO
from app.dao.topology_dao import TopologyDAO
from app.utils.constants import EVENT_TYPE_ERROR, EVENT_TYPE_TOPOLOGY_UPDATE


class TopologyController:
    """
    Controller responsible for topology management.

    Sprint 1:
    - Receive and store NEIGHBORS messages.

    Sprint 3:
    - Update link costs from administrator commands.
    """

    def __init__(self):
        self.router_dao = RouterDAO()
        self.topology_dao = TopologyDAO()
        self.log_dao = LogDAO()

    def register_neighbors(self, message):
        """
        Register neighbor information sent by a router.

        Expected message:
        {
            "type": "NEIGHBORS",
            "router_id": "R1",
            "neighbors": [
                {"neighbor_id": "R2", "cost": 10},
                {"neighbor_id": "R3", "cost": 5}
            ]
        }
        """
        try:
            required_fields = ["router_id", "neighbors"]

            for field in required_fields:
                if field not in message:
                    self.log_dao.insert_event(
                        EVENT_TYPE_ERROR,
                        f"NEIGHBORS inválido: falta el campo {field}",
                        datetime.now()
                    )

                    return {
                        "type": "ERROR",
                        "message": f"Missing field: {field}"
                    }

            router_name = message["router_id"]
            neighbors = message["neighbors"]

            if not isinstance(neighbors, list):
                self.log_dao.insert_event(
                    EVENT_TYPE_ERROR,
                    f"NEIGHBORS inválido para router {router_name}: neighbors no es una lista",
                    datetime.now()
                )

                return {
                    "type": "ERROR",
                    "message": "neighbors must be a list"
                }

            origin_router = self.router_dao.get_router_by_name(router_name)

            if origin_router is None:
                self.log_dao.insert_event(
                    EVENT_TYPE_ERROR,
                    f"Router origen no registrado: {router_name}",
                    datetime.now()
                )

                return {
                    "type": "ERROR",
                    "message": f"Origin router {router_name} is not registered"
                }

            for neighbor in neighbors:
                validation_error = self._validate_neighbor_entry(neighbor)

                if validation_error is not None:
                    self.log_dao.insert_event(
                        EVENT_TYPE_ERROR,
                        f"NEIGHBORS inválido para router {router_name}: {validation_error}",
                        datetime.now()
                    )

                    return {
                        "type": "ERROR",
                        "message": validation_error
                    }

                neighbor_name = neighbor["neighbor_id"]
                cost = neighbor["cost"]

                destination_router = self.router_dao.get_router_by_name(neighbor_name)

                if destination_router is None:
                    self.log_dao.insert_event(
                        EVENT_TYPE_ERROR,
                        f"Router vecino no registrado: {neighbor_name}",
                        datetime.now()
                    )

                    return {
                        "type": "ERROR",
                        "message": f"Neighbor router {neighbor_name} is not registered"
                    }

                self.topology_dao.save_link(
                    origin_router["id"],
                    destination_router["id"],
                    cost,
                    "activo"
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

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error registrando vecinos: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def update_link_cost(self, origin_router_name, destination_router_name, new_cost):
        """
        Update the cost of an active link using router names.

        Args:
            origin_router_name (str): Origin router name.
            destination_router_name (str): Destination router name.
            new_cost (int): New positive link cost.

        Returns:
            dict: Standard result message.
        """
        try:
            if not isinstance(origin_router_name, str) or origin_router_name.strip() == "":
                return {
                    "type": "ERROR",
                    "message": "Origin router name must be a non-empty string."
                }

            if not isinstance(destination_router_name, str) or destination_router_name.strip() == "":
                return {
                    "type": "ERROR",
                    "message": "Destination router name must be a non-empty string."
                }

            try:
                normalized_cost = int(new_cost)

            except ValueError:
                return {
                    "type": "ERROR",
                    "message": "New cost must be an integer."
                }

            if normalized_cost <= 0:
                return {
                    "type": "ERROR",
                    "message": "New cost must be greater than zero."
                }

            origin_router = self.router_dao.get_router_by_name(origin_router_name)
            destination_router = self.router_dao.get_router_by_name(destination_router_name)

            if origin_router is None:
                return {
                    "type": "ERROR",
                    "message": f"Origin router {origin_router_name} does not exist."
                }

            if destination_router is None:
                return {
                    "type": "ERROR",
                    "message": f"Destination router {destination_router_name} does not exist."
                }

            link_exists = self.topology_dao.link_exists(
                origin_router["id"],
                destination_router["id"]
            )

            if not link_exists:
                return {
                    "type": "ERROR",
                    "message": (
                        f"Link {origin_router_name} -> {destination_router_name} "
                        "does not exist."
                    )
                }

            self.topology_dao.update_link_cost(
                origin_router["id"],
                destination_router["id"],
                normalized_cost
            )

            self.log_dao.insert_event(
                EVENT_TYPE_TOPOLOGY_UPDATE,
                (
                    f"Costo actualizado para enlace "
                    f"{origin_router_name}->{destination_router_name}: {normalized_cost}"
                ),
                datetime.now()
            )

            return {
                "type": "LINK_COST_UPDATED",
                "origin_router": origin_router_name,
                "destination_router": destination_router_name,
                "new_cost": normalized_cost
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error actualizando costo de enlace: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def _validate_neighbor_entry(self, neighbor):
        """
        Validate one neighbor entry.
        """
        if not isinstance(neighbor, dict):
            return "Each neighbor must be a dictionary."

        if "neighbor_id" not in neighbor:
            return "Missing field: neighbor_id"

        if "cost" not in neighbor:
            return "Missing field: cost"

        if not isinstance(neighbor["neighbor_id"], str) or neighbor["neighbor_id"].strip() == "":
            return "neighbor_id must be a non-empty string"

        try:
            cost = int(neighbor["cost"])

        except ValueError:
            return "cost must be an integer"

        if cost <= 0:
            return "cost must be greater than zero"

        neighbor["cost"] = cost

        return None