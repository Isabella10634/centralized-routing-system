class RoutingTable:
    """
    Model that represents the routing/forwarding table of one router.

    A routing table belongs to one source router and contains multiple
    RoutingTableEntry objects.
    """

    def __init__(self, source_router):
        self.source_router = source_router
        self.entries = []

    def add_entry(self, entry):
        """
        Add one RoutingTableEntry to the table.
        """
        self.entries.append(entry)

    def to_dict(self):
        """
        Convert the complete routing table to a dictionary.
        """
        return {
            "source_router": self.source_router,
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ]
        }