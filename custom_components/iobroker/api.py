"""ioBroker REST API client (simple-api adapter)."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp


class IoBrokerApiError(Exception):
    """General API error."""


class IoBrokerConnectionError(IoBrokerApiError):
    """Connection error."""


class IoBrokerApi:
    """Client for the ioBroker simple-api REST adapter."""

    def __init__(
        self,
        host: str,
        port: int,
        session: aiohttp.ClientSession,
        timeout: int = 10,
    ) -> None:
        """Initialize the API client."""
        self._base_url = f"http://{host}:{port}"
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _request(self, path: str, params: dict | None = None) -> Any:
        """Perform a GET request and return parsed JSON."""
        url = f"{self._base_url}{path}"
        try:
            async with self._session.get(
                url, params=params, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                try:
                    return await response.json(content_type=None)
                except ValueError as err:
                    raise IoBrokerApiError(
                        f"Invalid JSON response from ioBroker at {url}"
                    ) from err
        except aiohttp.ClientConnectionError as err:
            raise IoBrokerConnectionError(
                f"Cannot connect to ioBroker at {url}: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise IoBrokerConnectionError(
                f"Timeout connecting to ioBroker at {url}"
            ) from err
        except aiohttp.ClientResponseError as err:
            raise IoBrokerApiError(
                f"Error response from ioBroker ({err.status}): {err.message}"
            ) from err

    async def async_get_states(self, pattern: str = "*") -> dict[str, Any]:
        """Return all states matching the pattern.

        Returns a dict keyed by state ID.
        """
        data = await self._request("/states", {"pattern": pattern})
        if isinstance(data, dict):
            return data
        return {}

    async def async_get_objects(self, pattern: str = "*") -> dict[str, Any]:
        """Return all objects matching the pattern.

        Returns a dict keyed by object ID.
        """
        data = await self._request("/objects", {"pattern": pattern})
        if isinstance(data, dict):
            return data
        return {}

    async def async_get_state(self, state_id: str) -> dict[str, Any]:
        """Return a single state by ID."""
        data = await self._request(f"/get/{state_id}")
        if isinstance(data, dict):
            return data
        return {}

    async def async_set_state(self, state_id: str, value: Any) -> None:
        """Set a state value via the simple-api set endpoint."""
        url = f"{self._base_url}/set/{state_id}"
        params: dict[str, Any] = {"value": value}
        try:
            async with self._session.get(
                url, params=params, timeout=self._timeout
            ) as response:
                response.raise_for_status()
        except aiohttp.ClientConnectionError as err:
            raise IoBrokerConnectionError(
                f"Cannot connect to ioBroker at {url}: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise IoBrokerConnectionError(
                f"Timeout connecting to ioBroker at {url}"
            ) from err
        except aiohttp.ClientResponseError as err:
            raise IoBrokerApiError(
                f"Error response from ioBroker ({err.status}): {err.message}"
            ) from err

    async def async_test_connection(self) -> bool:
        """Test the connection by fetching a minimal states response.

        The /states endpoint is guaranteed to return JSON (an object), making it
        a safe connection probe. The /help endpoint returns plain text which would
        cause a JSON decode error in _request().
        """
        try:
            # Use a narrow pattern to minimise the response payload
            await self._request("/states", {"pattern": "system.adapter.admin.0.alive"})
            return True
        except IoBrokerApiError:
            return False
