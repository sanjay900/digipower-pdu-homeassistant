"""The PDU component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    Platform,
    CONF_PORT,
    CONF_HOST
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .pdu import DigipowerPDU
from .const import DOMAIN, LOGGER, SERVICE_PDU, SCAN_INTERVAL, CONF_COMMUNITY

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    community = entry.data[CONF_COMMUNITY]
    sensor = DigipowerPDU(host, port, community)
    pdu_update: DataUpdateCoordinator[DigipowerPDU] = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_{SERVICE_PDU}",
        update_interval=SCAN_INTERVAL,
        update_method=sensor.update,
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = pdu_update
    await pdu_update.async_config_entry_first_refresh()

    # It's done by calling the `async_setup_entry` function in each platform module.
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    hass.data[DOMAIN][entry.entry_id].close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
