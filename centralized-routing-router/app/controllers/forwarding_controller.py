from app.controllers.queue_controller import QueueController
from app.controllers.routing_table_controller import RoutingTableController
from app.services.forwarding_service import ForwardingService


class ForwardingController:
    """
    Controller responsible for simulated packet forwarding decisions.

    Sprint 2:
    - Load local routing table.
    - Apply LPM using ForwardingService.

    Sprint 3:
    - Enqueue simulated packets using FIFO.
    - Apply tail drop when the queue is full.
    - Update forwarded/discarded metrics.
    """

    def __init__(self, router_name, max_queue_size=None):
        self.router_name = router_name
        self.routing_table_controller = RoutingTableController(router_name)
        self.forwarding_service = ForwardingService()
        self.queue_controller = QueueController(router_name, max_queue_size)

    def simulate_packet_forwarding(self, destination):
        """
        Simulate the forwarding decision for one packet destination.

        The packet is first inserted into the FIFO queue. If the queue is full,
        tail drop is applied. Otherwise, the packet is dequeued in FIFO order
        and forwarded/dropped according to LPM.
        """
        queue_result = self.queue_controller.enqueue_packet(destination)

        if queue_result["action"] == "DROP":
            return {
                "router_id": self.router_name,
                "routing_table_source": self.router_name,
                "queue": queue_result,
                "metrics": self.queue_controller.get_metrics(),
                "decision": {
                    "type": "FORWARDING_DECISION",
                    "action": "DROP",
                    "destination": destination,
                    "reason": "Queue is full. Tail drop applied."
                }
            }

        packet = self.queue_controller.dequeue_packet()
        destination_to_forward = packet["destination"]

        routing_table = self.routing_table_controller.get_current_routing_table()

        decision = self.forwarding_service.decide_forwarding(
            routing_table,
            destination_to_forward
        )

        if decision.get("action") == "FORWARD":
            self.queue_controller.mark_packet_forwarded()

        else:
            self.queue_controller.mark_packet_discarded()

        return {
            "router_id": self.router_name,
            "routing_table_source": routing_table.get("source_router"),
            "queue": {
                "type": "QUEUE_RESULT",
                "action": "PROCESSED",
                "policy": "FIFO",
                "packet": packet,
                "queue_size": self.queue_controller.get_queue_size()
            },
            "metrics": self.queue_controller.get_metrics(),
            "decision": decision
        }