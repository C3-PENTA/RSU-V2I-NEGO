from enum import Enum


class STATUS(Enum):
    UNKNOWN = -1
    DISCONNECTED = 0
    BAD = 1
    NORMAL = 2
    GOOD = 3
    GREAT = 4