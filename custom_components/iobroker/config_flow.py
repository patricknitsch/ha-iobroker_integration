"""Config flow for the ioBroker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IoBrokerApi, IoBrokerConnectionError
from .const import CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


class IoBrokerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ioBroker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST]
            port: int = user_input[CONF_PORT]

            # Ensure a single entry per host:port
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = IoBrokerApi(host, port, session)

            try:
                reachable = await api.async_test_connection()
            except IoBrokerConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during ioBroker connection test")
                errors["base"] = "unknown"
            else:
                if not reachable:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=f"ioBroker ({host}:{port})",
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
