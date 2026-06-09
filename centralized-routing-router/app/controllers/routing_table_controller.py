from app.dao.routing_table_dao import RoutingTableDAO


class RoutingTableController:
    """
    Controller responsible for managing the routing table received by a router.

    Sprint 2 responsibilities:
    - Receive UPDATE_TABLE payload from the controller.
    - Store the table locally.
    - Provide access to the current local table.
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.routing_table_dao = RoutingTableDAO(router_name)

    def apply_update_table_message(self, message):
        """
        Apply an UPDATE_TABLE message received from the controller.

        Args:
            message (dict): UPDATE_TABLE message.

        Returns:
            dict: Standard result message.
        """
        if message.get("type") != "UPDATE_TABLE":
            return {
                "type": "ERROR",
                "message": "Invalid message type for routing table update."
            }

        if message.get("router_id") != self.router_name:
            return {
                "type": "ERROR",
                "message": (
                    f"UPDATE_TABLE is for router {message.get('router_id')}, "
                    f"not for {self.router_name}."
                )
            }

        table = message.get("table")

        if not isinstance(table, dict):
            return {
                "type": "ERROR",
                "message": "UPDATE_TABLE message does not contain a valid table."
            }

        if "source_router" not in table:
            return {
                "type": "ERROR",
                "message": "Routing table is missing source_router."
            }

        if "entries" not in table:
            return {
                "type": "ERROR",
                "message": "Routing table is missing entries."
            }

        self.routing_table_dao.save_routing_table(table)

        return {
            "type": "UPDATE_TABLE_OK",
            "router_id": self.router_name,
            "entries": len(table["entries"])
        }

    def get_current_routing_table(self):
        """
        Return the locally stored routing table.
        """
        return self.routing_table_dao.load_routing_table()