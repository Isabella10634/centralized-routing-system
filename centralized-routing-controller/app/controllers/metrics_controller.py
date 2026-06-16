from datetime import datetime

from app.dao.log_dao import LogDAO
from app.dao.metrics_dao import MetricsDAO
from app.dao.router_dao import RouterDAO
from app.utils.constants import EVENT_TYPE_ERROR


class MetricsController:
    """
    Controller responsible for processing METRICS messages from routers.

    Supports two compatible formats:

    1. Legacy operational metrics:
       - uptime_seconds
       - heartbeat_count
       - routing_entries

    2. Documented Sprint 3 metrics:
       - queue_size
       - packets_forwarded
       - packets_discarded
    """

    LEGACY_FIELDS = [
        "uptime_seconds",
        "heartbeat_count",
        "routing_entries"
    ]

    DOCUMENTED_FIELDS = [
        "queue_size",
        "packets_forwarded",
        "packets_discarded"
    ]

    def __init__(self):
        self.router_dao = RouterDAO()
        self.metrics_dao = MetricsDAO()
        self.log_dao = LogDAO()

    def register_metrics(self, message_data):
        """
        Process a METRICS message.

        Legacy format:
        {
            "type": "METRICS",
            "router_id": "R1",
            "uptime_seconds": 20,
            "heartbeat_count": 4,
            "routing_entries": 2
        }

        Documented format:
        {
            "type": "METRICS",
            "router_id": "R1",
            "queue_size": 3,
            "packets_forwarded": 42,
            "packets_discarded": 2
        }
        """
        if "router_id" not in message_data:
            self._log_invalid_metrics("router_id")
            return {
                "type": "ERROR",
                "message": "Missing field: router_id"
            }

        router_name = message_data["router_id"]
        router = self.router_dao.get_router_by_name(router_name)

        if router is None:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"METRICS recibido de router no registrado: {router_name}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": f"Router {router_name} is not registered"
            }

        if self._has_any_legacy_field(message_data):
            missing_field = self._get_missing_field(message_data, self.LEGACY_FIELDS)

            if missing_field is not None:
                self._log_invalid_metrics(missing_field)
                return {
                    "type": "ERROR",
                    "message": f"Missing field: {missing_field}"
                }

            return self._register_legacy_metrics(router, router_name, message_data)

        if self._has_any_documented_field(message_data):
            missing_field = self._get_missing_field(
                message_data,
                self.DOCUMENTED_FIELDS
            )

            if missing_field is not None:
                self._log_invalid_metrics(missing_field)
                return {
                    "type": "ERROR",
                    "message": f"Missing field: {missing_field}"
                }

            return self._register_documented_metrics(router, router_name, message_data)

        missing_field = self.LEGACY_FIELDS[0]
        self._log_invalid_metrics(missing_field)

        return {
            "type": "ERROR",
            "message": f"Missing field: {missing_field}"
        }

    def _register_legacy_metrics(self, router, router_name, message_data):
        """
        Store previous operational metrics in metricas_router.
        """
        try:
            uptime_seconds = int(message_data["uptime_seconds"])
            heartbeat_count = int(message_data["heartbeat_count"])
            routing_entries = int(message_data["routing_entries"])

        except ValueError:
            return {
                "type": "ERROR",
                "message": "Metrics values must be integers"
            }

        if uptime_seconds < 0:
            return {
                "type": "ERROR",
                "message": "uptime_seconds must be greater than or equal to zero"
            }

        if heartbeat_count < 0:
            return {
                "type": "ERROR",
                "message": "heartbeat_count must be greater than or equal to zero"
            }

        if routing_entries < 0:
            return {
                "type": "ERROR",
                "message": "routing_entries must be greater than or equal to zero"
            }

        inserted_id = self.metrics_dao.insert_metrics(
            router["id"],
            router_name,
            uptime_seconds,
            heartbeat_count,
            routing_entries,
            datetime.now()
        )

        return {
            "type": "METRICS_OK",
            "router_id": router_name,
            "metric_id": inserted_id,
            "message": "Metrics stored successfully"
        }

    def _register_documented_metrics(self, router, router_name, message_data):
        """
        Store documented Sprint 3 metrics in metricas_globales.
        """
        try:
            queue_size = int(message_data["queue_size"])
            packets_forwarded = int(message_data["packets_forwarded"])
            packets_discarded = int(message_data["packets_discarded"])

        except ValueError:
            return {
                "type": "ERROR",
                "message": "Metrics values must be integers"
            }

        if queue_size < 0:
            return {
                "type": "ERROR",
                "message": "queue_size must be greater than or equal to zero"
            }

        if packets_forwarded < 0:
            return {
                "type": "ERROR",
                "message": "packets_forwarded must be greater than or equal to zero"
            }

        if packets_discarded < 0:
            return {
                "type": "ERROR",
                "message": "packets_discarded must be greater than or equal to zero"
            }

        inserted_id = self.metrics_dao.insert_global_metrics(
            router["id"],
            router_name,
            queue_size,
            packets_forwarded,
            packets_discarded,
            datetime.now()
        )

        return {
            "type": "METRICS_OK",
            "router_id": router_name,
            "metric_id": inserted_id,
            "message": "Metrics stored successfully"
        }

    def _has_any_legacy_field(self, message_data):
        """
        Return True if the message looks like a legacy metrics message.
        """
        return any(field in message_data for field in self.LEGACY_FIELDS)

    def _has_any_documented_field(self, message_data):
        """
        Return True if the message looks like a documented metrics message.
        """
        return any(field in message_data for field in self.DOCUMENTED_FIELDS)

    def _get_missing_field(self, message_data, required_fields):
        """
        Return the first missing field from a list of required fields.
        """
        for field in required_fields:
            if field not in message_data:
                return field

        return None

    def _log_invalid_metrics(self, missing_field):
        """
        Log invalid METRICS messages.
        """
        self.log_dao.insert_event(
            EVENT_TYPE_ERROR,
            f"METRICS inválido: falta el campo {missing_field}",
            datetime.now()
        )