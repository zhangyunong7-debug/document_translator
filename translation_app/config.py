"""
Configuration module for storing API keys and settings
"""
import json
import os
from pathlib import Path


class Config:
    """Configuration manager for the translation app"""

    def __init__(self):
        self.config_dir = Path.home() / ".translation_app"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self.settings = self._load_config()

    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return self._default_config()
        return self._default_config()

    def _default_config(self):
        """Return default configuration"""
        return {
            "google_api_key": "",
            "deepl_api_key": "",
            "baidu_app_id": "",
            "baidu_api_key": "",
            "default_source_lang": "auto",
            "default_target_lang": "zh-CN",
            "output_folder": "",
            "selected_engine": "google"
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.settings[key] = value

    def get_all(self):
        """Get all configuration"""
        return self.settings.copy()
