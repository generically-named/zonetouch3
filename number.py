import logging
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

DOMAIN = "zonetouch3"
CONTROLLER_IP = "10.0.2.125"
CONTROLLER_PORT = 7030

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Zone Percentage Number entities based on the setup from __init__.py."""
    if discovery_info is None:
        return
    coordinator = hass.data[DOMAIN]
    zones = coordinator.zones  # Assuming this is how you retrieve zone info
    add_entities([ZonePercentage(coordinator, zone) for zone in zones])

class ZonePercentage(NumberEntity, CoordinatorEntity):
    """Representation of a Number entity that controls the percentage for a zone."""

    def __init__(self, coordinator, zone):
        """Initialize the number entity for a specific zone."""
        super().__init__(coordinator, context = zone)
        self.zone = zone
        self._value = self.zone['percentage']  # Default value or retrieve initial state from coordinator

    @property
    def name(self):
        """Return the name of the entity."""
        return f"Zone {self.zone['name']} Percentage"

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return 0.0

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return 100.0

    @property
    def native_step(self):
        """Return the increment/decrement step."""
        return 1.0

    @property
    def native_value(self):
        """Return the entity's current value."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """This could optionally return a unit of measurement, if relevant."""
        return "%"

    async def async_set_native_value(self, value):
        """Update the current value."""
        self._value = value
        await self.coordinator.zone_set_percentage(self.zone['id'], int(value))
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._value = self.coordinator.data[self.zone]['percentage']
        self.async_write_ha_state()
