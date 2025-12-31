import json, os, difflib

class Settings:
    def load_settings(self, *args):
        settings_path = os.path.join(os.getcwd(), *args)
        with open(settings_path, 'r') as f:
            return json.load(f)
        
    def load_map_settings(self, map_name, difficulty):
        return self.load_settings('app', 'config', 'maps', map_name, difficulty + '.json')

    def load_global_settings(self):
        return self.load_settings('app', 'config', 'settings.json')

    def get_available_maps(self):
        """Return list of all available map folder names."""
        maps_dir = os.path.join(os.getcwd(), 'app', 'config', 'maps')
        return [d for d in os.listdir(maps_dir)
                if os.path.isdir(os.path.join(maps_dir, d))]

    def find_best_map_match(self, ocr_text, cutoff=0.75):
        """
        Find the best matching map name using fuzzy matching.

        Args:
            ocr_text: The OCR-read map name
            cutoff: Minimum similarity ratio (0.0-1.0). Higher = stricter.

        Returns:
            Tuple of (best_match, similarity_score) or (None, 0) if no match
        """
        available_maps = self.get_available_maps()

        # Get the best match above cutoff
        matches = difflib.get_close_matches(ocr_text, available_maps, n=1, cutoff=cutoff)

        if matches:
            best_match = matches[0]
            # Calculate the actual similarity score for logging
            score = difflib.SequenceMatcher(None, ocr_text, best_match).ratio()
            return (best_match, score)

        return (None, 0)