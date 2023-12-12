from struct import pack, unpack
from dataclasses import dataclass


class MessageType:
    BSM_NOIT = 1
    PIM_NOIT = 2
    DMM_NOIT = 3
    DNM_REQUEST = 4
    DNM_RESPONSE = 5
    DNM_ACK = 6
    EDM_NOIT = 7
    MY_BSM_NOIT = 8
    CIM_NOIT = 9
    BSM_LIGHT_NOIT = 51
    L2ID_REQUEST = 101
    L2ID_RESPONSE = 102
    LIGHT_NOIT = 103
    
    
class ExteriorLightType:
    LOWBEAM_HEADLIGHT_ON = 0
    HIGHBEAM_HEADLIGHT_ON = 1
    LEFT_TURN_SIGNAL_ON = 2
    RIGHT_TURN_SIGNAL_ON = 3
    HAZARD_SIGNAL_ON = 4
    AUTOMATIC_LIGHT_CONTROL_ON = 5
    DAYTIME_RUNNING_LIGHT_ON = 6
    FOG_LIGHT_ON = 7
    PARKING_LIGHT_ON = 8


class ManeuverType:
    UNKNOWN = 0
    STRAIGHT = 1
    LEFT_LANE_CHANGE = 2
    RIGHT_LANE_CHANGE = 3
    STRAIGHT_AT_CROSSROAD = 4
    LEFT_AT_CROSSROAD = 5
    RIGHT_AT_CROSSROAD = 6
    U_TURN = 7
    OVERTAKE = 8


@dataclass
class MessageHeader:
    magic: int = 0xf1f1
    msg_type: int = 0
    crc16: int = 0
    len:int = 0
    _fmt: str = '>HBHH'


@dataclass
class BsmData:
    msg_count: int = 0  # 4bytes uint / 0...127
    tmp_id: int = 0  # 4bytes uint 
    dsecond: int = 0  # 2bytes uint / unit: miliseconds
    lat: int = 0  # 4bytes int / unit: microdegrees/10
    lon: int = 0  # 4bytes int / unit: microdegrees/10
    elevation: int = 0  # 2bytes int / WGS84 / -4096 ~ 61439 / unit: 10cm
    semi_major: int = 0  # 1byte uint
    semi_minor: int = 0  # 1byte uint
    orientation: int = 0  # 2bytes uint
    transmission_and_speed: int = 0  # 2bytes uint / 0...11 bit * 0.02
    heading: int = 0  # 2bytes uint / unit of 0.0125 degrees / 0 ~ 359.9875
    steering_wheel_angle: int = 0  # 1byte uint
    accel_long: int = 0  # 2bytes int
    accel_lat: int = 0  # 2bytes int
    accel_vert: int = 0  # 1byte uint
    yaw_rate: int = 0  # 2bytes int
    brake_system_status: int = 0  # 2bytes uint
    width: int = 0  # 2bytes uint / unit: cm
    length: int = 0  # 2bytes uint / unit: cm
    l2id: int = 0  # 4bytes uint


@dataclass
class BsmLightData:
    msg_count: int = 0  # 4bytes uint / 0...127
    tmp_id: int = 0  # 4bytes uint 
    dsecond: int = 0  # 2bytes uint / unit: miliseconds
    lat: int = 0  # 4bytes int / unit: microdegrees/10
    lon: int = 0  # 4bytes int / unit: microdegrees/10
    elevation: int = 0  # 2bytes int / WGS84 / -4096 ~ 61439 / unit: 10cm
    semi_major: int = 0  # 1byte uint
    semi_minor: int = 0  # 1byte uint
    orientation: int = 0  # 2bytes uint
    transmission_and_speed: int = 0  # 2bytes uint / 0...11 bit * 0.02
    heading: int = 0  # 2bytes uint / unit of 0.0125 degrees / 0 ~ 359.9875
    steering_wheel_angle: int = 0  # 1byte uint
    accel_long: int = 0  # 2bytes int
    accel_lat: int = 0  # 2bytes int
    accel_vert: int = 0  # 1byte uint
    yaw_rate: int = 0  # 2bytes int
    brake_system_status: int = 0  # 2bytes uint
    width: int = 0  # 2bytes uint / unit: cm
    length: int = 0  # 2bytes uint / unit: cm
    l2id: int = 0  # 4bytes uint
    light: int = 0  # 2bytes uint


