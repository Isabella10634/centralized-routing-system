from app.dao.metric_dao import MetricDAO
from app.models.metric import Metric


class MetricController:
    """
    Controller responsible for generating router metrics.

    Sprint 3 / FR-13:
    - queue_size
    - packets_forwarded
    - packets_discarded
    """

    def __init__(self, router_name):
        self.router_name = router_name
        self.metric_dao = MetricDAO(router_name)

    def get_current_metric(self):
        """
        Return the current metrics snapshot as a dictionary.
        """
        current = self.metric_dao.get_current_metrics()

        metric = Metric(
            router_id=self.router_name,
            queue_size=current["queue_size"],
            packets_forwarded=current["packets_forwarded"],
            packets_discarded=current["packets_discarded"]
        )

        return metric.to_dict()