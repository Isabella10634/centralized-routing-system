import sys

from app.network.controller_connection import ControllerConnection
from app.utils.config_loader import ConfigLoader


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.main <config_file>")
        return

    config_filename = sys.argv[1]
    router_config = ConfigLoader.load_config(config_filename)

    print(f"Router {router_config['router_name']} started successfully.")

    connection = ControllerConnection(router_config)
    connection.start()


if __name__ == "__main__":
    main()