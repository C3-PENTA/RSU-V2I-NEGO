

from ..bridge.comm import ObuSocket
from config.parameter import RemoteAddress, CommunicatorConfig


class Middleware:
    def __init__(self) -> None:
        self.obu_module = ObuSocket('OBU', RemoteAddress.OBU_BIND)
        self.vehicle_module = ObuSocket('OBU', RemoteAddress.VEHICLE_BIND)

        