from app.models.routing_table import RoutingTable
from app.models.routing_table_entry import RoutingTableEntry


class RoutingTableService:
    """
    Service responsible for generating routing/forwarding tables from
    Dijkstra shortest path results.

    This service does not access MySQL and does not use sockets. It only
    transforms shortest path data into routing table entries.

    Expected shortest_paths format:

    {
        "R1": {
            "R1": {"cost": 0, "path": ["R1"]},
            "R2": {"cost": 10, "path": ["R1", "R2"]},
            "R3": {"cost": 5, "path": ["R1", "R3"]}
        }
    }

    Generated routing table format:

    {
        "R1": {
            "source_router": "R1",
            "entries": [
                {
                    "source_router": "R1",
                    "destination_router": "R2",
                    "destination_prefix": "R2",
                    "prefix_length": 32,
                    "next_hop": "R2",
                    "cost": 10,
                    "path": ["R1", "R2"]
                }
            ]
        }
    }
    """

    DEFAULT_PREFIX_LENGTH = 32

    def generate_table_for_router(
        self,
        source_router,
        shortest_paths_from_source,
        router_prefixes=None,
        default_prefix_length=DEFAULT_PREFIX_LENGTH
    ):
        """
        Generate one routing table for one source router.

        Args:
            source_router (str): Router that owns the table.
            shortest_paths_from_source (dict): Dijkstra result for one source.
            router_prefixes (dict | None): Optional mapping from router name to
                destination prefix. Example: {"R2": "10.0.2.0"}.
            default_prefix_length (int): Prefix length used when no specific
                prefix length source exists yet.

        Returns:
            dict: Routing table for source_router.
        """
        self._validate_source_router(source_router)
        self._validate_shortest_paths(shortest_paths_from_source)

        if router_prefixes is None:
            router_prefixes = {}

        routing_table = RoutingTable(source_router)

        for destination_router, path_data in shortest_paths_from_source.items():
            if destination_router == source_router:
                continue

            path = path_data["path"]
            cost = path_data["cost"]

            if len(path) < 2:
                continue

            next_hop = path[1]
            destination_prefix = router_prefixes.get(
                destination_router,
                destination_router
            )

            entry = RoutingTableEntry(
                source_router=source_router,
                destination_router=destination_router,
                destination_prefix=destination_prefix,
                prefix_length=default_prefix_length,
                next_hop=next_hop,
                cost=cost,
                path=path
            )

            routing_table.add_entry(entry)

        return routing_table.to_dict()

    def generate_all_tables(
        self,
        all_shortest_paths,
        router_prefixes=None,
        default_prefix_length=DEFAULT_PREFIX_LENGTH
    ):
        """
        Generate routing tables for all routers.

        Args:
            all_shortest_paths (dict): Dijkstra result for all routers.
            router_prefixes (dict | None): Optional destination prefix mapping.
            default_prefix_length (int): Default prefix length.

        Returns:
            dict: Routing tables indexed by source router name.
        """
        if not isinstance(all_shortest_paths, dict):
            raise ValueError("All shortest paths must be a dictionary.")

        routing_tables = {}

        for source_router, shortest_paths_from_source in all_shortest_paths.items():
            routing_tables[source_router] = self.generate_table_for_router(
                source_router=source_router,
                shortest_paths_from_source=shortest_paths_from_source,
                router_prefixes=router_prefixes,
                default_prefix_length=default_prefix_length
            )

        return routing_tables

    def _validate_source_router(self, source_router):
        """
        Validate source router name.
        """
        if not isinstance(source_router, str) or source_router.strip() == "":
            raise ValueError("Source router must be a non-empty string.")

    def _validate_shortest_paths(self, shortest_paths):
        """
        Validate Dijkstra shortest path result structure.
        """
        if not isinstance(shortest_paths, dict):
            raise ValueError("Shortest paths must be a dictionary.")

        for destination_router, path_data in shortest_paths.items():
            if not isinstance(destination_router, str) or destination_router.strip() == "":
                raise ValueError("Destination router must be a non-empty string.")

            if not isinstance(path_data, dict):
                raise ValueError(
                    f"Shortest path data for {destination_router} must be a dictionary."
                )

            if "cost" not in path_data:
                raise ValueError(
                    f"Shortest path data for {destination_router} is missing cost."
                )

            if "path" not in path_data:
                raise ValueError(
                    f"Shortest path data for {destination_router} is missing path."
                )

            if not isinstance(path_data["path"], list):
                raise ValueError(
                    f"Path for {destination_router} must be a list."
                )