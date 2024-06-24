from dataclasses import dataclass
from enum import StrEnum


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"
    PELLET_SENSOR = "pellet_sensor"
    OTHER = "other",
    COMPONENT = 'component'


@dataclass
class OutTemp:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    unit: str
    state: int | bool | str
    type: DeviceType
    icon: str | None


@dataclass
class DeviceSensor:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    state: int | bool | str
    type: DeviceType
    icon: str | None
    parentIdentifier: tuple
    unit: str | None


@dataclass
class Circuit:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    state: int | bool | str
    type: DeviceType
    icon: str | None


@dataclass
class Boiler:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    state: int | bool | str
    type: DeviceType
    icon: str | None


@dataclass
class Buffer:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    state: int | bool | str
    type: DeviceType
    icon: str | None


@dataclass
class FeedSystem:
    """API device."""
    key: int | str
    device_id: str | int
    device_unique_id: str | int
    displayName: str
    state: int | bool | str
    type: DeviceType
    unit: str
    icon: str | None


@dataclass
class FroelingDevice:

    def __init__(self, key, device, isParent):
        self.isParent = isParent
        self.name = key
        self.key = key
        self.device = device
