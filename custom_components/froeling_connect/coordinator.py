import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import APIAuthError, API
from .const import *
from .froelingDevice import FroelingDevice

_LOGGER = logging.getLogger(__name__)


@dataclass
class FroelingAPIData:
    """Class to hold api data."""

    controller_name: str
    devices: list[FroelingDevice]


class FroelingDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Froeling data."""

    data: FroelingAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.config_entry = config_entry
        self.user = config_entry.data[CONF_USERNAME]
        self.pwd = config_entry.data[CONF_PASSWORD]
        self.facilityId = config_entry.data[CONF_FACILITY_ID]

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        self.hass = hass
        self.headers = {
            'Content-Type': 'application/json',
        }

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.entry_id})",
            # Method to call on every update interval.
            update_method=self._async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here
        self.api = API(user=self.user, pwd=self.pwd, facilityId=self.facilityId)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            await self.hass.async_add_executor_job(self.api.connect)
            devices = await self.hass.async_add_executor_job(self.api.get_Devices)

        except APIAuthError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        return FroelingAPIData(self.api.controller_name, devices)

    def get_device_by_key(
            self, deviceKey: str
    ) -> FroelingDevice | None:
        """Return device by device id."""
        # Called by the binary sensors and sensors to get their updated data from self.data
        try:
            return [
                device
                for device in self.data.devices
                if device.key == deviceKey
            ][0]
        except IndexError:
            return None
