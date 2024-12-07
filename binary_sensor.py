from homeassistant.components.binary_sensor import BinarySensorEntity

DOMAIN = "zonetouch3"
CONTROLLER_IP = "10.0.2.125"
CONTROLLER_PORT = 7030

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the binary sensor platform."""
    # Example: create a binary sensor instance
    controller = hass.data[DOMAIN]
    async_add_entities([SpillZoneActiveSensor(controller, zone) for zone in controller.zones])

class SpillZoneActiveSensor(BinarySensorEntity):
    def __init__(self, controller, zone):
        self.controller = controller
        self.zone = zone
        self._name = zone['name'] + " Spill"
        self._state = zone['spill']

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of this device, from DEVICE_CLASSES."""
        # You can set this to any of the Home Assistant binary sensor device classes like 'motion', 'moisture', etc.
        return 'None'
    
    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.controller.async_add_listener(self._handle_coordinator_update))

    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        # Update the state, if the coordinator has new data for this zone
        if self.zone in self.controller.zones:
            self._state = self.zone['spill']
            self.async_write_ha_state()
