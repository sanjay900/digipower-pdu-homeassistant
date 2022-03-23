"""Support for displaying collected data over SNMP."""
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

from homeassistant.components.sensor import (
    SensorEntity,
    DOMAIN as COMPONENT_DOMAIN
)

from .pdu import DigipowerPDU

from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_CURRENT,
)
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
    entities = [
        DigipowerCurrentSensor(coordinator, entry.entry_id, sensor)
    ]
    if sensor.has_humidity:
        entities.append(DigipowerHumiditySensor(coordinator, entry.entry_id, sensor))
        entities.append(DigipowerTemperatureSensor(coordinator, entry.entry_id, sensor))
    async_add_entities(
        entities
    )


class DigipowerHumiditySensor(CoordinatorEntity, SensorEntity):
    """Representation of a SNMP sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, device: DigipowerPDU):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._name = "{} - Humidity".format(device.devicename)
        self.entity_id = "{}.{}_humidity".format(COMPONENT_DOMAIN, device.devicename.lower().replace(" ","_"))
        self._device = device
        self._state = None
        self._unit_of_measurement = "%"
        self._attr_device_class = DEVICE_CLASS_HUMIDITY
        self._attr_native_unit_of_measurement = self._unit_of_measurement
        self._unique_id = "{}_{}_humidity".format(entry_id,device.mac)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.mac)},
            manufacturer="Digipower",
            model=device.model_number,
            name=device.devicename,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._device.humidity

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

class DigipowerTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SNMP sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, device: DigipowerPDU):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._name = "{} - Temperature".format(device.devicename)
        self.entity_id = "{}.{}_temperature".format(COMPONENT_DOMAIN, device.devicename.lower().replace(" ","_"))
        self._device = device
        self._state = None
        self._unit_of_measurement = "°C"
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_native_unit_of_measurement = self._unit_of_measurement
        self._unique_id = "{}_{}_temperature".format(entry_id,device.mac)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.mac)},
            manufacturer="Digipower",
            model=device.model_number,
            name=device.devicename,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._device.temperature

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

class DigipowerCurrentSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SNMP sensor."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry_id: str, device: DigipowerPDU):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._name = "{} - Current".format(device.devicename)
        self.entity_id = "{}.{}_current".format(COMPONENT_DOMAIN, device.devicename.lower().replace(" ","_"))
        self._device = device
        self._state = None
        self._unit_of_measurement = "A"
        self._attr_device_class = DEVICE_CLASS_CURRENT
        self._attr_native_unit_of_measurement = self._unit_of_measurement
        self._unique_id = "{}_{}_current".format(entry_id,device.mac)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.mac)},
            manufacturer="Digipower",
            model=device.model_number,
            name=device.devicename,
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._device.current

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement