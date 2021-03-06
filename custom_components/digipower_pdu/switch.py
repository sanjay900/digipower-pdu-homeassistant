"""Support for SNMP enabled switch."""
import logging

import voluptuous as vol

from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import homeassistant.helpers.config_validation as cv

import voluptuous as vol

from homeassistant.components.switch import (
    SwitchEntity,
    DOMAIN as COMPONENT_DOMAIN
)

from .pdu import DigipowerPDU

import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor: DigipowerPDU = hass.data[DOMAIN][entry.entry_id].data
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        
    async_add_entities(
        DigipowerPort(coordinator, entry.entry_id, sensor, port)
        for port in range(sensor.port_count)
    )


class DigipowerPort(CoordinatorEntity, SwitchEntity):
    """Representation of a digipower port."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, device: DigipowerPDU, port: int):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._name = device.get_port_name(port)
        self.entity_id = "{}.{}_port_{}".format(COMPONENT_DOMAIN, device.devicename.lower().replace(" ","_"),chr(ord('a')+port))
        self._device = device
        self._port = port
        self._unique_id = "{}_{}_port_{}".format(entry_id,device.mac,chr(ord('a')+port))
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.mac)},
            manufacturer="Digipower",
            model=device.model_number,
            name=device.devicename,
        )

    def turn_on(self, **kwargs):
        """Turn on the switch."""
        self._device.set_port_state(self._port, True)

    def turn_off(self, **kwargs):
        """Turn off the switch."""
        self._device.set_port_state(self._port, False)

    @property
    def name(self):
        """Return the switch's name."""
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        """Return true if switch is on; False if off. None if unknown."""
        return self._device.get_port_state(self._port)
