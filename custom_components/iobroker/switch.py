"""Switch platform for ioBroker writable boolean states."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import IoBrokerApi
from .const import DOMAIN, IOBROKER_DATATYPE_BOOLEAN
from .entity import IoBrokerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ioBroker switches."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api: IoBrokerApi = data["api"]
    objects: dict[str, Any] = data["objects"]

    entities = []
    for obj_id, obj_meta in objects.items():
        common = obj_meta.get("common", {})
        datatype = common.get("type", "")
        writable = common.get("write", True)

        if datatype == IOBROKER_DATATYPE_BOOLEAN and writable:
            entities.append(IoBrokerSwitch(coordinator, api, obj_id, obj_meta))

    async_add_entities(entities)


class IoBrokerSwitch(IoBrokerEntity, SwitchEntity):
    """A switch representing a writable boolean ioBroker state."""

    def __init__(
        self,
        coordinator: Any,
        api: IoBrokerApi,
        obj_id: str,
        obj_meta: dict[str, Any],
    ) -> None:
        """Initialise the switch."""
        super().__init__(coordinator, obj_id, obj_meta)
        self._api = api

    @property
    def is_on(self) -> bool | None:
        """Return True if the state value is truthy."""
        state_data = self._state_data
        if state_data is None:
            return None
        val = state_data.get("val")
        if val is None:
            return None
        return bool(val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._api.async_set_state(self._obj_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._api.async_set_state(self._obj_id, False)
        await self.coordinator.async_request_refresh()
