from app.dao.queue_dao import QueueDAO
from app.models.packet import Packet


class QueueController:
    """
    Controller responsible for FIFO queue management.

    Sprint 3 / FR-12:
    - Maintain a FIFO queue.
    - Use configurable maximum size.
    - Apply tail drop when the queue is full.
    """

    DEFAULT_MAX_QUEUE_SIZE = 5

    def __init__(self, router_name, max_queue_size=None):
        self.router_name = router_name
        self.max_queue_size = self._normalize_max_queue_size(max_queue_size)
        self.queue_dao = QueueDAO(router_name)

    def enqueue_packet(self, destination):
        """
        Add a packet to the FIFO queue.

        If the queue is full, the new packet is discarded using tail drop.
        """
        self._validate_destination(destination)

        state = self.queue_dao.load_state()
        queue = state.get("queue", [])

        if len(queue) >= self.max_queue_size:
            state["metrics"]["packets_discarded"] += 1
            self.queue_dao.save_state(state)

            return {
                "type": "QUEUE_RESULT",
                "action": "DROP",
                "policy": "TAIL_DROP",
                "reason": "Queue is full.",
                "queue_size": len(queue),
                "max_queue_size": self.max_queue_size
            }

        state["last_packet_id"] += 1

        packet = Packet(
            packet_id=state["last_packet_id"],
            router_id=self.router_name,
            destination=destination,
            status="en_cola"
        )

        queue.append(packet.to_dict())
        state["queue"] = queue
        self.queue_dao.save_state(state)

        return {
            "type": "QUEUE_RESULT",
            "action": "ENQUEUED",
            "packet": packet.to_dict(),
            "queue_size": len(queue),
            "max_queue_size": self.max_queue_size
        }

    def dequeue_packet(self):
        """
        Remove and return the oldest packet in FIFO order.
        """
        state = self.queue_dao.load_state()
        queue = state.get("queue", [])

        if not queue:
            return None

        packet = queue.pop(0)
        state["queue"] = queue
        self.queue_dao.save_state(state)

        return packet

    def mark_packet_forwarded(self):
        """
        Increment forwarded packet counter.
        """
        state = self.queue_dao.load_state()
        state["metrics"]["packets_forwarded"] += 1
        self.queue_dao.save_state(state)

    def mark_packet_discarded(self):
        """
        Increment discarded packet counter.
        """
        state = self.queue_dao.load_state()
        state["metrics"]["packets_discarded"] += 1
        self.queue_dao.save_state(state)

    def get_queue_size(self):
        """
        Return current queue size.
        """
        state = self.queue_dao.load_state()
        return len(state.get("queue", []))

    def get_metrics(self):
        """
        Return current queue metrics.
        """
        state = self.queue_dao.load_state()
        metrics = state.get("metrics", {})

        return {
            "queue_size": len(state.get("queue", [])),
            "packets_forwarded": int(metrics.get("packets_forwarded", 0)),
            "packets_discarded": int(metrics.get("packets_discarded", 0))
        }

    def reset_queue(self):
        """
        Reset queue and counters.
        """
        return self.queue_dao.reset_state()

    def _normalize_max_queue_size(self, max_queue_size):
        """
        Validate and normalize queue max size.
        """
        if max_queue_size is None:
            return self.DEFAULT_MAX_QUEUE_SIZE

        try:
            normalized_value = int(max_queue_size)

        except ValueError as error:
            raise ValueError("max_queue_size must be an integer.") from error

        if normalized_value <= 0:
            raise ValueError("max_queue_size must be greater than zero.")

        return normalized_value

    def _validate_destination(self, destination):
        """
        Validate packet destination.
        """
        if not isinstance(destination, str) or destination.strip() == "":
            raise ValueError("Packet destination must be a non-empty string.")