import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfMass, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FroelingDataCoordinator
from .froelingDevice import FroelingDevice, DeviceType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from hass.data as specified in your __init__.py
    coordinator: FroelingDataCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ].coordinator

    devices = []

    for froelingDevice in coordinator.data.devices:
        if froelingDevice.isParent:
            devices.append(
                FroelingSensor(hass, coordinator, froelingDevice, config_entry)

            )

    sensors = []
    for froelingDevice in coordinator.data.devices:
        if not froelingDevice.isParent:
            sensors.append(
                FroelingSensor(hass, coordinator, froelingDevice, config_entry)

            )

    # Create the sensors.
    await add_sensors(sensors, async_add_entities)
    await add_devices(devices, async_add_entities)


async def add_devices(devices, async_add_entities):
    async_add_entities(devices)


async def add_sensors(sensors, async_add_entities):
    async_add_entities(sensors)


class FroelingSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(self, hass: HomeAssistant, coordinator: FroelingDataCoordinator, froelingDevice: FroelingDevice,
                 config_entry: ConfigEntry) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.froelingDevice = froelingDevice
        self.key = froelingDevice.key
        self.config_entry = config_entry

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.froelingDevice = self.coordinator.get_device_by_key(
            self.froelingDevice.key
        )
        _LOGGER.debug("Device: %s", self.froelingDevice.key)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str | None:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        if self.froelingDevice.device.type == DeviceType.TEMP_SENSOR:
            return SensorDeviceClass.TEMPERATURE
        if self.froelingDevice.device.type == DeviceType.PELLET_SENSOR:
            return SensorDeviceClass.WEIGHT
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        # Identifiers are what group entities into the same device.
        # If your device is created elsewhere, you can just specify the indentifiers parameter.
        # If your device connects via another device, add via_device parameter with the indentifiers of that device.
        if self.froelingDevice.isParent:
            return DeviceInfo(
                name=f"{self.froelingDevice.device.displayName}",
                manufacturer="Froeling",
                identifiers={
                    (
                        DOMAIN,
                        self.froelingDevice.device.device_unique_id,
                    )
                },
                suggested_area='Keller'
            )
        else:
            return DeviceInfo(
                name=f"{self.froelingDevice.device.displayName}",
                manufacturer="Froeling",
                identifiers={
                    (
                        DOMAIN,
                        self.froelingDevice.device.parentIdentifier
                    )
                },
            )

    @property
    def icon(self) -> str | None:
        return self.froelingDevice.device.icon

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.froelingDevice.device.displayName

    @property
    def native_value(self) -> int | float | str:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        if self.froelingDevice.device.type == DeviceType.PELLET_SENSOR:
            return float(self.froelingDevice.device.state) * 1000
        return self.froelingDevice.device.state

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        if self.froelingDevice.device.type == DeviceType.TEMP_SENSOR:
            return UnitOfTemperature.CELSIUS
        if self.froelingDevice.device.type == DeviceType.PELLET_SENSOR:
            return UnitOfMass.KILOGRAMS
        if self.froelingDevice.device.type == DeviceType.PERCENTAGE:
            return PERCENTAGE
        return None

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.froelingDevice.device.device_unique_id}"

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        if self.froelingDevice.device.type == DeviceType.TEMP_SENSOR:
            return SensorStateClass.MEASUREMENT
        return SensorStateClass.TOTAL

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        attrs = {}
        attrs["extra_info"] = "Extra Info"
        return attrs
