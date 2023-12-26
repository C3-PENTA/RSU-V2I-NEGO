from struct import pack, unpack
from dataclasses import dataclass, asdict
from dataclasses_json import dataclass_json

from abc import ABCMeta, abstractmethod

from config.contant import *


    

@dataclass_json
@dataclass
class _MessageHeader:  # for send
    magic: int = 0xf1f1  # 2bytes
    msg_type: int = 0  # 1byte
    crc16: int = 0  # 2bytes
    packet_len: int = 0  # 2bytes

    def unpack_header(self, packet: bytes, _fmt: str = DataFormat.HEADER) -> bool:
        self.magic, self.msg_type, self.crc16, self.packet_len = unpack(_fmt, packet[:7])
        return True

    @abstractmethod
    def pack_header(self, _fmt: str = DataFormat.HEADER):
        pass
        
    @abstractmethod
    def unpack_data(self, data, packet_len = None, _fmt = None):
        # Overwrite for each module
        if len(data) != packet_len:
            raise ValueError

    
@dataclass_json
@dataclass
class Message:  # for receive
    raw_packet: bytes
    data_field = None
    
    def __post_init__(self):
        if self.unpack_header(self.raw_packet):
            self.msg_type
        
    def unpack_header(self, packet: bytes, _fmt: str = DataFormat.HEADER) -> bool:
        self.magic, self.msg_type, self.crc16, self.packet_len = unpack(_fmt, packet[:7])
        self.data_field = 0
        return True

@dataclass
class BsmData(_MessageHeader):
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

    def __post__init__(self):
        pass
    
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
    
    def unpack_data(self, data, packet_len = None, _fmt:str = DataFormat.BSM):
        # if len(data) != packet_len:
        #     raise ValueError
        msg_count, tmp_id, dsecond, lat, lon, elevation, semi_major, semi_minor, orientation, transmission_and_speed, heading, \
        steering_wheel_angle, accel_long, accel_lat, accel_vert, yaw_rate, brake_system_status, width, length, l2id = [0]*20



@dataclass
class BsmLightData(_MessageHeader):
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
    
    def unpack_data(self, data, packet_len = None, _fmt:str = DataFormat.BSM_LIGHT):
        if len(data) != packet_len:
            raise ValueError


@dataclass
class DmmData(_MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.DMM):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmRequestData(_MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.DNM_REQUEST):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmResponseData(_MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    agreement_flag: int = 0  # 1byte uint / 0: disagreement 1: agreement

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.DNM_RESPONSE):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class DnmDoneData(_MessageHeader):
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    nego_driving_done: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.DNM_DONE):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class EdmData(_MessageHeader):
    sender: int = 0  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint
    remain_distance: int = 0  # 1byte uint

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.EDM):
        if len(data) != packet_len:
            raise ValueError


@dataclass
class L2idRequestData(_MessageHeader):
    msg_type = MessageType.L2ID_REQUEST

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.L2ID_REQUEST):
        if len(data) != packet_len:
            raise ValueError
        

@dataclass
class L2idResponseData(_MessageHeader):
    l2id: int = 0  # 4bytes uint

    def unpack_data(self, data, packet_len = None, _fmt = DataFormat.L2ID_RESPONSE):
        if len(data) != packet_len:
            raise ValueError


if __name__ == "__main__":
    a = Message(1)