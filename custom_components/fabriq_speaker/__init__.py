"""The Fabriq Wi-Fi Speaker (Linkplay A31) integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import FabriqSpeakerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.SENSOR,
]

SERVICE_SEND_COMMAND = "send_command"
SERVICE_JOIN_MULTIROOM = "join_multiroom"
SERVICE_LEAVE_MULTIROOM = "leave_multiroom"


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Fabriq Wi-Fi Speaker component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fabriq Wi-Fi Speaker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, f"Fabriq ({host})")
    uid = entry.data.get("uuid", entry.entry_id)

    coordinator = FabriqSpeakerCoordinator(hass, host=host, name=name, unique_id=uid)
    # Initial refresh; never fail setup if speaker is asleep
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND):
        async def handle_send_command(call: ServiceCall) -> None:
            """Send a raw Linkplay HTTP API command to one or all Fabriq speakers."""
            target_host = call.data.get("host")
            command = call.data["command"]
            for coord in hass.data[DOMAIN].values():
                if isinstance(coord, FabriqSpeakerCoordinator):
                    if not target_host or target_host in (coord.host, "all", "her_ikisi"):
                        await coord.async_send_command(command)
                        await coord.async_request_refresh()

        async def handle_join_multiroom(call: ServiceCall) -> None:
            """Join a slave Fabriq speaker to a master Fabriq speaker."""
            master_host = call.data["master_host"]
            slave_host = call.data["slave_host"]
            for coord in hass.data[DOMAIN].values():
                if isinstance(coord, FabriqSpeakerCoordinator) and coord.host == slave_host:
                    await coord.async_send_command(
                        f"ConnectMasterAp:JoinGroupMaster:eth{master_host}:wifi0.0.0.0"
                    )
                    await coord.async_request_refresh()

        async def handle_leave_multiroom(call: ServiceCall) -> None:
            """Ungroup Fabriq speaker(s) into standalone mode."""
            target_host = call.data.get("host")
            for coord in hass.data[DOMAIN].values():
                if isinstance(coord, FabriqSpeakerCoordinator):
                    if not target_host or target_host in (coord.host, "all", "her_ikisi"):
                        await coord.async_send_command("multiroom:Ungroup")
                        await coord.async_send_command("setPlayerCmd:slave_channel:0")
                        await coord.async_request_refresh()

        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_COMMAND,
            handle_send_command,
            schema=vol.Schema(
                {
                    vol.Optional("host"): cv.string,
                    vol.Required("command"): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_JOIN_MULTIROOM,
            handle_join_multiroom,
            schema=vol.Schema(
                {
                    vol.Required("master_host"): cv.string,
                    vol.Required("slave_host"): cv.string,
                }
            ),
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_LEAVE_MULTIROOM,
            handle_leave_multiroom,
            schema=vol.Schema(
                {
                    vol.Optional("host"): cv.string,
                }
            ),
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
