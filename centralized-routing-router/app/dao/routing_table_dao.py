import json
import os


class RoutingTableDAO:
    """
    DAO responsible for lightweight local persistence of the router routing table.

    For Sprint 2, each router stores its received routing table in a local JSON file.
    This avoids adding a local database too early and keeps the router lightweight.
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_path = os.path.join(self.base_path, "data")
        self.file_path = os.path.join(
            self.data_path,
            f"routing_table_{self.router_name}.json"
        )

    def save_routing_table(self, routing_table):
        """
        Save the routing table in a local JSON file.
        """
        os.makedirs(self.data_path, exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(routing_table, file, indent=4)

    def load_routing_table(self):
        """
        Load the routing table from local JSON storage.

        Returns:
            dict: Routing table, or an empty table if no file exists yet.
        """
        if not os.path.exists(self.file_path):
            return {
                "source_router": self.router_name,
                "entries": []
            }

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)