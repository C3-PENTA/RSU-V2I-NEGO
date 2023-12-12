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

