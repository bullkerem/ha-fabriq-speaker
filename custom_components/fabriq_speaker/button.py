"""Button platform for Fabriq Wi-Fi Speaker (Reboot, Time Sync, Multiroom Ungroup)."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up Fabriq Button entities."""
    coordinator: FabriqSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FabriqRebootButton(coordinator),
            FabriqTimeSyncButton(coordinator),
            FabriqUngroupButton(coordinator),
        ]
    )


class FabriqBaseButton(CoordinatorEntity[FabriqSpeakerCoordinator], ButtonEntity):
    """Base class for Fabriq buttons."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize base button."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
        )


class FabriqRebootButton(FabriqBaseButton):
    """Button to reboot the Fabriq speaker."""

    _attr_name = "Yeniden Başlat (Reboot)"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize reboot button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_reboot"

    async def async_press(self) -> None:
        """Send reboot command."""
        await self.coordinator.async_send_command("StartRebootTime:0")


class FabriqTimeSyncButton(FabriqBaseButton):
    """Button to synchronize speaker internal clock."""

    _attr_name = "Saati Senkronize Et"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize time sync button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_timesync"

    async def async_press(self) -> None:
        """Send timeSync command."""
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        await self.coordinator.async_send_command(f"timeSync:{now_str}")
        await self.coordinator.async_request_refresh()


class FabriqUngroupButton(FabriqBaseButton):
    """Button to leave multiroom group and become standalone."""

    _attr_name = "Multiroom Gruptan Ayır (Tekil Mod)"
    _attr_icon = "mdi:speaker-off"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize ungroup button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_ungroup"

    async def async_press(self) -> None:
        """Send ungroup command."""
        await self.coordinator.async_send_command("multiroom:Ungroup")
        await self.coordinator.async_send_command("setPlayerCmd:slave_channel:0")
        await self.coordinator.async_request_refresh()
