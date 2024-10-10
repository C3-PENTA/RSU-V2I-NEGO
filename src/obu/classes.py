import struct
from dataclasses import asdict, dataclass, field
from struct import pack, unpack
from time import time

from dataclasses_json import dataclass_json

from config.obu_contant import *
from config.parameter import VehicleSpec


@dataclass_json  # 타입 정의된 데이터만 dict, json으로 변환됨
@dataclass
class _MessageHeader:  # for send
    magic: int = 0xf1f1  # 2bytes
    msg_type: int = 0  # 1byte
    crc16: int = 0  # 2bytes
    packet_len: int = 0  # 2bytes
    
    def __post_init__(self):
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER
        self.header_fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER
        self.data_fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER
        self.data_list = self.__match_args__
        self.header_list = _MessageHeader.__match_args__
        self.timestamp: float = time()
        self.scaling_list = {'lat':1/10**8,
                     'lon':1/10**8,
                     'hgt':0.1,
                     'transmission_and_speed':0.02,
                     'heading':0.0125,
                     'width':1,
                     'length':1,
        }
    
    @classmethod
    def unpack_header(cls, packet: bytes, _fmt: str = None) -> bool:
        if _fmt is None:
            _fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER
        magic, msg_type, crc16, packet_len = unpack(_fmt, packet[:7])
        return msg_type

    
    def pack_header(self, header_fmt: str = None) -> bytes:
        data_list = []
        if header_fmt is None:
            header_fmt = self.header_fmt
        for key in self.header_list:
            value = self.__getattribute__(key)
            data_list.append(value)
        return pack(header_fmt,*data_list)
    
    
    def pack_data(self, _fmt = None):
        if _fmt is None:
            _fmt = self.fmt
        _data_list = []
        for key in self.data_list:
            value = self.__getattribute__(key)
            if key in self.scaling_list:
                value = int(value / self.scaling_list[key])
            _data_list.append(value)

        # checksum
        # if len(_data_list) != (len(self.data_list) - len(self.header_list)):
        #     print(f"{_data_list = }")
        #     raise ValueError
        # try:
        #     packed_data = pack(_fmt, *_data_list)
        # except struct.error:
        #     packed_data = b''
        # packed_header = self.pack_header()

        packed_data = pack(_fmt, *_data_list)
            
        return packed_data
        
    def unpack_data(self, data, _fmt:str = None):
        if _fmt is None:
            _fmt = self.fmt
        # print(f"{_fmt = } {data = }")
        unpacked_data = unpack(_fmt, data)

        # if len(self.data_list) != len(unpacked_data):
        #     raise ValueError
        
        _scaling_list = self.scaling_list
        for name, value in zip(self.data_list, unpacked_data):
            if name in _scaling_list:
                value = value * _scaling_list[name]
            self.__setattr__(name,value)

        return True
    
@dataclass_json  # 타입 정의된 데이터만 dict, json으로 변환됨
@dataclass
class Message:  # for receive
    raw_packet: bytes
    data_field = None
    
    def __post_init__(self):
        if self.unpack_header(self.raw_packet):
            pass
        
    def unpack_header(self, packet: bytes, _fmt: str = DataFormat.BYTE_ORDER+DataFormat.HEADER) -> bool:
        self.magic, self.msg_type, self.crc16, self.packet_len = unpack(_fmt, packet[:7])
        self.data_field = 0
        return True

