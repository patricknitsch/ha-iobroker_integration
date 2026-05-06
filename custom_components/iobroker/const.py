"""Constants for the ioBroker integration."""

DOMAIN = "iobroker"

DEFAULT_HOST = "3a1c5d11-iobroker"
DEFAULT_PORT = 8087
DEFAULT_SCAN_INTERVAL = 30

CONF_HOST = "host"
CONF_PORT = "port"

# ioBroker object types
IOBROKER_TYPE_STATE = "state"

# ioBroker common.type values
IOBROKER_DATATYPE_BOOLEAN = "boolean"
IOBROKER_DATATYPE_NUMBER = "number"
IOBROKER_DATATYPE_STRING = "string"
IOBROKER_DATATYPE_MIXED = "mixed"

PLATFORMS = ["binary_sensor", "sensor", "switch", "number"]
