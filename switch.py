"""Support for EnOcean switches."""
from __future__ import annotations

from enocean.utils import combine_hex
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_ID, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .device import EnOceanEntity

CONF_CHANNEL = "channel"
CONF_BEHAVIOR = "behavior"
CONF_AVAILABLE_BEHAVIOR = ["relay", "onoff", "push", "button"]
DEFAULT_NAME = "EnOcean Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ID): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_CHANNEL, default=0): cv.positive_int,
        vol.Optional(CONF_BEHAVIOR, default=CONF_AVAILABLE_BEHAVIOR[0]): vol.In(CONF_AVAILABLE_BEHAVIOR),
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the EnOcean switch platform."""
    channel = config.get(CONF_CHANNEL)
    dev_id = config.get(CONF_ID)
    dev_name = config.get(CONF_NAME)
    behavior = config.get(CONF_BEHAVIOR)
    add_entities([EnOceanSwitch(dev_id, dev_name, channel, behavior)])


class EnOceanSwitch(EnOceanEntity, SwitchEntity):
    """Representation of an EnOcean switch device."""

    def __init__(self, dev_id, dev_name, channel, behavior):
        """Initialize the EnOcean switch device."""
        super().__init__(dev_id, dev_name)
        self._on_state = False
        self.channel = channel
        self.behavior = behavior
        self._attr_unique_id = f"{combine_hex(dev_id)}-{behavior}-{channel}"

    @property
    def is_on(self):
        """Return whether the switch is on or off."""
        return self._on_state

    @property
    def name(self):
        """Return the device name."""
        return self.dev_name

    def turn_on(self, **kwargs):
        """Turn on the switch."""
        if self.behavior == 'relay':
            optional = [0x03]
            optional = [0x03]
            optional.extend(self.dev_id)
            optional.extend([0xFF, 0x00])
            self.send_command(
                data=[0xD2, 0x01, self.channel & 0xFF, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00],
                optional=optional,
                packet_type=0x01,
            )
        self._on_state = True

    def turn_off(self, **kwargs):
        """Turn off the switch."""
        if self.behavior == 'relay':
            optional = [0x03]
            optional.extend(self.dev_id)
            optional.extend([0xFF, 0x00])
            self.send_command(
                data=[0xD2, 0x01, self.channel & 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                optional=optional,
                packet_type=0x01,
            )
        self._on_state = False

    def value_changed(self, packet):
        """EEP: F6-02-02 - Nodon Soft Remote"""
        if packet.data[0] == 0xF6:
            press = packet.data[1]
            if self.behavior == 'onoff':
                if (press == 0x70 and (self.channel == 2 or self.channel == 0)) or (press == 0x30 and (self.channel == 1 or self.channel == 0)):
                    self._on_state = True
                elif press == 0x50 and (self.channel == 2 or self.channel == 0) or (press == 0x10 and (self.channel == 1 or self.channel == 0)):
                    self._on_state = False
            if self.behavior == 'push' and ((press == 0x70 and self.channel == 4) or (press == 0x50 and self.channel == 3) or (press == 0x30 and self.channel == 2) or (press == 0x10 and self.channel == 1)):
                self._on_state = not(self._on_state)
            if self.behavior == 'button' and ((press == 0x70 and self.channel == 4) or (press == 0x50 and self.channel == 3) or (press == 0x30 and self.channel == 2) or (press == 0x10 and self.channel == 1)):
                self._on_state = True
            elif self.behavior == 'button':
                self._on_state = False
            self.schedule_update_ha_state()
        """Update the internal state of the switch."""
        if packet.data[0] == 0xA5:
            # power meter telegram, turn on if > 10 watts
            packet.parse_eep(0x12, 0x01)
            if packet.parsed["DT"]["raw_value"] == 1:
                raw_val = packet.parsed["MR"]["raw_value"]
                divisor = packet.parsed["DIV"]["raw_value"]
                watts = raw_val / (10**divisor)
                if watts > 1:
                    self._on_state = True
                    self.schedule_update_ha_state()
        elif packet.data[0] == 0xD2:
            # actuator status telegram
            packet.parse_eep(0x01, 0x01)
            if packet.parsed["CMD"]["raw_value"] == 4:
                channel = packet.parsed["IO"]["raw_value"]
                output = packet.parsed["OV"]["raw_value"]
                if channel == self.channel:
                    self._on_state = output > 0
                    self.schedule_update_ha_state()
