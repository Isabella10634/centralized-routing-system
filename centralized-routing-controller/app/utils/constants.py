from app.utils.config_loader import ConfigLoader

_controller_config = ConfigLoader.load_config("controller_config.json")

CONTROLLER_HOST = _controller_config["server"]["host"]
CONTROLLER_PORT = _controller_config["server"]["port"]

ROUTER_STATUS_ACTIVE = "activo"
ROUTER_STATUS_DOWN = "caido"

LINK_STATUS_ACTIVE = "activo"
LINK_STATUS_DOWN = "caido"

EVENT_TYPE_ROUTER_REGISTRATION = "registro_router"
EVENT_TYPE_TOPOLOGY_UPDATE = "actualizacion_topologia"
EVENT_TYPE_ROUTE_CALCULATION = "calculo_rutas"
EVENT_TYPE_TABLE_DELIVERY = "envio_tabla"
EVENT_TYPE_LINK_COST_CHANGE = "cambio_costo_enlace"
EVENT_TYPE_HEARTBEAT_FAILED = "heartbeat_fallido"
EVENT_TYPE_ROUTER_DOWN = "router_caido"
EVENT_TYPE_METRICS_RECEIVED = "metricas_recibidas"
EVENT_TYPE_ERROR = "error"