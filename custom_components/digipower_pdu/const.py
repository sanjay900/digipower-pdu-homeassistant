"""SNMP constants."""
import logging
from datetime import timedelta
from typing import Final

CONF_COMMUNITY = "community"

DEFAULT_COMMUNITY = "public"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "161"

ATTR_CURRENT = "current"

DOMAIN = "digipower_pdu"

SCAN_INTERVAL = timedelta(seconds=10)
SERVICE_PDU: Final = "digipower_pdu"

SNMP_VERSIONS = {"1": 0, "2c": 1, "3": None}

LOGGER = logging.getLogger(__name__)

