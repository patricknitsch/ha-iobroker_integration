"""Constants for the ioBroker integration."""

DOMAIN = "iobroker"

DEFAULT_HOST = "3a1c5d11-iobroker"
DEFAULT_PORT = 8087
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 3600

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

# Category filter config keys
CONF_INCLUDE_SYSTEM = "include_system"
CONF_INCLUDE_ADMIN = "include_admin"
CONF_INCLUDE_USERDATA = "include_userdata"
CONF_INCLUDE_DEVICES = "include_devices"
CONF_INCLUDE_DISCOVERY = "include_discovery"
CONF_INCLUDE_SIMPLE_API = "include_simple_api"
CONF_INCLUDE_HASS = "include_hass"

# ioBroker state-ID prefixes per category
CATEGORY_PREFIXES: dict[str, tuple[str, ...]] = {
    CONF_INCLUDE_SYSTEM: ("system.",),
    CONF_INCLUDE_ADMIN: ("admin.",),
    CONF_INCLUDE_USERDATA: ("0_userdata.",),
    CONF_INCLUDE_DISCOVERY: ("discovery.",),
    CONF_INCLUDE_SIMPLE_API: ("simple-api.",),
    CONF_INCLUDE_HASS: ("hass.",),
    # CONF_INCLUDE_DEVICES has no fixed prefix – it covers everything else
}

# Default values for each optional category
CATEGORY_DEFAULTS: dict[str, bool] = {
    CONF_INCLUDE_SYSTEM: True,
    CONF_INCLUDE_ADMIN: False,
    CONF_INCLUDE_USERDATA: True,
    CONF_INCLUDE_DEVICES: True,
    CONF_INCLUDE_DISCOVERY: False,
    CONF_INCLUDE_SIMPLE_API: False,
    CONF_INCLUDE_HASS: False,
}

# ioBroker object types
IOBROKER_TYPE_STATE = "state"

# ioBroker common.type values
IOBROKER_DATATYPE_BOOLEAN = "boolean"
IOBROKER_DATATYPE_NUMBER = "number"
IOBROKER_DATATYPE_STRING = "string"
IOBROKER_DATATYPE_MIXED = "mixed"

PLATFORMS = ["binary_sensor", "sensor", "switch", "number"]
