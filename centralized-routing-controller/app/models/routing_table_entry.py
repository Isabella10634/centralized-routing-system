class RoutingTableEntry:
    """
    Model that represents one routing/forwarding table entry.

    Each entry tells one source router how to reach one destination router.

    Fields:
    - source_router: Router that owns this table entry.
    - destination_router: Final destination router.
    - destination_prefix: Simulated destination prefix.
    - prefix_length: Prefix length used later by Longest Prefix Matching.
    - next_hop: Next router to forward the packet to.
    - cost: Total path cost from source_router to destination_router.
    - path: Complete shortest path calculated by Dijkstra.
    """

    def __init__(
        self,
        source_router,
        destination_router,
        destination_prefix,
        prefix_length,
        next_hop,
        cost,
        path
    ):
        self.source_router = source_router
        self.destination_router = destination_router
        self.destination_prefix = destination_prefix
        self.prefix_length = prefix_length
        self.next_hop = next_hop
        self.cost = cost
        self.path = path

    def to_dict(self):
        """
        Convert the routing table entry to a dictionary.

        This format can be used later for:
        - JSON UPDATE_TABLE messages.
        - MySQL persistence.
        - CLI visualization.
        """
        return {
            "source_router": self.source_router,
            "destination_router": self.destination_router,
            "destination_prefix": self.destination_prefix,
            "prefix_length": self.prefix_length,
            "next_hop": self.next_hop,
            "cost": self.cost,
            "path": self.path
        }