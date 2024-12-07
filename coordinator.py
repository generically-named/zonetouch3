import asyncio
from . import zoneTouch3Library
from homeassistant.core import HomeAssistant, Config
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
import logging

DOMAIN = "zonetouch3"
CONTROLLER_IP = "10.0.2.125"
CONTROLLER_PORT = 7030

_LOGGER = logging.getLogger('custom_components.zonetouch3')



class ZoneTouch3Controller(DataUpdateCoordinator):
    """Class to manage communication with Zone Touch 3 controller."""
    def __init__(self, hass, ip, port):
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name="ZoneTouch3Controller",
            update_interval=timedelta(seconds=30),  # Adjust as needed
        )
        self.ip = ip
        self.port = port
        self.zones = []
        self._listeners = []

    def async_add_listener(self, listener_callback):
        """Add a listener for data updates."""
        self._listeners.append(listener_callback)
        _LOGGER.debug("Added callback")

    def async_remove_listener(self, listener_callback):
        """Remove a listener."""
        self._listeners.remove(listener_callback)

    async def _notify_listeners(self):
        """Notify all listeners about data update."""
        for listener in self._listeners:
            listener()
        _LOGGER.debug("Listeners from _notify_listeners")
        _LOGGER.debug(self._listeners)
    
    async def _async_update_data(self):
        """Update data and notify listeners."""
        await self.async_update_zone_info()
        await self._notify_listeners()

    async def async_initialize(self):
        """Initialize connection to the controller and discover zones."""
        # Implement TCP connection logic here
        # Parse the response to populate self.zones
        # This is a dummy implementation:
        message = [0x55,0x55,0x55,0xAA,0x90,0xB0,0x07,0x1F,0x00,0x02,0xFF,0xF0]
        messageToBeSent = zoneTouch3Library.format_message(message)
        receivedData = await zoneTouch3Library.send_message(messageToBeSent,CONTROLLER_IP,CONTROLLER_PORT)
        processedData = zoneTouch3Library.process_extended_response(receivedData)
        for i in processedData:
            self.zones.append(i)
        _LOGGER.debug("Initialisation")
        _LOGGER.debug(self.zones)
        
    async def receive_data(self):
        try:
            while True:
                data = await self.reader.read(348)  # adjust buffer size based on your needs
                if not data:
                    raise ConnectionError("Connection lost")
                await self.handle_data(data)
                await self._notify_listeners()
        except ConnectionError:
            await self.reconnect()
    
    async def handle_data (self,data):
        if data[9:10] == 'b0' and data[11:12] == '80':
            processedData = zoneTouch3Library.process_status_response(data)
            for i in self.zones:
                for j in processedData:
                    if i['id'] == j['id']:
                        #{'id': id, 'state': status, 'percentage': percent, 'spill': spill, 'turbo': turbo}
                        i['state'] = j['state']
                        i['percentage'] = j['percentage']
                        i['spill'] = j['spill']
                        i['turbo'] = j['turbo']
        elif data[9:10] == 'b0' and data[11:12] == '90':
            processedData = zoneTouch3Library.process_extended_response(data)
            for i in self.zones:
                for j in processedData:
                    if i['id'] == j['id']:
                        #{'id': id, 'name': name, 'state': status, 'percentage': percent, 'spill': spill, 'turbo': turbo, 'supports_turbo': supports_turbo}
                        i['name'] = j['name']
                        i['state'] = j['state']
                        i['percentage'] = j['percentage']
                        i['spill'] = j['spill']
                        i['turbo'] = j['turbo']
                        i['supports_turbo'] = j['supports_turbo']


    async def async_update_zone_info(self):
        message = [0x55,0x55,0x55,0xAA,0x90,0xB0,0x07,0x1F,0x00,0x02,0xFF,0xF0]
        messageToBeSent = zoneTouch3Library.format_message(message)
        receivedData = await zoneTouch3Library.send_message(messageToBeSent,CONTROLLER_IP,CONTROLLER_PORT)
        processedData = zoneTouch3Library.process_extended_response(receivedData)
        await self.handle_data(processedData)
        _LOGGER.info("Update zones")
        _LOGGER.info(self.zones)
        await self._notify_listeners()

    async def zone_on(self,zone_id):
        processed_msg = await zoneTouch3Library.control_message_assembler(zone_id,"on")
        received_data = await zoneTouch3Library.send_message(processed_msg,CONTROLLER_IP,CONTROLLER_PORT)
        await self.handle_data(received_data)
        await self._notify_listeners()
        _LOGGER.debug("Received data (turn on):" + received_data)

    async def zone_off(self,zone_id):
        processed_msg = await zoneTouch3Library.control_message_assembler(zone_id,"off")
        received_data = await zoneTouch3Library.send_message(processed_msg,CONTROLLER_IP,CONTROLLER_PORT)
        await self.handle_data(received_data)
        await self._notify_listeners()
        _LOGGER.debug("Received data (turn off):" + received_data)
    
    async def zone_set_percentage(self,zone_id,percentage: int):
        processed_msg = await zoneTouch3Library.control_message_assembler(zone_id,"set",percentage)
        received_data = await zoneTouch3Library.send_message(processed_msg,CONTROLLER_IP,CONTROLLER_PORT)
        await self.handle_data(received_data)
        await self._notify_listeners()
        _LOGGER.debug("Received data (set percentage):" + received_data)
        
