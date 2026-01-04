from gi.repository import Gtk, Adw
import gi
import sys

from loguru import logger as log

from src.backend.PluginManager import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

KEY_COMPOSITE_TIMEOUT = "composite_timeout"
DEFAULT_COMPOSITE_TIMEOUT = 80  # milliseconds


class PluginSettings:
    def __init__(self, plugin_base: PluginBase):
        self._plugin_base = plugin_base
        self._settings_cache = None

    def get_settings_area(self) -> Adw.PreferencesGroup:
        
        # Composite timeout spin button
        self._composite_timeout_adjustment = Gtk.Adjustment(
            value=DEFAULT_COMPOSITE_TIMEOUT,
            lower=10,
            upper=500,
            step_increment=10,
            page_increment=50
        )
        self._composite_timeout_spin = Adw.SpinRow(
            adjustment=self._composite_timeout_adjustment,
            title=self._plugin_base.lm.get("settings.composite-timeout.label"),
            subtitle=self._plugin_base.lm.get("settings.composite-timeout.subtitle")
        )

        self._load_settings()
        self._composite_timeout_spin.connect("notify::value", self._on_change_composite_timeout)

        pref_group = Adw.PreferencesGroup()
        pref_group.set_title(self._plugin_base.lm.get("settings.title"))
        pref_group.add(self._composite_timeout_spin)
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
        composite_timeout = settings.get(KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT)
        self._composite_timeout_spin.set_value(composite_timeout)

    def _update_settings(self, key: str, value: str):
        settings = self._get_cached_settings()
        settings[key] = value
        self._plugin_base.set_settings(settings)
        self._invalidate_cache()

    def _on_change_composite_timeout(self, spin, _):
        timeout = int(spin.get_value())
        self._update_settings(KEY_COMPOSITE_TIMEOUT, timeout)

    def get_composite_timeout(self) -> int:
        """Get the configured composite timeout in milliseconds."""
        settings = self._get_cached_settings()
        return settings.get(KEY_COMPOSITE_TIMEOUT, DEFAULT_COMPOSITE_TIMEOUT)