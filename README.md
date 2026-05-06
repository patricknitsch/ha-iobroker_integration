# ha-iobroker_integration

<img src="custom_components/iobroker/icon.png" alt="ioBroker Integration" width="80"/>

A Home Assistant custom integration that communicates with ioBroker and automatically discovers all selected ioBroker states as Home Assistant entities.

## Features

- Auto-discovery of ioBroker states via the **simple-api** adapter (REST, port 8087)
- Maps ioBroker data types to Home Assistant entity platforms:
  - **Writable boolean** → `switch`
  - **Read-only boolean** → `binary_sensor`
  - **Writable number** → `number` (with min/max/step/unit support)
  - **Read-only number / string / mixed** → `sensor`
- UI-based configuration flow (Settings → Integrations → Add Integration → ioBroker)
- Category selection: choose which ioBroker data groups to import
- **Configurable polling interval** (default: 30 s, minimum: 5 s)
- Automatic entity cleanup: entities from deselected categories are removed when the configuration is saved
- Only entities whose state value has actually changed are updated in Home Assistant
- Device grouping by ioBroker adapter instance

## Prerequisites

### Install the simple-api adapter in ioBroker

This integration communicates exclusively with the **ioBroker simple-api adapter** via HTTP/REST on port **8087** (default).

> **Important:** Without the simple-api adapter the integration cannot connect.  
> Port 8081 is the ioBroker *Admin* web UI — it is **not** used by this integration.

Steps to install it:

1. Open ioBroker → **Adapters**
2. Search for **simple-api** and install it
3. Start the adapter instance — it will listen on port **8087**
4. Verify: open `http://<iobroker-host>:8087/states?pattern=system.adapter.admin.0.alive` in a browser; it should return JSON

## Installation

### Manual (HACS-ready structure)

1. Copy the `custom_components/iobroker/` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **ioBroker**.
4. Enter the hostname (default: `3a1c5d11-iobroker` when using the HA App) and port (default: `8087`).
5. Select which data categories to import (see below).

### HACS (recommended)

Add this repository as a custom repository in HACS and install the **ioBroker** integration.

## Configuration

### Step 1 – Connection

| Field    | Default                | Description                                   |
|----------|------------------------|-----------------------------------------------|
| Hostname | `3a1c5d11-iobroker`    | Hostname or IP of the ioBroker server         |
| Port     | `8087`                 | Port of the **simple-api adapter** (not 8081) |

### Step 2 – Data categories

Choose which ioBroker state categories should be imported as HA entities:

| Toggle | ioBroker prefix | Default | Description |
|---|---|---|---|
| System data | `system.*` | ✅ on | Core ioBroker system states (uptime, memory, etc.) |
| Admin | `admin.*` | ☐ off | Admin adapter states |
| User data | `0_userdata.*` | ✅ on | Custom user-defined states |
| Devices | *(all others)* | ✅ on | All connected device adapters (Homematic, Zigbee, …) |
| Discovery | `discovery.*` | ☐ off | Discovery adapter states |
| Simple-API | `simple-api.*` | ☐ off | Simple-API adapter internal states |
| Hass | `hass.*` | ☐ off | Hass adapter states |

| Setting | Default | Description |
|---|---|---|
| Polling interval | `30` | How often (in seconds) HA polls ioBroker for state updates (min: 5, max: 3600) |

> **Note:** When you change the category selection and save the options, entities from deselected categories are automatically removed and entities from newly selected categories are automatically imported.

## Port reference

| Port | Service | Used by this integration |
|------|---------|--------------------------|
| 8081 | ioBroker Admin web UI | ❌ No |
| 8087 | simple-api REST adapter | ✅ **Yes** |

## Entity mapping

| ioBroker `common.type` | Writable | HA platform      |
|------------------------|----------|------------------|
| `boolean`              | yes      | `switch`         |
| `boolean`              | no       | `binary_sensor`  |
| `number`               | yes      | `number`         |
| `number`               | no       | `sensor`         |
| `string` / `mixed`     | any      | `sensor`         |

## License

MIT
