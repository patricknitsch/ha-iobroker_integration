"""Config flow for the ioBroker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import IoBrokerApi, IoBrokerConnectionError
from .const import (
    CATEGORY_DEFAULTS,
    CONF_HOST,
    CONF_INCLUDE_ADMIN,
    CONF_INCLUDE_DEVICES,
    CONF_INCLUDE_DISCOVERY,
    CONF_INCLUDE_HASS,
    CONF_INCLUDE_SIMPLE_API,
    CONF_INCLUDE_SYSTEM,
    CONF_INCLUDE_USERDATA,
    CONF_PORT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


def _categories_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_INCLUDE_SYSTEM, default=CATEGORY_DEFAULTS[CONF_INCLUDE_SYSTEM]
            ): bool,
            vol.Required(
                CONF_INCLUDE_ADMIN, default=CATEGORY_DEFAULTS[CONF_INCLUDE_ADMIN]
            ): bool,
            vol.Required(
                CONF_INCLUDE_USERDATA, default=CATEGORY_DEFAULTS[CONF_INCLUDE_USERDATA]
            ): bool,
            vol.Required(
                CONF_INCLUDE_DEVICES, default=CATEGORY_DEFAULTS[CONF_INCLUDE_DEVICES]
            ): bool,
            vol.Required(
                CONF_INCLUDE_DISCOVERY, default=CATEGORY_DEFAULTS[CONF_INCLUDE_DISCOVERY]
            ): bool,
            vol.Required(
                CONF_INCLUDE_SIMPLE_API, default=CATEGORY_DEFAULTS[CONF_INCLUDE_SIMPLE_API]
            ): bool,
            vol.Required(
                CONF_INCLUDE_HASS, default=CATEGORY_DEFAULTS[CONF_INCLUDE_HASS]
            ): bool,
        }
    )


class IoBrokerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ioBroker."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> IoBrokerOptionsFlowHandler:
        """Return the options flow handler."""
        return IoBrokerOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str = ""
        self._port: int = DEFAULT_PORT

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step (host + port)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST].strip()
            port: int = user_input[CONF_PORT]

            if not host or ".." in host or host.startswith(".") or host.endswith("."):
                errors[CONF_HOST] = "invalid_host"
                return self.async_show_form(
                    step_id="user",
                    data_schema=STEP_USER_DATA_SCHEMA,
                    errors=errors,
                )

            # Ensure a single entry per host:port
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = IoBrokerApi(host, port, session)

            try:
                reachable = await api.async_test_connection()
            except IoBrokerConnectionError as err:
                _LOGGER.error(
                    "Connection to ioBroker at %s:%s failed: %s – "
                    "Make sure the simple-api adapter is installed and running in ioBroker "
                    "(Adapters → simple-api, default port 8087)",
                    host,
                    port,
                    err,
                )
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during ioBroker connection test")
                errors["base"] = "unknown"
            else:
                if not reachable:
                    _LOGGER.error(
                        "ioBroker at %s:%s did not respond – "
                        "Make sure the simple-api adapter is installed and running "
                        "(Adapters → simple-api, default port 8087)",
                        host,
                        port,
                    )
                    errors["base"] = "cannot_connect"
                else:
                    self._host = host
                    self._port = port
                    return await self.async_step_categories()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the category selection step."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"ioBroker ({self._host}:{self._port})",
                data={
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    **user_input,
                },
            )

        return self.async_show_form(
            step_id="categories",
            data_schema=_categories_schema(),
        )


class IoBrokerOptionsFlowHandler(OptionsFlow):
    """Handle ioBroker options flow for reconfiguring data category visibility toggles."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the ioBroker options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        # Use current options, fall back to values stored in entry.data
        current = {**self.config_entry.data, **self.config_entry.options}

        def _current(key: str) -> bool:
            return current.get(key, CATEGORY_DEFAULTS[key])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_INCLUDE_SYSTEM, default=_current(CONF_INCLUDE_SYSTEM)): bool,
                    vol.Required(CONF_INCLUDE_ADMIN, default=_current(CONF_INCLUDE_ADMIN)): bool,
                    vol.Required(CONF_INCLUDE_USERDATA, default=_current(CONF_INCLUDE_USERDATA)): bool,
                    vol.Required(CONF_INCLUDE_DEVICES, default=_current(CONF_INCLUDE_DEVICES)): bool,
                    vol.Required(CONF_INCLUDE_DISCOVERY, default=_current(CONF_INCLUDE_DISCOVERY)): bool,
                    vol.Required(CONF_INCLUDE_SIMPLE_API, default=_current(CONF_INCLUDE_SIMPLE_API)): bool,
                    vol.Required(CONF_INCLUDE_HASS, default=_current(CONF_INCLUDE_HASS)): bool,
                }
            ),
        )
