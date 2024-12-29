import json, os

class Settings:
    def load_settings():
        settings_path = os.path.join(os.getcwd(), 'app', 'config', 'settings.json')
        with open(settings_path, 'r') as f:
            return json.load(f)

    settings = load_settings()