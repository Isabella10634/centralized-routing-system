class RoutingTableView:
    """
    View responsible for printing a router routing table in the terminal.
    """

    @staticmethod
    def display(routing_table):
        """
        Print a routing table in a readable CLI format.
        """
        source_router = routing_table.get("source_router", "UNKNOWN")
        entries = routing_table.get("entries", [])

        print("")
        print(f"Routing table for router {source_router}")
        print("-" * 78)
        print(
            f"{'Destination':<15}"
            f"{'Prefix':<15}"
            f"{'Len':<8}"
            f"{'Next hop':<15}"
            f"{'Cost':<8}"
            f"{'Path'}"
        )
        print("-" * 78)

        if not entries:
            print("No routing entries available.")
            print("-" * 78)
            return

        for entry in entries:
            destination = entry.get("destination_router", "-")
            prefix = entry.get("destination_prefix", "-")
            prefix_length = entry.get("prefix_length", "-")
            next_hop = entry.get("next_hop", "-")
            cost = entry.get("cost", "-")
            path = " -> ".join(entry.get("path", []))

            print(
                f"{destination:<15}"
                f"{prefix:<15}"
                f"{str(prefix_length):<8}"
                f"{next_hop:<15}"
                f"{str(cost):<8}"
                f"{path}"
            )

        print("-" * 78)