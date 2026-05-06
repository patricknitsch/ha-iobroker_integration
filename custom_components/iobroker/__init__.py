"""The ioBroker integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IoBrokerApi, IoBrokerApiError, IoBrokerConnectionError
from .const import (
    CATEGORY_DEFAULTS,
    CATEGORY_PREFIXES,
    CONF_HOST,
    CONF_INCLUDE_DEVICES,
    CONF_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    IOBROKER_TYPE_STATE,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


def _filter_by_categories(
    config: dict[str, Any], state_objects: dict[str, Any]
) -> dict[str, Any]:
    """Return only the state objects that belong to enabled categories.

    Categories map to ioBroker state-ID prefixes (e.g. ``system.`` for the
    *system* category).  The special *devices* category covers every state that
    does not match any of the known prefixes.
    """
    result: dict[str, Any] = {}
    for obj_id, obj in state_objects.items():
        matched_category: str | None = None
        for conf_key, prefixes in CATEGORY_PREFIXES.items():
            if any(obj_id.startswith(p) for p in prefixes):
                matched_category = conf_key
                break

        if matched_category is None:
            # Falls into the "devices" bucket
            enabled = config.get(
                CONF_INCLUDE_DEVICES, CATEGORY_DEFAULTS[CONF_INCLUDE_DEVICES]
            )
        else:
            enabled = config.get(
                matched_category, CATEGORY_DEFAULTS[matched_category]
            )

        if enabled:
            result[obj_id] = obj

    return result


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
        _LOGGER.error(
            "Cannot connect to ioBroker at %s:%s – check host/IP and port: %s",
            host,
            port,
            err,
        )
        raise ConfigEntryNotReady(f"Cannot connect to ioBroker: {err}") from err

    if not connected:
        _LOGGER.error(
            "ioBroker at %s:%s is not reachable – check host/IP and port",
            host,
            port,
        )
        raise ConfigEntryNotReady("ioBroker is not reachable")

    # Fetch objects once for metadata (roles, units, min/max, writable flag, etc.)
    try:
        objects: dict[str, Any] = await api.async_get_objects()
    except IoBrokerApiError as err:
        _LOGGER.error("Failed to load ioBroker objects from %s:%s: %s", host, port, err)
        raise ConfigEntryNotReady(f"Failed to load ioBroker objects: {err}") from err

    # Keep only "state" type objects, then filter by selected categories
    state_objects: dict[str, Any] = {
        obj_id: obj
        for obj_id, obj in objects.items()
        if obj.get("type") == IOBROKER_TYPE_STATE
    }

    # Options (set via the options flow) take precedence over initial data
    merged_config = {**entry.data, **entry.options}
    state_objects = _filter_by_categories(merged_config, state_objects)

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

    entry.async_on_unload(entry.add_update_listener(_async_reload_on_options_update))

    return True


async def _async_reload_on_options_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update – reload the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform(p) for p in PLATFORMS]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
