import json
import sys

from app.controllers.routing_controller import RoutingController


def main():
    """
    CLI command to show the shortest path between two specific routers.

    Usage:
        python -m app.cli.path_cli R1 R5

    This command is useful for demonstrations because the professor can choose
    two routers and the system shows the current best path according to the
    active topology and Dijkstra's algorithm.
    """
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python -m app.cli.path_cli <source_router> <destination_router>")
        print("")
        print("Example:")
        print("  python -m app.cli.path_cli R1 R5")
        sys.exit(1)

    source_router = sys.argv[1].strip().upper()
    destination_router = sys.argv[2].strip().upper()

    routing_controller = RoutingController()

    result = routing_controller.calculate_shortest_paths_from_router(source_router)

    if result.get("type") == "ERROR":
        print(json.dumps(result, indent=4))
        sys.exit(1)

    shortest_paths = result.get("shortest_paths", {})

    if destination_router not in shortest_paths:
        response = {
            "type": "PATH_NOT_FOUND",
            "source_router": source_router,
            "destination_router": destination_router,
            "message": (
                f"No active path was found from {source_router} "
                f"to {destination_router}."
            ),
            "graph": result.get("graph", {})
        }

        print(json.dumps(response, indent=4))
        sys.exit(0)

    path_data = shortest_paths[destination_router]
    path = path_data["path"]
    cost = path_data["cost"]

    response = {
        "type": "PATH_FOUND",
        "source_router": source_router,
        "destination_router": destination_router,
        "cost": cost,
        "path": path,
        "path_text": " -> ".join(path)
    }

    print("")
    print("NETCORE - Shortest Path")
    print("=" * 60)
    print(f"Source router      : {source_router}")
    print(f"Destination router : {destination_router}")
    print(f"Total cost         : {cost}")
    print(f"Path               : {' -> '.join(path)}")
    print("=" * 60)
    print("")
    print("JSON result:")
    print(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()