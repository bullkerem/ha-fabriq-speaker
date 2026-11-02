"""DataUpdateCoordinator for Fabriq Wi-Fi Speakers (Linkplay A31)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import json
import logging
from typing import Any
from urllib.parse import quote

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


def decode_hex_string(val: str | None) -> str:
    """Decode Linkplay hex-encoded UTF-8 string if applicable."""
    if not val:
        return ""
    if val in ("0", "Unknown"):
        return ""
    try:
        if all(c in "0123456789abcdefABCDEF" for c in val) and len(val) % 2 == 0 and len(val) >= 4:
            decoded = bytes.fromhex(val).decode("utf-8", errors="replace").strip()
            if decoded and decoded != "Unknown":
                return decoded
    except Exception:
        pass
    return val


class FabriqSpeakerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls Fabriq speaker and survives sleep cycles without disconnecting."""

    def __init__(self, hass: HomeAssistant, host: str, name: str, unique_id: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{host}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.host = host
        self.speaker_name = name
        self.unique_id = unique_id
        self.online = False
        self.prompt_enabled = True
        self._last_status_ex: dict[str, Any] = {
            "DeviceName": name,
            "uuid": unique_id,
            "firmware": "4.0.6405",
            "hardware": "A31",
            "RSSI": "-65",
        }
        self._last_player_status: dict[str, Any] = {
            "status": "stop",
            "vol": "35",
            "mute": "0",
            "eq": "0",
            "mode": "10",
            "ch": "0",
            "Title": "",
            "Artist": "",
            "Album": "",
        }

    async def async_send_command(self, command: str, timeout: float = 4.0) -> str | None:
        """Send a raw Linkplay HTTP API command to the speaker."""
        session = async_get_clientsession(self.hass)
        url = f"http://{self.host}/httpapi.asp?command={command}"
        try:
            async with asyncio.timeout(timeout):
                async with session.get(url, ssl=False) as resp:
                    text = await resp.text(encoding="utf-8", errors="replace")
                    return text.strip()
        except Exception as err:
            _LOGGER.debug("Fabriq (%s) command '%s' failed (speaker may be sleeping): %s", self.host, command, err)
            return None

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll getStatusEx and getPlayerStatus; retain cached state if sleeping."""
        was_online = self.online
        status_raw = await self.async_send_command("getStatusEx", timeout=2.5)
        if not status_raw:
            self.online = False
            return {
                "online": False,
                "status_ex": self._last_status_ex,
                "player": self._last_player_status,
            }

        try:
            status_ex = json.loads(status_raw)
            if isinstance(status_ex, dict):
                self._last_status_ex.update(status_ex)
                if status_ex.get("DeviceName"):
                    self.speaker_name = status_ex["DeviceName"]
        except Exception:
            pass

        player_raw = await self.async_send_command("getPlayerStatus", timeout=2.5)
        if player_raw:
            try:
                player = json.loads(player_raw)
                if isinstance(player, dict):
                    self._last_player_status.update(player)
            except Exception:
                pass

        self.online = True

        # If speaker just woke up from sleep, sync its clock automatically
        if not was_online:
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            await self.async_send_command(f"timeSync:{now_str}", timeout=2.0)

        return {
            "online": True,
            "status_ex": self._last_status_ex,
            "player": self._last_player_status,
        }

    async def async_play_url(self, url: str) -> bool:
        """Play an HTTP audio stream URL on the speaker."""
        res = await self.async_send_command(f"setPlayerCmd:play:{url}", timeout=4.0)
        await self.async_request_refresh()
        return res is not None
