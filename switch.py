from homeassistant.components.switch import SwitchEntity
import logging

_LOGGER = logging.getLogger('custom_components.zonetouch3')

DOMAIN = "zonetouch3"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ZoneTouch3 switch platform."""
    controller = hass.data[DOMAIN]
    async_add_entities([ZoneSwitch(controller, zone) for zone in controller.zones])

class ZoneSwitch(SwitchEntity):
    def __init__(self, controller, zone):
        self.controller = controller
        self.zone = zone
        self._is_on = zone['state']

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self.zone['name']} Switch"

    @property
    def is_on(self):
        """Return true if the entity is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on asynchronously."""
        _LOGGER.warning("Turn on HERE")
        await self.controller.zone_on(self.zone['id'])
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.controller.zone_off(self.zone['id'])
        self._is_on = False

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.controller.async_add_listener(self._handle_coordinator_update))

    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        # Update the state, if the coordinator has new data for this zone
        if self.zone in self.controller.zones:
            self._state = True if self.zone['state'] == 'on' else False
            self.async_write_ha_state()
