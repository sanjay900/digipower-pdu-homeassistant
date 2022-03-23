"""Support for SNMP enabled switch."""
import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    CONF_HOST,
    CONF_NAME,
    CONF_PAYLOAD_OFF,
    CONF_PAYLOAD_ON,
    CONF_PORT,
    CONF_USERNAME,
)
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_AUTH_KEY,
    CONF_AUTH_PROTOCOL,
    CONF_BASEOID,
    CONF_COMMUNITY,
    CONF_PRIV_KEY,
    CONF_PRIV_PROTOCOL,
    CONF_VARTYPE,
    CONF_VERSION,
    DEFAULT_AUTH_PROTOCOL,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_PRIV_PROTOCOL,
    DEFAULT_VARTYPE,
    DEFAULT_VERSION,
    MAP_AUTH_PROTOCOLS,
    MAP_PRIV_PROTOCOLS,
    SNMP_VERSIONS,
)



PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_COMMUNITY, default=DEFAULT_COMMUNITY): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


async def async_get(request_args, oid):
    errindication, errstatus, errindex, restable = await getCmd(
        *request_args, ObjectType(ObjectIdentity(oid))
    )
    if errindication:
        _LOGGER.error("SNMP error: %s", errindication)
    elif errstatus:
        _LOGGER.error(
            "SNMP error: %s at %s",
            errstatus.prettyPrint(),
            errindex and restable[-1][int(errindex) - 1] or "?",
        )
    else:
        return restable[0][-1]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the SNMP switch."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    community = config.get(CONF_COMMUNITY)
    request_args = [
        SnmpEngine(),
        CommunityData(community, mpModel=SNMP_VERSIONS["1"]),
        UdpTransportTarget((host, port)),
        ContextData(),
    ]
    switchCount = await async_get(request_args, "1.3.6.1.2.1.1.7.0") or 0
    mac = await async_get(request_args, "1.3.6.1.4.1.17420.1.2.3.0") or 0
    switches = []
    devicename = str(await async_get(request_args, "1.3.6.1.2.1.1.5.0")) or ""
    for x in range(1, switchCount + 2):
        oid = "1.3.6.1.4.1.17420.1.2.9.1.14.%d.0" % x
        name = str(((await async_get(request_args, oid)) or OctetString())).split(",")[
            0
        ]
        switches.append(
            SnmpSwitch(devicename + " - " + name, host, port, community, x - 1, mac)
        )

    async_add_entities(
        switches,
        True,
    )


class SnmpSwitch(SwitchEntity):
    """Representation of a SNMP switch."""

    def __init__(self, name, host, port, community, id, mac):
        """Initialize the switch."""

        self._unique_id = "%s-%d" % (mac, id)

        self._id = id
        self._name = name

        self._state = None
        self._tempState = None
        self._request_args = [
            SnmpEngine(),
            CommunityData(community, mpModel=SNMP_VERSIONS["1"]),
            UdpTransportTarget((host, port)),
            ContextData(),
        ]

    async def get_current(self):
        errindication, errstatus, errindex, restable = await getCmd(
            *self._request_args,
            ObjectType(ObjectIdentity("1.3.6.1.4.1.17420.1.2.9.1.13.0")),
        )

        if errindication:
            _LOGGER.error("SNMP error: %s", errindication)
        elif errstatus:
            _LOGGER.error(
                "SNMP error: %s at %s",
                errstatus.prettyPrint(),
                errindex and restable[-1][int(errindex) - 1] or "?",
            )
        else:
            return str(restable[0][-1]).split(",")

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        await self._set(False)

    async def async_update(self):
        """Update the state."""
        self._state = (await self.get_current())[self._id] == "1"
        # It takes the PDU a while to update its state, so we want to force it when we toggle state.
        if self._tempState != None:
            if self._tempState == self._state:
                self._tempState = None
            else:
                self._state = self._tempState

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
        return self._state

    async def _set(self, value):
        self._tempState = value
        current = await self.get_current()
        current[self._id] = str(int(value))
        await setCmd(
            *self._request_args,
            ObjectType(
                ObjectIdentity("1.3.6.1.4.1.17420.1.2.9.1.13.0"),
                OctetString(",".join(current)),
            ),
        )
