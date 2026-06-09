from app.controllers.routing_table_controller import RoutingTableController
from app.services.forwarding_service import ForwardingService


class ForwardingController:
    """
    Controller responsible for simulated packet forwarding decisions.

    It loads the local routing table of the router and asks ForwardingService
    to decide whether the packet must be forwarded or dropped.
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.routing_table_controller = RoutingTableController(router_name)
        self.forwarding_service = ForwardingService()

    def simulate_packet_forwarding(self, destination):
        """
        Simulate the forwarding decision for one packet destination.

        Args:
            destination (str): Simulated packet destination.

        Returns:
            dict: Forwarding decision.
        """
        routing_table = self.routing_table_controller.get_current_routing_table()

        decision = self.forwarding_service.decide_forwarding(
            routing_table,
            destination
        )

        return {
            "router_id": self.router_name,
            "routing_table_source": routing_table.get("source_router"),
            "decision": decision
        }