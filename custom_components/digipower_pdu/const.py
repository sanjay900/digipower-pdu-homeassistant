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

SCAN_INTERVAL = timedelta(seconds=1)
SERVICE_PDU: Final = "digipower_pdu"

LOGGER = logging.getLogger(__name__)

