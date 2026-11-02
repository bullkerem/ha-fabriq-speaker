"""Config flow for Fabriq Wi-Fi Speaker integration."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_probe_speaker(hass, host: str, timeout: float = 2.0) -> dict[str, Any] | None:
    """Probe a single IP for a Linkplay / Fabriq HTTP API endpoint."""
    session = async_get_clientsession(hass)
    url = f"http://{host}/httpapi.asp?command=getStatusEx"
    try:
        async with asyncio.timeout(timeout):
            async with session.get(url, ssl=False) as resp:
                if resp.status == 200:
                    text = await resp.text(encoding="utf-8", errors="replace")
                    data = json.loads(text)
                    if isinstance(data, dict) and ("uuid" in data or "DeviceName" in data):
                        return data
    except Exception:
        pass
    return None


class FabriqSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fabriq Wi-Fi Speaker."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._discovered: dict[str, dict[str, Any]] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step: allow manual IP or pick discovered speaker."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, "").strip()

            info = await async_probe_speaker(self.hass, host, timeout=3.0)
            if info:
                uuid = info.get("uuid") or info.get("MAC") or host
                dev_name = name or info.get("DeviceName") or f"Fabriq ({host})"
            else:
                # Allow adding even if speaker is currently in deep sleep!
                uuid = f"fabriq_{host.replace('.', '_')}"
                dev_name = name or f"Fabriq ({host})"

            await self.async_set_unique_id(uuid)
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})

            return self.async_create_entry(
                title=f"{dev_name} ({host})",
                data={
                    CONF_HOST: host,
                    CONF_NAME: dev_name,
                    "uuid": uuid,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.8.124"): str,
                vol.Optional(CONF_NAME, default="Fabriq Hoparlör"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
