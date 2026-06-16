from app.dao.queue_dao import QueueDAO


class MetricDAO:
    """
    DAO responsible for obtaining local router metrics.

    Metrics are derived from the persisted FIFO queue state.
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.queue_dao = QueueDAO(router_name)

    def get_current_metrics(self):
        """
        Return the current metrics required by the Sprint 3 document.
        """
        state = self.queue_dao.load_state()
        metrics = state.get("metrics", {})

        return {
            "queue_size": len(state.get("queue", [])),
            "packets_forwarded": int(metrics.get("packets_forwarded", 0)),
            "packets_discarded": int(metrics.get("packets_discarded", 0))
        }