"""Binary sensor platform for ioBroker boolean read-only states."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, IOBROKER_DATATYPE_BOOLEAN
from .entity import IoBrokerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ioBroker binary sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    objects: dict[str, Any] = data["objects"]

    entities = []
    for obj_id, obj_meta in objects.items():
        common = obj_meta.get("common", {})
        datatype = common.get("type", "")
        # ioBroker default for common.write is True (writable); only False means read-only
        writable = common.get("write", True)

        # Binary sensor: boolean + explicitly NOT writable
        if datatype == IOBROKER_DATATYPE_BOOLEAN and not writable:
            entities.append(IoBrokerBinarySensor(coordinator, entry.entry_id, obj_id, obj_meta))

    async_add_entities(entities)


class IoBrokerBinarySensor(IoBrokerEntity, BinarySensorEntity):
    """A binary sensor representing a read-only boolean ioBroker state."""

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
