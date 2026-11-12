"""Media Player platform for Fabriq Wi-Fi Speaker."""
from __future__ import annotations

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    EQ_MODE_TO_CODE,
    EQ_MODES,
    INPUT_SOURCES,
    PLAYER_MODE_MAP,
    SOURCE_TO_CMD,
)
from .coordinator import FabriqSpeakerCoordinator, decode_hex_string


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Fabriq Media Player entity."""
    coordinator: FabriqSpeakerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FabriqMediaPlayer(coordinator, entry)])


class FabriqMediaPlayer(CoordinatorEntity[FabriqSpeakerCoordinator], MediaPlayerEntity):
    """Representation of a Fabriq Wi-Fi Speaker."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.PLAY_MEDIA
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.SELECT_SOUND_MODE
    )
    _attr_source_list = list(INPUT_SOURCES.values())
    _attr_sound_mode_list = list(EQ_MODES.values())

    def __init__(self, coordinator: FabriqSpeakerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the Fabriq media player."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id}_media_player"
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this Fabriq speaker."""
        st = self.coordinator.data.get("status_ex", {}) if self.coordinator.data else {}
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.unique_id)},
            name=self.coordinator.speaker_name,
            manufacturer="Fabriq / Linkplay",
            model=st.get("project", "Fabriq Chorus (A31)"),
            sw_version=st.get("firmware", "4.0.6405"),
            hw_version=st.get("hardware", "A31"),
            configuration_url=f"http://{self.coordinator.host}",
        )

    @property
    def available(self) -> bool:
        """Keep entity available even during brief sleep so automations don't break."""
        return True

    @property
    def state(self) -> MediaPlayerState:
        """Return the current playback state."""
        if not self.coordinator.online:
            return MediaPlayerState.STANDBY
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        st = str(player.get("status", "stop")).lower()
        if st in ("play", "playing", "load"):
            return MediaPlayerState.PLAYING
        if st == "pause":
            return MediaPlayerState.PAUSED
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float:
        """Volume level of the media player (0..1)."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        try:
            return max(0.0, min(1.0, int(player.get("vol", 35)) / 100.0))
        except (ValueError, TypeError):
            return 0.35

    @property
    def is_volume_muted(self) -> bool:
        """Boolean if volume is currently muted."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        return str(player.get("mute", "0")) == "1"

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        if not self.coordinator.online:
            return "Uyku Modunda (Dokununca Uyanır)"
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        return decode_hex_string(player.get("Title")) or None

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        return decode_hex_string(player.get("Artist")) or None

    @property
    def media_album_name(self) -> str | None:
        """Album of current playing media."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        return decode_hex_string(player.get("Album")) or None

    @property
    def source(self) -> str | None:
        """Current input source."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        mode = str(player.get("mode", "10"))
        return PLAYER_MODE_MAP.get(mode, "Wi-Fi / Ağ")

    @property
    def sound_mode(self) -> str | None:
        """Current EQ sound mode."""
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        eq = str(player.get("eq", "0"))
        return EQ_MODES.get(eq, "Normal (Flat)")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra hardware attributes."""
        st = self.coordinator.data.get("status_ex", {}) if self.coordinator.data else {}
        player = self.coordinator.data.get("player", {}) if self.coordinator.data else {}
        return {
            "ip_address": self.coordinator.host,
            "online": self.coordinator.online,
            "wifi_rssi_dbm": st.get("RSSI"),
            "firmware": st.get("firmware"),
            "mac_address": st.get("MAC"),
            "multiroom_group": st.get("group"),
            "channel_mode": player.get("ch"),
        }

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        vol_int = max(0, min(100, int(round(volume * 100))))
        await self.coordinator.async_send_command(f"setPlayerCmd:vol:{vol_int}")
        self.coordinator._last_player_status["vol"] = str(vol_int)
        self.async_write_ha_state()

    async def async_volume_up(self) -> None:
        """Step volume up by 5%."""
        await self.async_set_volume_level(min(1.0, self.volume_level + 0.05))

    async def async_volume_down(self) -> None:
        """Step volume down by 5%."""
        await self.async_set_volume_level(max(0.0, self.volume_level - 0.05))

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        m = "1" if mute else "0"
        await self.coordinator.async_send_command(f"setPlayerCmd:mute:{m}")
        self.coordinator._last_player_status["mute"] = m
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Send play/resume command."""
        await self.coordinator.async_send_command("setPlayerCmd:resume")
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.coordinator.async_send_command("setPlayerCmd:pause")
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self.coordinator.async_send_command("setPlayerCmd:stop")
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.coordinator.async_send_command("setPlayerCmd:next")
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.coordinator.async_send_command("setPlayerCmd:prev")
        await self.coordinator.async_request_refresh()

    async def async_play_media(
        self, media_type: MediaType | str, media_id: str, **kwargs: Any
    ) -> None:
        """Play a piece of media (HTTP stream URL)."""
        await self.coordinator.async_play_url(media_id)

    async def async_select_source(self, source: str) -> None:
        """Select input source (Wi-Fi, Bluetooth, AUX)."""
        cmd_mode = SOURCE_TO_CMD.get(source, "wifi")
        await self.coordinator.async_send_command(f"setPlayerCmd:switchmode:{cmd_mode}")
        await self.coordinator.async_request_refresh()

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select Equalizer sound mode."""
        code = EQ_MODE_TO_CODE.get(sound_mode, "0")
        await self.coordinator.async_send_command(f"EQLoad:{code}")
        self.coordinator._last_player_status["eq"] = code
        self.async_write_ha_state()
