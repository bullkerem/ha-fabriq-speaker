"""Switch platform for Fabriq Wi-Fi Speaker (Voice Prompt toggle)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Fabriq Switch entities."""
    coordinator: FabriqSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FabriqVoicePromptSwitch(coordinator)])


class FabriqVoicePromptSwitch(CoordinatorEntity[FabriqSpeakerCoordinator], SwitchEntity):
    """Switch to enable or disable Fabriq voice prompts."""

    _attr_has_entity_name = True
    _attr_name = "Sesli Uyarılar (Voice Prompt)"
    _attr_icon = "mdi:account-voice"

    def __init__(self, coordinator: FabriqSpeakerCoordinator) -> None:
        """Initialize voice prompt switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_voice_prompt"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
        )

    @property
    def is_on(self) -> bool:
        """Return true if voice prompt is enabled."""
        return self.coordinator.prompt_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable voice prompts on speaker."""
        await self.coordinator.async_send_command("PromptEnable:1")
        self.coordinator.prompt_enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable voice prompts on speaker."""
        await self.coordinator.async_send_command("PromptEnable:0")
        self.coordinator.prompt_enabled = False
        self.async_write_ha_state()
