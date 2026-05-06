"""The ioBroker integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IoBrokerApi, IoBrokerApiError, IoBrokerConnectionError
from .const import (
    CONF_HOST,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    IOBROKER_TYPE_STATE,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ioBroker from a config entry."""
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]

    session = async_get_clientsession(hass)
    api = IoBrokerApi(host, port, session)

    # Test connection
    try:
        connected = await api.async_test_connection()
    except IoBrokerConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to ioBroker: {err}") from err

    if not connected:
        raise ConfigEntryNotReady("ioBroker is not reachable")

    # Fetch objects once for metadata (roles, units, min/max, writable flag, etc.)
    try:
        objects: dict[str, Any] = await api.async_get_objects()
    except IoBrokerApiError as err:
        raise ConfigEntryNotReady(f"Failed to load ioBroker objects: {err}") from err

    # Keep only "state" type objects
    state_objects: dict[str, Any] = {
        obj_id: obj
        for obj_id, obj in objects.items()
        if obj.get("type") == IOBROKER_TYPE_STATE
    }

    async def _async_update_data() -> dict[str, Any]:
        """Fetch current state values from ioBroker."""
        try:
            return await api.async_get_states()
        except IoBrokerConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except IoBrokerApiError as err:
            raise UpdateFailed(f"API error: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"ioBroker ({host}:{port})",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Perform first refresh
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "objects": state_objects,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(p) for p in PLATFORMS]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform(p) for p in PLATFORMS]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
