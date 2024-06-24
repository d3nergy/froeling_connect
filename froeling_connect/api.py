"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""
import json
import logging

import httpx

from .froelingDevice import FroelingDevice, DeviceType, OutTemp, Boiler, Buffer, FeedSystem, DeviceSensor

_LOGGER = logging.getLogger(__name__)


class API:
    """Class for example API."""

    def __init__(self, user: str, pwd: str, facilityId: str) -> None:
        """Initialise."""
        self.payload = {
            'osType': 'web',
            'password': pwd,
            'username': user
        }
        self.facilityId = facilityId
        self.connected: bool = False,
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.userData = {}

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.facilityId.replace(".", "_")

    def connect(self):
        """Connect to api."""
        try:
            with httpx.Client(http2=True) as client:

                login = client.post('https://connect-api.froeling.com/connect/v1.0/resources/login',
                                    headers=self.headers, data=json.dumps(self.payload))

                self.headers['Authorization'] = login.headers['Authorization']
                self.connected = True
                self.userData = login.json()['userData']

        except Exception as e:
            raise APIAuthError("Error connecting to api.", e) from e

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    def get_Devices(self) -> list[FroelingDevice]:

        userId = self.userData['userId']

        """Get devices on api."""
        with httpx.Client(http2=True) as client:
            try:
                facilityData = client.get(
                    'https://connect-api.froeling.com/fcs/v1.0/resources/user/' + str(
                        userId) + '/facility/' + str(
                        self.facilityId) + '/overview',
                    headers=self.headers)

                data_json = facilityData.json()
                outTempData = data_json['outTemp']

                outTempDevice = FroelingDevice(key=f"{self.controller_name}_outTemp", isParent=True,
                                               device=OutTemp(device_id='outTemp1', icon="mdi:sun-thermometer",
                                                              device_unique_id=f"{self.controller_name}_outTemp"
                                                              , key='outTemp', state=outTempData['value'],
                                                              unit=outTempData['unit'],
                                                              displayName=outTempData['displayName'],
                                                              type=DeviceType.TEMP_SENSOR))

                componentData = data_json['components']
                componentDevices = []

                for component in componentData:
                    if component['type'] == 'BOILER':
                        componentDevices.append(
                            FroelingDevice(
                                key=f"{self.controller_name}_{component['componentId']}_kessel_{component['componentNumber']}",
                                isParent=True,
                                device=Boiler(device_id=component['componentId'],
                                              device_unique_id=f"{self.controller_name}_{component['componentId']}"
                                              , key=component['componentId'], icon="mdi:hvac",
                                              state=component['state']['displayValue'],
                                              displayName=component['displayName'],
                                              type=DeviceType.COMPONENT))
                        )
                        childrenEntitiesKessel = self.add_entities_to_device(component,
                                                                             f"{self.controller_name}_{component['componentId']}",
                                                                             ['boilerTemp',
                                                                              'mode2',
                                                                              'ignitionWhenBufferTempBelow'])

                    if component['type'] == 'CIRCUIT':
                        componentDevices.append(
                            FroelingDevice(
                                key=f"{self.controller_name}_{component['componentId']}_circuit_{component['componentNumber']}",
                                isParent=True,

                                device=Boiler(device_id=component['componentId'],
                                              device_unique_id=f"{self.controller_name}_{component['componentId']}"
                                              , key=component['componentId'], icon="mdi:heating-coil",
                                              state=component['mode']['displayValue'],
                                              displayName=component['displayName'],
                                              type=DeviceType.COMPONENT))
                        )
                        childrenEntitiesCircuit = self.add_entities_to_device(component,
                                                                              f"{self.controller_name}_{component['componentId']}",
                                                                              ['desiredRoomTemp',
                                                                               'mode',
                                                                               'actualFlowTemp'])
                    if component['type'] == 'DHW':
                        componentDevices.append(
                            FroelingDevice(
                                key=f"{self.controller_name}_{component['componentId']}_boiler_{component['componentNumber']}",
                                isParent=True,

                                device=Boiler(device_id=component['componentId'],
                                              device_unique_id=f"{self.controller_name}_{component['componentId']}"
                                              , key=component['componentId'],
                                              state=component['active'], icon="mdi:water-boiler",
                                              displayName=component['displayName'],
                                              type=DeviceType.COMPONENT))
                        )
                        childrenEntitiesBoiler = self.add_entities_to_device(component,
                                                                             f"{self.controller_name}_{component['componentId']}",
                                                                             ['dhwTempTop',
                                                                              'mode',
                                                                              'setDhwTemp'])
                    if component['type'] == 'BUFFER_TANK':
                        componentDevices.append(
                            FroelingDevice(
                                key=f"{self.controller_name}_{component['componentId']}_buffer_{component['componentNumber']}",
                                isParent=True,

                                device=Buffer(device_id=component['componentId'],
                                              device_unique_id=f"{self.controller_name}_{component['componentId']}"
                                              , key=component['componentId'],
                                              state=component['active'], icon="mdi:propane-tank",
                                              displayName=component['displayName'],
                                              type=DeviceType.COMPONENT))

                        )
                        childrenEntitiesBuffer = self.add_entities_to_device(component,
                                                                             f"{self.controller_name}_{component['componentId']}",
                                                                             ['bufferPumpControl',
                                                                              'bufferTankCharge',
                                                                              'bufferTempBottom',
                                                                              'bufferTempTop',
                                                                              ])
                    if component['type'] == 'FEED_SYSTEM':
                        componentDevices.append(
                            FroelingDevice(
                                key=f"{self.controller_name}_{component['componentId']}_feedSystem_{component['componentNumber']}",
                                isParent=True,

                                device=FeedSystem(device_id=component['componentId'],
                                                  device_unique_id=f"{self.controller_name}_{component['componentId']}"
                                                  , key=component['componentId'],
                                                  state=component['remainingPelletsAmount']['value'],
                                                  displayName=component['displayName'], icon="mdi:cog-box",
                                                  type=DeviceType.PELLET_SENSOR,
                                                  unit=component['remainingPelletsAmount']['unit'])
                            )
                        )
                        childrenEntitiesFeedSystem = self.add_entities_to_device(component,
                                                                                 f"{self.controller_name}_{component['componentId']}",
                                                                                 ['pelletsUsageCounter',
                                                                                  'remainingPelletsAmount',
                                                                                  'totalPelletConsumption',
                                                                                  ])

            except Exception as e:
                raise ValueError('Error fetching Devices', e) from e

            componentDevices = componentDevices + childrenEntitiesKessel + childrenEntitiesCircuit + childrenEntitiesBoiler + childrenEntitiesBuffer + childrenEntitiesFeedSystem
        return [outTempDevice] + componentDevices

    def add_entities_to_device(self, parent, parentId, entities: list[str]):
        entities_to_be_returned = []
        for entity in entities:
            try:

                if 'displayValue' in parent[f"{entity}"]:
                    entityState = parent[f"{entity}"]['displayValue']
                else:
                    entityState = parent[f"{entity}"]['value']

                entityUnit = None
                if 'unit' in parent[f"{entity}"]:
                    entityUnit = parent[f"{entity}"]['unit']

                entities_to_be_returned.append(FroelingDevice(
                    key=f"{self.controller_name}_{parent['componentId']}_kessel_{parent['componentNumber']}_{entity}",
                    isParent=False,
                    device=DeviceSensor(device_id=f"{parent['componentId']}_{entity}",
                                        device_unique_id=f"{self.controller_name}_{entity}"
                                        , key=f"{parent['componentId']}_{entity}", icon="mdi:hvac",
                                        state=entityState,
                                        displayName=parent[f"{entity}"]['displayName'],
                                        parentIdentifier=parentId,
                                        type=self.device_type_by_unit(entityUnit), unit=entityUnit)
                ))
            except Exception as e:
                raise ValueError('Error adding entity', e) from e

        return entities_to_be_returned

    def device_type_by_unit(self, unit):
        match unit:
            case None:
                return DeviceType.OTHER
            case '°C':
                return DeviceType.TEMP_SENSOR
            case _:
                return DeviceType.OTHER


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
