"""Number platform for ioBroker writable numeric states."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import IoBrokerApi
from .const import DOMAIN, IOBROKER_DATATYPE_NUMBER
from .entity import IoBrokerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ioBroker number entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api: IoBrokerApi = data["api"]
    objects: dict[str, Any] = data["objects"]

    entities = []
    for obj_id, obj_meta in objects.items():
        common = obj_meta.get("common", {})
        datatype = common.get("type", "")
        writable = common.get("write", True)

        if datatype == IOBROKER_DATATYPE_NUMBER and writable:
            entities.append(IoBrokerNumber(coordinator, api, obj_id, obj_meta))

    async_add_entities(entities)


class IoBrokerNumber(IoBrokerEntity, NumberEntity):
    """A number entity representing a writable numeric ioBroker state."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: Any,
        api: IoBrokerApi,
        obj_id: str,
        obj_meta: dict[str, Any],
    ) -> None:
        """Initialise the number entity."""
        super().__init__(coordinator, obj_id, obj_meta)
        self._api = api
        common = obj_meta.get("common", {})

        unit = common.get("unit")
        if unit:
            self._attr_native_unit_of_measurement = unit

        min_val = common.get("min")
        if min_val is not None:
            self._attr_native_min_value = float(min_val)

        max_val = common.get("max")
        if max_val is not None:
            self._attr_native_max_value = float(max_val)

        step = common.get("step")
        if step is not None:
            self._attr_native_step = float(step)

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        state_data = self._state_data
        if state_data is None:
            return None
        val = state_data.get("val")
        if val is None:
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the value in ioBroker."""
        await self._api.async_set_state(self._obj_id, value)
        await self.coordinator.async_request_refresh()
