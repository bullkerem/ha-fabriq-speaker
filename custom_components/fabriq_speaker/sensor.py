"""Sensor platform for Fabriq Wi-Fi Speaker (Wi-Fi RSSI, Connection Status)."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FabriqSpeakerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fabriq Sensor entities."""
    coordinator: FabriqSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FabriqRssiSensor(coordinator),
            FabriqStatusSensor(coordinator),
        ]
    )


class FabriqRssiSensor(CoordinatorEntity[FabriqSpeakerCoordinator], SensorEntity):
    """Wi-Fi RSSI Signal Strength sensor for Fabriq speaker."""

    _attr_has_entity_name = True
    _attr_name = "Wi-Fi Sinyal Gücü"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_icon = "mdi:wifi"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize RSSI sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_wifi_rssi"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
        )

    @property
    def native_value(self) -> int | None:
        """Return Wi-Fi RSSI in dBm."""
        st = self.coordinator.data.get("status_ex", {}) if self.coordinator.data else {}
        try:
            return int(st.get("RSSI", -65))
        except (ValueError, TypeError):
            return None


class FabriqStatusSensor(CoordinatorEntity[FabriqSpeakerCoordinator], SensorEntity):
    """Online / Deep Sleep status sensor for Fabriq speaker."""

    _attr_has_entity_name = True
    _attr_name = "Bağlantı Durumu"
    _attr_icon = "mdi:access-point-check"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize connection status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_conn_status"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
        )

    @property
    def native_value(self) -> str:
        """Return Çevrimiçi or Uyku Modunda."""
        return "Çevrimiçi (Aktif)" if self.coordinator.online else "Uyku Modunda (Beklemede)"
