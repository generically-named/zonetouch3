import asyncio
from . import zoneTouch3Library
from . import coordinator
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.discovery import async_load_platform
import logging
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger('custom_components.zonetouch3')

DOMAIN = "zonetouch3"
CONTROLLER_IP = "10.0.2.125"
CONTROLLER_PORT = 7030

async def async_setup(hass: HomeAssistant, config: Config):
    """Set up the ZoneTouch3 component."""
    controller = coordinator.ZoneTouch3Controller(hass, CONTROLLER_IP, CONTROLLER_PORT)
    await controller.async_initialize()

    hass.data[DOMAIN] = controller

    # Load platforms with discovered zone data
    for platform in ("switch", "number","binary_sensor"):
        hass.async_create_task(
            async_load_platform(hass, platform, DOMAIN, {}, config)
        )

    return True
