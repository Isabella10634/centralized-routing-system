import heapq
from math import inf


class DijkstraService:
    """
    Service responsible for computing shortest paths in a weighted directed graph.

    The graph format expected by this service is:

    {
        "R1": [
            {"to": "R2", "cost": 10},
            {"to": "R3", "cost": 5}
        ],
        "R2": [
            {"to": "R3", "cost": 1}
        ],
        "R3": []
    }

    This service does not access the database directly. It only receives a graph
    and returns shortest path results. This keeps the algorithm reusable,
    testable, and independent from persistence.
    """

    def compute_shortest_paths(self, graph, source):
        """
        Compute the shortest paths from one source router to all reachable routers.

        Args:
            graph (dict): Weighted directed graph.
            source (str): Source router name.

        Returns:
            dict: Dictionary with the shortest cost and path to each router.

            Example:
            {
                "R1": {"cost": 0, "path": ["R1"]},
                "R2": {"cost": 2, "path": ["R1", "R2"]},
                "R3": {"cost": 3, "path": ["R1", "R2", "R3"]}
            }
        """
        self._validate_graph(graph)
        self._validate_source(graph, source)

        distances = {router: inf for router in graph}
        previous_nodes = {router: None for router in graph}

        distances[source] = 0
        priority_queue = [(0, source)]

        while priority_queue:
            current_cost, current_router = heapq.heappop(priority_queue)

            if current_cost > distances[current_router]:
                continue

            for neighbor in graph[current_router]:
                neighbor_router = neighbor["to"]
                link_cost = neighbor["cost"]

                new_cost = current_cost + link_cost

                if new_cost < distances[neighbor_router]:
                    distances[neighbor_router] = new_cost
                    previous_nodes[neighbor_router] = current_router
                    heapq.heappush(priority_queue, (new_cost, neighbor_router))

        return self._build_shortest_path_result(distances, previous_nodes, source)

    def compute_all_shortest_paths(self, graph):
        """
        Compute shortest paths from every router to every other reachable router.

        Args:
            graph (dict): Weighted directed graph.

        Returns:
            dict: Dictionary indexed by source router.

            Example:
            {
                "R1": {
                    "R1": {"cost": 0, "path": ["R1"]},
                    "R2": {"cost": 2, "path": ["R1", "R2"]}
                },
                "R2": {
                    "R2": {"cost": 0, "path": ["R2"]}
                }
            }
        """
        self._validate_graph(graph)

        all_results = {}

        for source in graph:
            all_results[source] = self.compute_shortest_paths(graph, source)

        return all_results

    def _build_shortest_path_result(self, distances, previous_nodes, source):
        """
        Build the final result with cost and path for each reachable router.
        """
        result = {}

        for destination, cost in distances.items():
            if cost == inf:
                continue

            result[destination] = {
                "cost": cost,
                "path": self._reconstruct_path(previous_nodes, source, destination)
            }

        return result

    def _reconstruct_path(self, previous_nodes, source, destination):
        """
        Reconstruct a shortest path from source to destination.
        """
        path = []
        current_router = destination

        while current_router is not None:
            path.insert(0, current_router)

            if current_router == source:
                break

            current_router = previous_nodes[current_router]

        return path

    def _validate_graph(self, graph):
        """
        Validate the graph structure before running Dijkstra.
        """
        if not isinstance(graph, dict):
            raise ValueError("Graph must be a dictionary.")

        for router, neighbors in graph.items():
            if not isinstance(router, str) or router.strip() == "":
                raise ValueError("Each router name must be a non-empty string.")

            if not isinstance(neighbors, list):
                raise ValueError(f"Neighbors of router {router} must be a list.")

            for neighbor in neighbors:
                self._validate_neighbor(graph, router, neighbor)

    def _validate_neighbor(self, graph, router, neighbor):
        """
        Validate one neighbor entry.
        """
        if not isinstance(neighbor, dict):
            raise ValueError(f"Invalid neighbor entry in router {router}.")

        if "to" not in neighbor:
            raise ValueError(f"Neighbor entry in router {router} is missing 'to'.")

        if "cost" not in neighbor:
            raise ValueError(f"Neighbor entry in router {router} is missing 'cost'.")

        destination = neighbor["to"]
        cost = neighbor["cost"]

        if destination not in graph:
            raise ValueError(
                f"Router {router} has a link to unknown router {destination}."
            )

        if not isinstance(cost, (int, float)):
            raise ValueError(
                f"Cost from {router} to {destination} must be numeric."
            )

        if cost < 0:
            raise ValueError(
                f"Cost from {router} to {destination} cannot be negative."
            )

    def _validate_source(self, graph, source):
        """
        Validate that the source router exists in the graph.
        """
        if source not in graph:
            raise ValueError(f"Source router {source} does not exist in graph.")