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
    magic: int = 0xf1f1  # 2bytes
    msg_type: int = 0  # 1byte
    crc16: int = 0  # 2bytes
    packet_len: int = 0  # 2bytes

    def unpack_header(self, packet: bytes, _fmt: str = '>HBHH'):
        self.magic, self.msg_type, self.crc16, self.packet_len = unpack(_fmt, packet[:7])
        
    def unpack_data(self, data, packet_len = None):
        # Overwrite for each module
        if len(data) != packet_len:
            raise ValueError

@dataclass
class BsmData(MessageHeader):
    msg_count: int = 0  # 1byte uint / 0...127
    tmp_id: int = 0  # 4bytes uint 
    dsecond: int = 0  # 2bytes uint / unit: miliseconds
    lat: int = 0  # 4bytes int / unit: microdegrees/10
    lon: int = 0  # 4bytes int / unit: microdegrees/10
    elevation: int = 0  # 2bytes uint / WGS84 / -4096 ~ 61439 / unit: 10cm  !question
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
    
    def __init__(self):
        self.data_list = BsmData.__match_args__
    
    def set_unpacking(self, name, value):
        calc_list = {'lat':1/10**7,
                     'lon':1/10**7,
                     'elevation':0.1,
                     'transmission_and_speed':0.02*3.6,
                     'heading':0.0125,
                     'width':0.1,
                     'length':0.1,
                     }
        
        if name in calc_list:
            if name == 'transmission_and_speed':
                value = round((value &0b11111111111) * calc_list[name],4)
            else:
                value = value * calc_list[name]
        
        return object.__setattr__(self, name, value)
    
    def unpack_data(self, data, packet_len = None, _fmt:str = '>BIHiiHBBHHHBhhBhHHHI'):
        # if len(data) != packet_len:
        #     raise ValueError
        msg_count, tmp_id, dsecond, lat, lon, elevation, semi_major, semi_minor, orientation, transmission_and_speed, heading, \
        steering_wheel_angle, accel_long, accel_lat, accel_vert, yaw_rate, brake_system_status, width, length, l2id = [0]*20



@dataclass
class BsmLightData(MessageHeader):
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
    
    def __setattr__(self, name, value):
        calc_list = {'lat':1/10**7,
                     'lon':1/10**7,
                     'elevation':0.1,
                     'transmission_and_speed':0.02*3.6,
                     'heading':0.0125,
                     'width':0.1,
                     'length':0.1,
                     }
        if name in calc_list:
            if name == 'transmission_and_speed':
                value = round((value &0b11111111111) * calc_list[name],4)
            else:
                value = value * calc_list[name]
        
        return object.__setattr__(self, name, value)
    
    def unpack_data(self, data, packet_len = None, _fmt:str = '>BIHiiHBBHHHBhhBhHHHIH'):
        if len(data) != packet_len:
            raise ValueError


@dataclass
class DmmData(MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmRequestData(MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmResponseData(MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    agreement_flag: int = 0  # 1byte uint / 0: disagreement 1: agreement

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmDoneData(MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    nego_driving_done: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class EdmData(MessageHeader):
    sender: int = 0  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError


@dataclass
class L2idRequestData(MessageHeader):
    msg_type = MessageType.L2ID_REQUEST

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class L2idResponseData(MessageHeader):
    l2id: int = 0  # 4bytes uint

    def unpack_data(self, data, packet_len = None):
        if len(data) != packet_len:
            raise ValueError
