import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.services.forwarding_service import ForwardingService


class TestForwardingService(unittest.TestCase):
    """
    Sprint 2 tests for packet forwarding decisions.
    """

    def setUp(self):
        self.service = ForwardingService()

    def test_forward_packet_when_router_destination_exists(self):
        routing_table = {
            "source_router": "R1",
            "entries": [
                {
                    "source_router": "R1",
                    "destination_router": "R2",
                    "destination_prefix": "R2",
                    "prefix_length": 32,
                    "next_hop": "R2",
                    "cost": 10,
                    "path": ["R1", "R2"]
                }
            ]
        }

        result = self.service.decide_forwarding(routing_table, "R2")

        self.assertEqual(result["action"], "FORWARD")
        self.assertEqual(result["next_hop"], "R2")
        self.assertEqual(result["matched_prefix"], "R2")
        self.assertEqual(result["cost"], 10)
        self.assertEqual(result["path"], ["R1", "R2"])

    def test_drop_packet_when_no_matching_route_exists(self):
        routing_table = {
            "source_router": "R3",
            "entries": []
        }

        result = self.service.decide_forwarding(routing_table, "R1")

        self.assertEqual(result["action"], "DROP")
        self.assertIn("No matching route", result["reason"])

    def test_forward_uses_next_hop_from_indirect_path(self):
        routing_table = {
            "source_router": "R1",
            "entries": [
                {
                    "source_router": "R1",
                    "destination_router": "R3",
                    "destination_prefix": "R3",
                    "prefix_length": 32,
                    "next_hop": "R2",
                    "cost": 4,
                    "path": ["R1", "R2", "R3"]
                }
            ]
        }

        result = self.service.decide_forwarding(routing_table, "R3")

        self.assertEqual(result["action"], "FORWARD")
        self.assertEqual(result["next_hop"], "R2")
        self.assertEqual(result["cost"], 4)
        self.assertEqual(result["path"], ["R1", "R2", "R3"])

    def test_invalid_routing_table_without_entries_is_rejected(self):
        routing_table = {
            "source_router": "R1"
        }

        with self.assertRaises(ValueError):
            self.service.decide_forwarding(routing_table, "R2")

    def test_ipv4_longest_prefix_match_selects_most_specific_route(self):
        routing_table = {
            "source_router": "R1",
            "entries": [
                {
                    "source_router": "R1",
                    "destination_router": "NET_A",
                    "destination_prefix": "192.168.0.0",
                    "prefix_length": 16,
                    "next_hop": "R2",
                    "cost": 10,
                    "path": ["R1", "R2"]
                },
                {
                    "source_router": "R1",
                    "destination_router": "NET_B",
                    "destination_prefix": "192.168.1.0",
                    "prefix_length": 24,
                    "next_hop": "R3",
                    "cost": 5,
                    "path": ["R1", "R3"]
                }
            ]
        }

        result = self.service.decide_forwarding(routing_table, "192.168.1.50")

        self.assertEqual(result["action"], "FORWARD")
        self.assertEqual(result["next_hop"], "R3")
        self.assertEqual(result["matched_prefix"], "192.168.1.0")
        self.assertEqual(result["cost"], 5)

    def test_ipv4_packet_is_dropped_when_no_prefix_matches(self):
        routing_table = {
            "source_router": "R1",
            "entries": [
                {
                    "source_router": "R1",
                    "destination_router": "NET_A",
                    "destination_prefix": "192.168.0.0",
                    "prefix_length": 16,
                    "next_hop": "R2",
                    "cost": 10,
                    "path": ["R1", "R2"]
                }
            ]
        }

        result = self.service.decide_forwarding(routing_table, "10.0.0.5")

        self.assertEqual(result["action"], "DROP")
        self.assertIn("No matching route", result["reason"])


if __name__ == "__main__":
    unittest.main()