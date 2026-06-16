import json
import os


class QueueDAO:
    """
    DAO responsible for local JSON persistence of the router FIFO queue.

    The persisted state includes:
    - queued packets
    - packets forwarded counter
    - packets discarded counter
    - last generated packet id
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_path = os.path.join(self.base_path, "data")
        self.file_path = os.path.join(
            self.data_path,
            f"queue_state_{self.router_name}.json"
        )

    def load_state(self):
        """
        Load queue state from local JSON file.
        """
        if not os.path.exists(self.file_path):
            return self._default_state()

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_state(self, state):
        """
        Save queue state to local JSON file.
        """
        os.makedirs(self.data_path, exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4)

    def reset_state(self):
        """
        Reset queue state. Useful for controlled tests and demos.
        """
        state = self._default_state()
        self.save_state(state)
        return state

    def _default_state(self):
        """
        Return the default queue state.
        """
        return {
            "router_id": self.router_name,
            "last_packet_id": 0,
            "queue": [],
            "metrics": {
                "packets_forwarded": 0,
                "packets_discarded": 0
            }
        }