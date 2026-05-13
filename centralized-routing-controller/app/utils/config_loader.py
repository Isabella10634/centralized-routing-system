import json
import os


class ConfigLoader:
    @staticmethod
    def load_config(config_filename):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_path, "config", config_filename)

        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)