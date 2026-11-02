"""Select platform for Fabriq Wi-Fi Speaker (Equalizer, Input Source, Audio Channel)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CHANNEL_MODES,
    CHANNEL_TO_CODE,
    DOMAIN,
    EQ_MODE_TO_CODE,
    EQ_MODES,
    INPUT_SOURCES,
    PLAYER_MODE_MAP,
    SOURCE_TO_CMD,
)
from .coordinator import FabriqSpeakerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fabriq Select entities."""
    coordinator: FabriqSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FabriqEqualizerSelect(coordinator),
            FabriqInputSourceSelect(coordinator),
            FabriqChannelSelect(coordinator),
        ]
    )


class FabriqBaseSelect(CoordinatorEntity[FabriqSpeakerCoordinator], SelectEntity):
    """Base class for Fabriq select entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize base select."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
        )


class FabriqEqualizerSelect(FabriqBaseSelect):
    """Equalizer (EQ) Mode selector for Fabriq speaker."""

    _attr_name = "Ekolayzer (EQ)"
    _attr_icon = "mdi:equalizer"
    _attr_options = list(EQ_MODES.values())

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize EQ select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_equalizer"

    @property
    def current_option(self) -> str | None:
        """Return currently selected EQ preset."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        eq = str(player.get("eq", "0"))
        return EQ_MODES.get(eq, "Normal (Flat)")

    async def async_select_option(self, option: str) -> None:
        """Change the selected EQ preset."""
        code = EQ_MODE_TO_CODE.get(option, "0")
        await self.coordinator.async_send_command(f"EQLoad:{code}")
        self.coordinator._last_player_status["eq"] = code
        self.async_write_ha_state()


class FabriqInputSourceSelect(FabriqBaseSelect):
    """Input source selector (Wi-Fi, Bluetooth, AUX) for Fabriq speaker."""

    _attr_name = "Ses Giriş Kaynağı"
    _attr_icon = "mdi:audio-input-stereo-minijack"
    _attr_options = list(INPUT_SOURCES.values())

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize Input Source select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_input_source"

    @property
    def current_option(self) -> str | None:
        """Return current input mode."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        mode = str(player.get("mode", "10"))
        mapped = PLAYER_MODE_MAP.get(mode, "Wi-Fi / Ağ")
        return mapped if mapped in self._attr_options else "Wi-Fi / Ağ"

    async def async_select_option(self, option: str) -> None:
        """Switch input mode."""
        cmd = SOURCE_TO_CMD.get(option, "wifi")
        await self.coordinator.async_send_command(f"setPlayerCmd:switchmode:{cmd}")
        await self.coordinator.async_request_refresh()


class FabriqChannelSelect(FabriqBaseSelect):
    """Audio channel selector (Stereo / Left / Right)."""

    _attr_name = "Ses Kanalı (Stereo / L / R)"
    _attr_icon = "mdi:speaker-multiple"
    _attr_options = list(CHANNEL_MODES.values())

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize Channel select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_audio_channel"

    @property
    def current_option(self) -> str | None:
        """Return current channel mode."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        ch = str(player.get("ch", "0"))
        return CHANNEL_MODES.get(ch, "Stereo (L+R)")

    async def async_select_option(self, option: str) -> None:
        """Change stereo/left/right channel mode."""
        code = CHANNEL_TO_CODE.get(option, "0")
        await self.coordinator.async_send_command(f"setPlayerCmd:slave_channel:{code}")
        self.coordinator._last_player_status["ch"] = code
        self.async_write_ha_state()
