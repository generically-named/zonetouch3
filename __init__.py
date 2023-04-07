import socket
import logging
import voluptuous as vol

from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery

DOMAIN = "zone_controller"
SERVICE_SET_ZONE = "set_zone"
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Required(CONF_PORT): cv.port,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    conf = config[DOMAIN]
    server_ip = conf[CONF_IP_ADDRESS]
    server_port = conf[CONF_PORT]

    def set_zone(call):
        zone = call.data.get("zone")
        state = call.data.get("state")
        _LOGGER.info(f"Setting zone {zone} to state {state}")

        response_hex = send_zone_command(server_ip, server_port, zone, state)
        _LOGGER.info(f"Response from server as raw TCP hex: {response_hex}")

    hass.services.register(DOMAIN, SERVICE_SET_ZONE, set_zone)

    return True

# The rest of the original code is included below, with slight modifications
# ... (original code)

def send_zone_command(server_ip, server_port, zone, state):
    state = "03" if state.lower() == "on" else "02"
    hex_data[19] = state
    hex_data[18] = zone
    data = hex_string(hex_data[4:22])
    checksum = hex_string(crc16_modbus(data))
    hex_data[22] = checksum[0:2]
    hex_data[23] = checksum[2:4]

    response_hex = send_hex_data(server_ip, server_port, hex_string(hex_data))
    return response_hex
