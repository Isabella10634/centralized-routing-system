from app.utils.config_loader import ConfigLoader

_controller_config = ConfigLoader.load_config("controller_config.json")
DB_CONFIG = _controller_config["database"]