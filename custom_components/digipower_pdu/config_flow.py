"""Config flow to configure the digipower pdu integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from .pdu import DigipowerPDU, SNMPException

from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_COMMUNITY, DEFAULT_COMMUNITY, DEFAULT_HOST, DEFAULT_PORT


class DigipowerPDUFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for digipower pdu."""

    VERSION = 1

    entry: ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            name = user_input[CONF_HOST]
            try:
                host = user_input[CONF_HOST]
                port = user_input[CONF_PORT]
                community = user_input[CONF_COMMUNITY]
                device = DigipowerPDU(host, port, community)
                await device.init()
                await device.update()
                name = device.devicename
            except SNMPException as e:
                print(e)
                errors["base"] = " ".join(str(r) for r in e.args)
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_COMMUNITY: user_input[CONF_COMMUNITY],
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_COMMUNITY, default=DEFAULT_COMMUNITY): cv.string,
                    vol.Required(CONF_HOST): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                }
            ),
            errors=errors,
        )
