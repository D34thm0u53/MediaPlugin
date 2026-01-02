from gi.repository import Gtk, Adw
import gi
import sys

from loguru import logger as log

from src.backend.PluginManager import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

KEY_LOG_LEVEL = "log_level"


class PluginSettings:
    def __init__(self, plugin_base: PluginBase):
        self._plugin_base = plugin_base
        self._settings_cache = None

    def get_settings_area(self) -> Adw.PreferencesGroup:
        # Log level selector
        self._log_level_model = Gtk.StringList()
        self._log_level_selector = Adw.ComboRow(
            model=self._log_level_model,
            title=self._plugin_base.lm.get("settings.log-level.label"),
            subtitle=self._plugin_base.lm.get("settings.log-level.subtitle")
        )

        # Populate log level options
        log_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in log_levels:
            self._log_level_model.append(level)

        self._load_settings()
        self._log_level_selector.connect("notify::selected", self._on_change_log_level)

        pref_group = Adw.PreferencesGroup()
        pref_group.set_title(self._plugin_base.lm.get("settings.title"))
        pref_group.add(self._log_level_selector)
        return pref_group

    def _get_cached_settings(self):
        """Get settings from cache or load from storage."""
        if self._settings_cache is None:
            self._settings_cache = self._plugin_base.get_settings()
        return self._settings_cache

    def _invalidate_cache(self):
        """Invalidate settings cache after modifications."""
        self._settings_cache = None

    def _load_settings(self):
        settings = self._get_cached_settings()
        log_level = settings.get(KEY_LOG_LEVEL, "INFO")

        # Select the appropriate level
        try:
            selected_index = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(log_level)
        except ValueError:
            selected_index = 2  # Default to INFO

        self._log_level_selector.set_selected(selected_index)

    def _update_settings(self, key: str, value: str):
        settings = self._get_cached_settings()
        settings[key] = value
        self._plugin_base.set_settings(settings)
        self._invalidate_cache()

    def _on_change_log_level(self, combo, *args):
        selected_index = combo.get_selected()
        log_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if selected_index < len(log_levels):
            log_level = log_levels[selected_index]
            self._update_settings(KEY_LOG_LEVEL, log_level)
            # Reconfigure the logger with the new level
            log.remove()  # Remove existing handlers
            log.add(
                sys.stderr,
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                level=log_level,
            )