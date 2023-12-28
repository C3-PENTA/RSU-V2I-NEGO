from collections import deque

from ..bridge.comm import ObuSocket
from config.parameter import RemoteAddress, CommunicatorConfig
from .classes import *

class Middleware:
    def __init__(self) -> None:
        self.obu_module = ObuSocket('OBU', RemoteAddress.OBU_BIND, self)
        self.vehicle_module = ObuSocket('OBU', RemoteAddress.VEHICLE_BIND, self)

        self.queue_data = deque([])
        
        self.__init_obu_data()

    def __init_obu_data(self):
        self.l2id = 0

        self.bsm = BsmData()
        self.cim = CimData()
    
    def _create_post_l2id(self, l2id: int):

        self.dnm_rep = DnmResponseData(l2id)
        self.dmm = DmmData(l2id)
        
    def interchange_data(self):
        pass