import json
import sys

from app.controllers.routing_controller import RoutingController
from app.controllers.topology_controller import TopologyController


def main():
    """
    CLI command for Sprint 3 link cost update.

    Usage:
        python -m app.cli.link_cost_cli R1 R2 3

    This command:
    - Updates the cost of link R1 -> R2.
    - Recalculates routing tables.
    - Stores updated routes in MySQL.
    """
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python -m app.cli.link_cost_cli <origin_router> <destination_router> <new_cost>")
        print("")
        print("Example:")
        print("  python -m app.cli.link_cost_cli R1 R2 3")
        sys.exit(1)

    origin_router = sys.argv[1]
    destination_router = sys.argv[2]
    new_cost = sys.argv[3]

    topology_controller = TopologyController()
    routing_controller = RoutingController()

    update_result = topology_controller.update_link_cost(
        origin_router,
        destination_router,
        new_cost
    )

    print("")
    print("Link cost update result:")
    print(json.dumps(update_result, indent=4))

    if update_result.get("type") != "LINK_COST_UPDATED":
        sys.exit(1)

    recalculation_result = routing_controller.calculate_and_store_routing_tables()

    print("")
    print("Routing recalculation result:")
    print(json.dumps(recalculation_result, indent=4, default=str))

    if recalculation_result.get("type") != "ROUTING_TABLES_STORED":
        sys.exit(1)

    print("")
    print("Link cost updated and routing tables recalculated successfully.")


if __name__ == "__main__":
    main()