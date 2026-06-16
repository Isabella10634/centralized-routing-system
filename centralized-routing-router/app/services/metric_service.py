class MetricService:
    """
    Service responsible for building METRICS messages sent to the controller.
    """

    @staticmethod
    def build_metrics_message(router_id, metric_snapshot):
        """
        Build the METRICS message required by the project documents.
        """
        required_fields = [
            "queue_size",
            "packets_forwarded",
            "packets_discarded"
        ]

        for field in required_fields:
            if field not in metric_snapshot:
                raise ValueError(f"Metric snapshot is missing {field}.")

        return {
            "type": "METRICS",
            "router_id": router_id,
            "queue_size": int(metric_snapshot["queue_size"]),
            "packets_forwarded": int(metric_snapshot["packets_forwarded"]),
            "packets_discarded": int(metric_snapshot["packets_discarded"])
        }