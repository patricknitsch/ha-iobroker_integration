# ha-iobroker_integration

A Home Assistant custom integration that communicates with the [ioBroker HA App](https://github.com/klein0r/ha-app-iobroker) and automatically discovers all ioBroker states as Home Assistant entities.

## Features

- Auto-discovery of all ioBroker states via the **simple-api** adapter (REST, port 8087)
- Maps ioBroker data types to Home Assistant entity platforms:
  - **Writable boolean** → `switch`
  - **Read-only boolean** → `binary_sensor`
  - **Writable number** → `number` (with min/max/step/unit support)
  - **Read-only number / string / mixed** → `sensor`
- UI-based configuration flow (Settings → Integrations → Add Integration → ioBroker)
- Polling-based state updates (default: every 30 s)
- Device grouping by ioBroker adapter instance

## Prerequisites

1. Install the [ioBroker HA App](https://github.com/klein0r/ha-app-iobroker) in Home Assistant
2. Enable the **simple-api** adapter inside ioBroker (it listens on port **8087** by default)

## Installation

### Manual (HACS-ready structure)

1. Copy the `custom_components/iobroker/` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Integrations → Add Integration** and search for **ioBroker**.
4. Enter the hostname (default: `3a1c5d11-iobroker` when using the HA App) and port (default: `8087`).

### HACS (recommended)

Add this repository as a custom repository in HACS and install the **ioBroker** integration.

## Configuration

| Field    | Default                | Description                           |
|----------|------------------------|---------------------------------------|
| Hostname | `3a1c5d11-iobroker`    | Hostname or IP of the ioBroker server |
| Port     | `8087`                 | Port of the simple-api adapter        |

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
