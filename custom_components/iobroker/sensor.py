"""Sensor platform for ioBroker read-only numeric and string states."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    IOBROKER_DATATYPE_BOOLEAN,
    IOBROKER_DATATYPE_MIXED,
    IOBROKER_DATATYPE_NUMBER,
    IOBROKER_DATATYPE_STRING,
)
from .entity import IoBrokerEntity

_LOGGER = logging.getLogger(__name__)

_READ_ONLY_TYPES = {IOBROKER_DATATYPE_NUMBER, IOBROKER_DATATYPE_STRING, IOBROKER_DATATYPE_MIXED}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ioBroker sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    objects: dict[str, Any] = data["objects"]

    entities = []
    for obj_id, obj_meta in objects.items():
        common = obj_meta.get("common", {})
        datatype = common.get("type", "")
        writable = common.get("write", True)

        if datatype in _READ_ONLY_TYPES and not writable:
            entities.append(IoBrokerSensor(coordinator, obj_id, obj_meta))
        elif datatype == IOBROKER_DATATYPE_BOOLEAN and not writable:
            # Booleans are handled by binary_sensor; skip here
            pass
        elif datatype in _READ_ONLY_TYPES and writable:
            # Writable numbers are handled by number platform; we still expose a sensor
            # for types that have no dedicated writable platform (string, mixed).
            if datatype != IOBROKER_DATATYPE_NUMBER:
                entities.append(IoBrokerSensor(coordinator, obj_id, obj_meta))

    async_add_entities(entities)


class IoBrokerSensor(IoBrokerEntity, SensorEntity):
    """A sensor representing a numeric or string ioBroker state."""

    def __init__(self, coordinator: Any, obj_id: str, obj_meta: dict[str, Any]) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, obj_id, obj_meta)
        common = obj_meta.get("common", {})
        datatype = common.get("type", "")

        unit = common.get("unit")
        if unit:
            self._attr_native_unit_of_measurement = unit

        if datatype == IOBROKER_DATATYPE_NUMBER:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        """Return the current state value."""
        state_data = self._state_data
        if state_data is None:
            return None
        return state_data.get("val")
