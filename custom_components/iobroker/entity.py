"""Base entity for ioBroker states."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


def _build_device_info(obj_id: str, obj_meta: dict[str, Any]) -> DeviceInfo:
    """Build a DeviceInfo from the ioBroker object hierarchy.

    ioBroker state IDs are structured as:
        adapter.instance.channel.state
    We use the adapter + instance as the device identifier.
    """
    parts = obj_id.split(".")
    # Use first two segments (adapter.instance) as device id when possible
    device_id = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
    device_name = device_id

    # Try to get a nicer name from the channel/device object if available
    common = obj_meta.get("common", {})
    if isinstance(common.get("name"), str) and common["name"]:
        # Use the object's name if it looks like an overall device label
        pass

    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=device_name,
        manufacturer="ioBroker",
    )


class IoBrokerEntity(CoordinatorEntity):
    """Base entity for an ioBroker state."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        obj_id: str,
        obj_meta: dict[str, Any],
    ) -> None:
        """Initialise the entity."""
        super().__init__(coordinator)
        self._obj_id = obj_id
        self._obj_meta = obj_meta
        common: dict[str, Any] = obj_meta.get("common", {})

        self._attr_unique_id = f"{DOMAIN}_{obj_id}"

        raw_name = common.get("name", obj_id)
        self._attr_name = raw_name if isinstance(raw_name, str) else obj_id

        self._attr_device_info = _build_device_info(obj_id, obj_meta)

    @property
    def _state_data(self) -> dict[str, Any] | None:
        """Return the current state data from the coordinator."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._obj_id)

    @property
    def available(self) -> bool:
        """Return True when coordinator has data for this state."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._obj_id in self.coordinator.data
        )
