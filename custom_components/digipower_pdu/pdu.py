
from enum import Enum
import pysnmp.hlapi.asyncio as hlapi
from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    UsmUserData,
    getCmd,
    setCmd
)
from pysnmp.proto.rfc1902 import (
    Counter32,
    Counter64,
    Gauge32,
    Integer,
    Integer32,
    IpAddress,
    Null,
    ObjectIdentifier,
    OctetString,
    Opaque,
    TimeTicks,
    Unsigned32,
)


from const import (
    CONF_ACCEPT_ERRORS,
    CONF_AUTH_KEY,
    CONF_AUTH_PROTOCOL,
    CONF_BASEOID,
    CONF_COMMUNITY,
    CONF_DEFAULT_VALUE,
    CONF_PRIV_KEY,
    CONF_PRIV_PROTOCOL,
    CONF_VERSION,
    DEFAULT_AUTH_PROTOCOL,
    DEFAULT_COMMUNITY,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_PRIV_PROTOCOL,
    DEFAULT_VERSION,
    MAP_AUTH_PROTOCOLS,
    MAP_PRIV_PROTOCOLS,
    SNMP_VERSIONS,
    ATTR_CURRENT,
    LOGGER
)

class SNMPException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class OIDs(Enum):
    MAC = "1.3.6.1.4.1.17420.1.2.3.0"
    FIRMWARE_VERSION = "1.3.6.1.4.1.17420.1.2.4.0"
    DEVICE_OWNER = "1.3.6.1.2.1.1.4.0"
    DEVICE_NAME = "1.3.6.1.2.1.1.5.0"
    DEVICE_LOCATION = "1.3.6.1.2.1.1.6.0"
    CURRENT = "1.3.6.1.4.1.17420.1.2.9.1.11.0"
    TEMPERATURE = "1.3.6.1.4.1.17420.1.2.7.0"
    HUMIDITY = "1.3.6.1.4.1.17420.1.2.8.0"
    SWITCH_COUNT = "1.3.6.1.2.1.1.7.0"
    def SWITCH_NAME_BY_ID(
        self, x): return "1.3.6.1.4.1.17420.1.2.9.1.14.%d.0" % x
    ACTIVE_SWITCHES = "1.3.6.1.4.1.17420.1.2.9.1.13.0"
    MODEL_NUMBER = "1.3.6.1.4.1.17420.1.2.9.1.19.0"
    MODEL_NAME = "1.3.6.1.4.1.17420.1.2.9.1.18.0"
    MODEL_NAME_SHORT = "1.3.6.1.4.1.17420.1.2.9.1.20.0"
    MFG_DATE = "1.3.6.1.4.1.17420.1.3.0.0"
    VOLTAGE = "1.3.6.1.4.1.17420.1.3.1.0"
    FREQUENCY = "1.3.6.1.4.1.17420.1.3.2.0"
    POWER_FACTOR = "1.3.6.1.4.1.17420.1.3.3.0"
    ACTIVE_POWER = "1.3.6.1.4.1.17420.1.3.4.0"
    APPEARENT_POWER = "1.3.6.1.4.1.17420.1.3.5.0"
    MAIN_ENERGY = "1.3.6.1.4.1.17420.1.3.6.0"
    ACCUMLATING_ENERGY = "1.3.6.1.4.1.17420.1.3.8.0"
    CARBON_EMMISION_RATE = "1.3.6.1.4.1.17420.1.3.10.0"


class DigipowerPDU:
    def __init__(self, host, port, community) -> None:
        self.host = host
        self.port = port
        self.community = community
        self.humidity = 0
        self.temperature = 0
        self.current = 0
        self.model = ""
        self.model_short = ""
        self.model_number = ""
        self.port_count = 0
        self.request_args = [
            SnmpEngine(),
            CommunityData(self.community, mpModel=SNMP_VERSIONS["1"]),
            UdpTransportTarget((self.host, self.port)),
            ContextData(),
        ]
        self.dispatcher = SnmpEngine()
        self.community_data = CommunityData(
            self.community, mpModel=SNMP_VERSIONS["1"])
        self.transport_target = UdpTransportTarget((self.host, self.port))
        self.context = ContextData()

    async def update(self):
        if self.has_humidity:
            self.humidity = int(await self._snmp_get(OIDs.HUMIDITY)) or 0
        if self.has_temp:
            self.temperature = int(await self._snmp_get(OIDs.TEMPERATURE)) or 0
        self.current = int(await self._snmp_get(OIDs.CURRENT)) or 0
        self.current /= 10
        self.active_ports = str(await self._snmp_get(OIDs.ACTIVE_SWITCHES)).split(",")
        return self

    async def init(self):
        self.has_humidity = True
        self.has_temp = True
        await self.update()
        self.mac = await self._snmp_get(OIDs.MAC) or ""
        self.devicename = str(await self._snmp_get(OIDs.DEVICE_NAME)) or ""
        self.model = str(await self._snmp_get(OIDs.MODEL_NAME)) or ""
        self.model_number = str(await self._snmp_get(OIDs.MODEL_NUMBER)) or ""
        self.model_short = str(await self._snmp_get(OIDs.MODEL_NAME_SHORT)) or ""
        self.has_humidity = self.humidity != 0
        self.has_temp = self.temperature != 0
        self.port_count = int(await self._snmp_get(OIDs.SWITCH_COUNT)) + 1

    async def _snmp_get(self, oid: OIDs):
        errindication, errstatus, errindex, restable = await getCmd(
            self.dispatcher,
            self.community_data,
            self.transport_target,
            self.context,
            ObjectType(ObjectIdentity(oid.value))
        )
        if errindication:
            raise SNMPException("SNMP error: {}".format(errindication))
        elif errstatus:
            raise SNMPException("SNMP error: {} at {}", errstatus.prettyPrint(),
                errindex and restable[-1][int(errindex) - 1] or "?")
        else:
            return restable[0][-1]

    async def set_port_state(self, port: int, state: bool):
        self.active_ports[port] = str(int(state))
        errindication, errstatus, errindex, restable = await setCmd(
            self.dispatcher,
            self.community_data,
            self.transport_target,
            self.context,
            ObjectType(
                ObjectIdentity("1.3.6.1.4.1.17420.1.2.9.1.13.0"),
                OctetString(",".join(self.active_ports)),
            ),
        )
        if errindication:
            raise SNMPException("SNMP error: {}".format(errindication))
        elif errstatus:
            raise SNMPException("SNMP error: {} at {}", errstatus.prettyPrint(),
                errindex and restable[-1][int(errindex) - 1] or "?")

    def get_port_state(self, port: int):
        return self.active_ports[port]
