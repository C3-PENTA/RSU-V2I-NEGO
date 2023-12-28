from collections import deque

from ..bridge.comm import ObuSocket
from config.parameter import RemoteAddress, CommunicatorConfig
from .classes import *

class Middleware:
    def __init__(self) -> None:
        self.obu_module = ObuSocket('OBU', RemoteAddress.OBU_BIND, self)
        self.vehicle_module = ObuSocket('OBU', RemoteAddress.VEHICLE_BIND, self)

        self.queue_data = deque([])
        
        self.__init_data()

    def __init_data(self):
        self.l2id = 0

        self.bsm = BsmData()

        self.vehicle_data = VehicleData()
    
    def _create_post_l2id(self, l2id: int):

        self.cim = CimData(l2id)
        self.dnm_rep = DnmResponseData(l2id)
        self.dmm = DmmData(l2id)
        
    def interchange_data(self):
        self.vehicle_module

    def update_data(self):
        vehicle_data = self.vehicle_data
        vehicle_module = self.vehicle_module
        if not vehicle_module.is_connected:
            return False
        
        vehicle_data.update_data(vehicle_module.get_data())
        self.bsm.__dict__.update(vehicle_data.to_dict())

        return True