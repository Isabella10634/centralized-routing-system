import ipaddress


class ForwardingService:
    """
    Service responsible for forwarding decisions using a routing table.

    Sprint 2 responsibility:
    - Apply Longest Prefix Matching (LPM) over the received routing table.
    - Return the next hop for a simulated packet destination.

    This implementation supports two cases:

    1. Academic router-name destination:
       destination = "R2"
       destination_prefix = "R2"

    2. Future IPv4 prefix destination:
       destination = "10.0.2.15"
       destination_prefix = "10.0.2.0"
       prefix_length = 24

    This keeps Sprint 2 working now and allows the project to grow later
    without rewriting the forwarding logic.
    """

    def decide_forwarding(self, routing_table, destination):
        """
        Decide how to forward a simulated packet.

        Args:
            routing_table (dict): Local routing table received from controller.
            destination (str): Simulated packet destination.

        Returns:
            dict: Forwarding decision.
        """
        self._validate_routing_table(routing_table)
        self._validate_destination(destination)

        entries = routing_table.get("entries", [])
        best_entry = self._find_best_entry(entries, destination)

        if best_entry is None:
            return {
                "type": "FORWARDING_DECISION",
                "action": "DROP",
                "destination": destination,
                "reason": "No matching route found."
            }

        return {
            "type": "FORWARDING_DECISION",
            "action": "FORWARD",
            "destination": destination,
            "next_hop": best_entry.get("next_hop"),
            "matched_destination_router": best_entry.get("destination_router"),
            "matched_prefix": best_entry.get("destination_prefix"),
            "prefix_length": best_entry.get("prefix_length"),
            "cost": best_entry.get("cost"),
            "path": best_entry.get("path", [])
        }

    def _find_best_entry(self, entries, destination):
        """
        Find the best routing table entry using LPM.

        Exact router-name matches are accepted for the current Sprint 2 demo.
        IPv4 prefix matches are selected by longest prefix length.
        """
        best_entry = None
        best_prefix_length = -1

        for entry in entries:
            match_result = self._match_entry(entry, destination)

            if not match_result["matches"]:
                continue

            current_prefix_length = match_result["prefix_length"]

            if current_prefix_length > best_prefix_length:
                best_prefix_length = current_prefix_length
                best_entry = entry

        return best_entry

    def _match_entry(self, entry, destination):
        """
        Check whether one routing table entry matches the packet destination.
        """
        destination_router = entry.get("destination_router")
        destination_prefix = entry.get("destination_prefix")
        prefix_length = entry.get("prefix_length", 0)

        if destination == destination_router:
            return {
                "matches": True,
                "prefix_length": 10_000
            }

        if destination == destination_prefix:
            return {
                "matches": True,
                "prefix_length": 10_000
            }

        if self._is_ipv4_address(destination):
            return self._match_ipv4_prefix(
                destination,
                destination_prefix,
                prefix_length
            )

        return {
            "matches": False,
            "prefix_length": -1
        }

    def _match_ipv4_prefix(self, destination, destination_prefix, prefix_length):
        """
        Match an IPv4 destination against one routing table prefix.
        """
        if destination_prefix is None:
            return {
                "matches": False,
                "prefix_length": -1
            }

        try:
            network = ipaddress.ip_network(
                f"{destination_prefix}/{prefix_length}",
                strict=False
            )
            destination_ip = ipaddress.ip_address(destination)

            return {
                "matches": destination_ip in network,
                "prefix_length": int(prefix_length)
            }

        except ValueError:
            return {
                "matches": False,
                "prefix_length": -1
            }

    def _is_ipv4_address(self, value):
        """
        Check whether a string is a valid IPv4 address.
        """
        try:
            ipaddress.ip_address(value)
            return True

        except ValueError:
            return False

    def _validate_routing_table(self, routing_table):
        """
        Validate routing table structure.
        """
        if not isinstance(routing_table, dict):
            raise ValueError("Routing table must be a dictionary.")

        if "source_router" not in routing_table:
            raise ValueError("Routing table is missing source_router.")

        if "entries" not in routing_table:
            raise ValueError("Routing table is missing entries.")

        if not isinstance(routing_table["entries"], list):
            raise ValueError("Routing table entries must be a list.")

    def _validate_destination(self, destination):
        """
        Validate simulated destination.
        """
        if not isinstance(destination, str) or destination.strip() == "":
            raise ValueError("Destination must be a non-empty string.")