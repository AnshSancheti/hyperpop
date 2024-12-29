import json, os

class Settings:
    def load_settings(self, *args):
        settings_path = os.path.join(os.getcwd(), *args)
        with open(settings_path, 'r') as f:
            return json.load(f)
        
    def load_map_settings(self, map_name, difficulty):
        return self.load_settings('app', 'config', 'maps', map_name, difficulty)

    def load_global_settings(self):
        return self.load_settings('app', 'config', 'settings.json')    