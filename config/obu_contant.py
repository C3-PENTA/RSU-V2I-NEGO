from enum import IntEnum, StrEnum


class MessageType(IntEnum):
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
    
    
class ExteriorLightType(IntEnum):
    LOWBEAM_HEADLIGHT_ON = 0
    HIGHBEAM_HEADLIGHT_ON = 1
    LEFT_TURN_SIGNAL_ON = 2
    RIGHT_TURN_SIGNAL_ON = 3
    HAZARD_SIGNAL_ON = 4
    AUTOMATIC_LIGHT_CONTROL_ON = 5
    DAYTIME_RUNNING_LIGHT_ON = 6
    FOG_LIGHT_ON = 7
    PARKING_LIGHT_ON = 8


class EdmManeuverType(IntEnum):
    UNKNOWN = 0
    LANE_CHANGE = 1
    STRAIGHT_AT_CROSSROAD = 2
    LEFT_AT_CROSSROAD = 3
    RIGHT_AT_CROSSROAD = 4
    U_TURN = 7
    OVERTAKE = 8


class DmmManeuverType(IntEnum):
    UNKNOWN = 0
    STRAIGHT = 1
    LEFT_LANE_CHANGE = 2
    RIGHT_LANE_CHANGE = 3
    STRAIGHT_AT_CROSSROAD = 4
    LEFT_AT_CROSSROAD = 5
    RIGHT_AT_CROSSROAD = 6
    U_TURN = 7
    OVERTAKE = 8

class DataFormat(StrEnum):
    BYTE_ORDER = '>'
    HEADER: str = 'HBHH'
    BSM: str = 'BIHiiHBBHHHBhhBhHHHI'
    BSM_LIGHT: str = 'BIHiiHBBHHHbHHBHHHHIH'
    CIM:str = 'IB'
    DMM: str = 'IIHB'
    DNM_REQUEST: str = 'IIB'
    DNM_RESPONSE: str = 'IIB'
    DNM_DONE: str = 'IIB'
    EDM: str = 'IHB'
    L2ID_RESPONSE: str = 'I'
    L2ID_REQUEST: str = ''
    
class ManeuverCommandType(IntEnum):
    NONE = 0
    WAIT = 1
    STOP = 2
    SLOW_DOWN = 3
    LANE_CHANGE = 4
    OVERTAKING = 5

class ManeuverLaneType(IntEnum): # 내 차량이 가야할 곳
    NONE = 0
    CURRENT_LANE = 1
    LEFT_LANE = 2
    RIGHT_LANE = 3
    
    
class BSM:
    msg_type: int = MessageType.BSM_NOIT
    packet_len: int = 50

class DMM:
    msg_type: int = MessageType.DMM_NOIT
    packet_len: int = 11
    
class CIM:
    msg_type: int = MessageType.CIM_NOIT
    packet_len: int = 18

class DNM_REP:
    msg_type: int = MessageType.DNM_RESPONSE
    packet_len: int = 16

class L2ID:
    msg_type: int = MessageType.L2ID_REQUEST
    packet_len: int = 7

class L2ID_RESPONSE:
    msg_type: int = MessageType.L2ID_RESPONSE
    packet_len: int = 11

class DNM_DONE:
    msg_type: int = MessageType.DNM_ACK
    packet_len: int = 9
    
class DNM_REQUEST:
    msg_type: int = MessageType.DNM_REQUEST
    packet_len: int = 9

class EDM:
    msg_type: int = MessageType.EDM_NOIT
    packet_len: int = 7
    
class BSM_LIGHT:
    msg_type: int = MessageType.BSM_LIGHT_NOIT
    packet_len: int = 52
    