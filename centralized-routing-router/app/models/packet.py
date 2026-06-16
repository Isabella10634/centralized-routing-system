from datetime import datetime


class Packet:
    """
    Represents one simulated packet handled by a router queue.

    Sprint 3:
    - Used by the FIFO queue.
    - Stores destination, arrival time and status.
    """

    def __init__(self, packet_id, router_id, destination, status="en_cola"):
        self.packet_id = packet_id
        self.router_id = router_id
        self.destination = destination
        self.timestamp_llegada = datetime.now().isoformat(timespec="seconds")
        self.status = status

    def to_dict(self):
        """
        Convert packet object to dictionary for JSON persistence.
        """
        return {
            "packet_id": self.packet_id,
            "router_id": self.router_id,
            "destination": self.destination,
            "timestamp_llegada": self.timestamp_llegada,
            "status": self.status
        }