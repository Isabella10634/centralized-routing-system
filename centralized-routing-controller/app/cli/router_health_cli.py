import json
import sys

from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.routing_controller import RoutingController


def main():
    """
    CLI command to verify router health, mark inactive routers and recalculate
    routing tables when a failure is detected.

    Usage:
        python -m app.cli.router_health_cli 15

    Flow:
    1. Marks as inactive every router whose ultima_actividad is older than
       timeout_seconds.
    2. If at least one router was marked inactive, recalculates routing tables
       using the active topology.
    3. Stores the recalculated routing tables in MySQL.

    This supports Sprint 3 / FR-11 / NFR-10:
    - heartbeat-based fault detection
    - router failure state update
    - route recalculation after failure
    """
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python -m app.cli.router_health_cli <timeout_seconds>")
        print("")
        print("Example:")
        print("  python -m app.cli.router_health_cli 15")
        sys.exit(1)

    try:
        timeout_seconds = int(sys.argv[1])

    except ValueError:
        print("timeout_seconds must be an integer.")
        sys.exit(1)

    if timeout_seconds <= 0:
        print("timeout_seconds must be greater than zero.")
        sys.exit(1)

    registry_controller = RouterRegistryController()
    routing_controller = RoutingController()

    health_result = registry_controller.mark_inactive_routers(timeout_seconds)

    affected_rows = int(health_result.get("affected_rows", 0))

    result = {
        "type": "ROUTER_HEALTH_CHECK_COMPLETED",
        "timeout_seconds": timeout_seconds,
        "inactive_routers_marked": affected_rows,
        "route_recalculation_triggered": False,
        "routing_result": None
    }

    if affected_rows > 0:
        routing_result = routing_controller.calculate_and_store_routing_tables()

        result["route_recalculation_triggered"] = True
        result["routing_result"] = {
            "type": routing_result.get("type"),
            "saved_entries": routing_result.get("saved_entries", 0)
        }

        if routing_result.get("type") == "ERROR":
            result["routing_result"]["message"] = routing_result.get("message")

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()