@dataclass
class BsmData(_MessageHeader):
    msg_type: int = BSM.msg_type
    packet_len: int = BSM.packet_len
    msg_count: int = 0  # 1byte uint / 0...127
    tmp_id: int = 0  # 4bytes uint 
    dsecond: int = 0  # 2bytes uint / unit: miliseconds
    lat: int = 0  # 4bytes int / unit: microdegrees/10
    lon: int = 0  # 4bytes int / unit: microdegrees/10
    hgt: int = 0  # 2bytes uint / WGS84 / -4096 ~ 61439 / unit: 10cm  !question
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
    width: int = VehicleSpec.WIDTH  # 2bytes uint / unit: cm
    length: int = VehicleSpec.LENGTH  # 2bytes uint / unit: cm
    l2id: int = 0  # 4bytes uint

    
    def __init__(self, data: bytes = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.BSM
        self.data_fmt =  DataFormat.BYTE_ORDER+DataFormat.BSM
        self.data_list = self.__match_args__

        if data is not None:
            self.unpack_data(data, self.fmt)


    def pack_data(self, data_fmt = None):
        if data_fmt is None:
            data_fmt = self.data_fmt
        _data_list = []

        for key in self.data_list:
            if key in self.header_list:
                continue
            value = self.__getattribute__(key)
            if key in self.scaling_list:
                value = int(value / self.scaling_list[key])
            # _data_list.append(0)
            _data_list.append(value)
        self.msg_count += 1
        if self.msg_count > 128:
            self.msg_count = 0

        # checksum
        if len(_data_list) != (len(self.data_list) - len(self.header_list)):
            print(f"Raise BSM data len Error")
            raise ValueError

        packed_data = pack(data_fmt, *_data_list)
        packed_header = self.pack_header()
        return packed_header+packed_data


@dataclass
class MyBsmData(BsmData):  # 자율차 -> 태블릿 송신 전용
    msg_type: int = MY_BSM.msg_type
    packet_len: int = MY_BSM.packet_len
    
    
    def __init__(self, data: bytes = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.MY_BSM
        self.data_fmt =  DataFormat.BYTE_ORDER+DataFormat.MY_BSM
        self.data_list = self.__match_args__

        if data is not None:
            self.unpack_data(data, self.fmt)
            
@dataclass
class BsmLightData(BsmData):
    msg_type: int = BSM_LIGHT.msg_type
    packet_len: int = BSM_LIGHT.packet_len
    light: int = 0  # 2bytes uint
    
    
    def __init__(self, data: bytes = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.BSM_LIGHT
        self.data_fmt =  DataFormat.BYTE_ORDER+DataFormat.BSM_LIGHT
        self.data_list = BsmData.__match_args__
        if data is not None:
            self.unpack_data(data, self.fmt)

@dataclass
class DmmData(_MessageHeader):
    '''
    DMM Maneuver Type 설명
    차로 주행: 차선 내 직진주행(1)
    차로 변경: 좌차로 변경(2), 우차로 변경(3)
    교차로 통과: 직진(4), 좌회전(5), 우회전(6)
    기타: 유턴(7), 추월(8)
    '''
    packet_len: int = DMM.packet_len
    msg_type: int = DMM.msg_type
    sender: int = 0  # 4bytes uint
    receiver: int = 0xffffffff  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint 
    remain_distance: int = 0  # 1byte uint
    
    def __init__(self, l2id: int = 0, maneuver: int = 0, dist: int = 0, data = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.DMM
        self.msg_type = DMM.msg_type
        self.packet_len = DMM.packet_len
        if data is not None:
            self.unpack_data(data)
        if l2id:
            self.sender = l2id
        if maneuver:
            self.maneuver_type = maneuver
        if dist:
            self.remain_distance = dist

    # def unpack_data(self, data, packet_len = None, _fmt = DataFormat.DMM):
    #     if len(data) != packet_len:
    #         raise ValueError
        

@dataclass
class DnmRequestData(_MessageHeader):
    packet_len: int = DNM_REQUEST.packet_len
    msg_type: int = DNM_REQUEST.msg_type
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    remain_distance: int = 0  # 1byte uint

    def __init__(self,data = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.DNM_REQUEST
        if data is not None:
            self.unpack_data(data)


@dataclass
class DnmResponseData(_MessageHeader):  # 자율차 -> OBU 송신 전용
    msg_type: int = DNM_REP.msg_type
    packet_len: int = DNM_REP.packet_len
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    agreement_flag: int = AgreementFlag.AGREEMENT  # 1byte uint / 0: disagreement 1: agreement

    def __init__(self, l2id: int = 0, receiver: int = 0, agreement_flag: int = AgreementFlag.AGREEMENT, **kward):
        super().__post_init__()
        self.sender = l2id
        self.receiver = receiver
        self.agreement_flag = agreement_flag
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.DNM_RESPONSE
        

@dataclass
class DnmDoneData(_MessageHeader):
    packet_len: int = DNM_DONE.packet_len
    msg_type: int = DNM_DONE.msg_type
    sender: int = 0  # 4bytes uint
    receiver: int = 0  # 4bytes uint
    nego_driving_done: int = 0  # 1byte uint

    def __init__(self, data = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.DNM_DONE
        if data is not None:
            self.unpack_data(data)

        

@dataclass
class EdmData(_MessageHeader):
    '''
    EDM Maneuver Type 설명
    차로 변경: (1)
    교차로 통과: 직진(2), 좌회전(3), 우회전(4)
    기타: 유턴(7), 추월(8)
    '''
    msg_type = EDM.msg_type
    packet_len = EDM.packet_len
    sender: int = 0  # 4bytes uint
    maneuver_type: int = 0  # 2bytes uint
    remain_distance: int = 0  # 1byte uint

    def __init__(self, data = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.EDM
        if data is not None:
            self.unpack_data(data, self.fmt)


@dataclass
class L2idRequestData(_MessageHeader):  # 자율차 -> OBU 송신 전용
    msg_type: int = L2ID.msg_type
    packet_len = L2ID.packet_len

    def __init__(self, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_REQUEST

    def pack_data(self, data_fmt=None):
        return self.pack_header()
        

@dataclass
class L2idResponseData(_MessageHeader):
    msg_type = L2ID_RESPONSE.msg_type
    l2id: int = 0  # 4bytes uint
    def __init__(self, data: bytes = None, **kward):
        super().__post_init__()
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_RESPONSE
        if data is not None:
            self.unpack_data(data)


@dataclass
class CimData(_MessageHeader):
    msg_type: int = CIM.msg_type
    packet_len: int = CIM.packet_len
    sender: int = 0
    vehicle_type: int = 10

    def __init__(self, l2id: int = 0, **kward):
        super().__post_init__()
        if l2id:
            self.sender = l2id
        self.fmt = DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.CIM
        self.data_list = CimData.__match_args__


@dataclass_json
@dataclass
class ObuToVehicleData:
    timestamp: float = time()
    msg_type: int = 0
    maneuver_command: int = 0
    obu_message: dict = field(default_factory=dict)
    
    
@dataclass_json
@dataclass
class VehicleData:
    timestamp: float = time() 
    lat: float = 0
    lon: float = 0
    hgt: float = 0
    heading: float = 0
    speed: float = 0  # km/h
    turn_signal: int = 0

    width: int = VehicleSpec.WIDTH
    length: int = VehicleSpec.LENGTH
    def __init__(self):
        self.status = None
        self.update_rate = 0

    def update_data(self, kward):
        self.__dict__.update(kward)
        
        
MSG_TYPE = {MessageType.BSM_NOIT:BsmData,
            MessageType.DMM_NOIT:DmmData,
            MessageType.DNM_REQUEST:DnmRequestData,
            MessageType.DNM_RESPONSE:DnmResponseData,
            MessageType.DNM_ACK:DnmDoneData,
            MessageType.EDM_NOIT:EdmData,
            MessageType.MY_BSM_NOIT:BsmData,
            MessageType.CIM_NOIT:CimData,
            MessageType.BSM_LIGHT_NOIT:BsmLightData,
            MessageType.L2ID_REQUEST:L2idRequestData,
            MessageType.L2ID_RESPONSE:L2idResponseData,
    }
    
if __name__ == "__main__":
    # test_bytes = b'\x00\x02\x02\x00\x02\x00\x02\x00\x01\x01\x00\x01\x00\x01'
    bsm_test_data = bytes.fromhex('F1F1010000002B00000000010000165E581A4B776578000000000000000000000000000000000000000000C801F400000000')
    bsm_test_data1 = bytes.fromhex('F1F1010000000300000000000000FFFFFF')
    # print(f"{_test_data =}")
    # test_data = _test_data.to_bytes()
    # a = Message(test_bytes)
    b = BsmData(bsm_test_data)
    print(b)
    b.pack_data()
    # b.pack_data()
    # b.pack_data()
    print(b.to_dict())
    

'''
1. data 관리를 어찌 할 것인가,,,
    - 데이터를 msg header의 인자로 넣고, 관리 or 한 꺼번에 관리
    - 받는 데이터는 매번 생성?

2. 차량<->미들웨어의 데이터 관리를 어찌,,,
    - 데이터와 주기가 매번 다름
'''