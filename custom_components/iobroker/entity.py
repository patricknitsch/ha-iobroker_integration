"""Base entity for ioBroker states."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


def _build_device_info(entry_id: str, obj_id: str) -> DeviceInfo:
    """Build a DeviceInfo from the ioBroker object hierarchy.

    ioBroker state IDs are structured as:
        adapter.instance.channel.state
    We use the adapter + instance as the device identifier, scoped to the
    config entry so that multiple ioBroker instances never share a device.
    """
    parts = obj_id.split(".")
    # Use first two segments (adapter.instance) as device label when possible
    device_label = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

    return DeviceInfo(
        # Scope the identifier to this config entry to avoid collisions
        # between multiple ioBroker instances with the same adapter/instance name.
        identifiers={(DOMAIN, f"{entry_id}_{device_label}")},
        name=device_label,
        manufacturer="ioBroker",
    )


class IoBrokerEntity(CoordinatorEntity):
    """Base entity for an ioBroker state."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id: str,
        obj_id: str,
        obj_meta: dict[str, Any],
    ) -> None:
        """Initialise the entity."""
        super().__init__(coordinator)
        self._obj_id = obj_id
        self._obj_meta = obj_meta
        common: dict[str, Any] = obj_meta.get("common", {})

        # Include entry_id so unique_ids are globally unique even when multiple
        # ioBroker instances expose states with the same obj_id.
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{obj_id}"

        raw_name = common.get("name", obj_id)
        self._attr_name = raw_name if isinstance(raw_name, str) else obj_id

        self._attr_device_info = _build_device_info(entry_id, obj_id)

        # Track the last-seen state so we can skip no-op updates.
        self._prev_state_data: dict[str, Any] | None = None

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

    def _handle_coordinator_update(self) -> None:
        """Write HA state only when this entity's ioBroker state actually changed."""
        new_state = self._state_data
        if new_state == self._prev_state_data:
            return
        self._prev_state_data = new_state
        self.async_write_ha_state()
