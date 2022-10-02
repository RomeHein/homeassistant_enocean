"""Hold utility functions."""
from __future__ import annotations

import logging

from enocean.communicators import Communicator

# import DATA_ENOCEAN, ENOCEAN_DONGLE, EnOceanDongle
import homeassistant.components.enocean as ec
from homeassistant.core import HomeAssistant

LOGGER = logging.getLogger(__name__)


def get_communicator_reference(hass: HomeAssistant) -> object | Communicator:
    """Get a reference to the communicator (dongle/pihat)."""
    enocean_data = hass.data.get(ec.DATA_ENOCEAN, {})
    dongle: ec.EnOceanDongle = enocean_data[ec.ENOCEAN_DONGLE]
    if not dongle:
        LOGGER.error(
            "No EnOcean Dongle configured or available. No teach-in possible")
        return None
    communicator: Communicator = dongle.communicator
    return communicator


def int_to_list(int_value):
    """Convert integer to list of values."""
    result = []
    while int_value > 0:
        result.append(int_value % 256)
        int_value = int_value // 256
    result.reverse()
    return result


def hex_to_list(hex_list):
    """Convert hexadecimal list to a list of int values."""
    # [0xFF, 0xD9, 0x7F, 0x81] => [255, 217, 127, 129]
    result = []
    if hex_list is None:
        return result

    for hex_value in hex_list:
        result.append(int(hex_value))
    result.reverse()
    return result
