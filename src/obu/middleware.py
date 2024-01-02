from collections import deque
from time import sleep, time

from ..bridge.socket import ObuSocket, VehicleSocket
from config.parameter import ObuSocketParam, VehicleSocketParam, MiddleWareParam
from .classes import *

class Middleware:
    def __init__(self) -> None:
        self.config = MiddleWareParam
        self.obu_module = ObuSocket(ObuSocketParam, self)
        self.vehicle_module = VehicleSocket(VehicleSocketParam, self)

        self.obu_queue = deque([])
        
        self.__init_data()

    def __init_data(self):
        self.l2id = 0

        self.bsm = BsmData()

        self.vehicle_data = VehicleData()
    
    def _create_post_l2id(self, l2id: int):

        self.cim = CimData(l2id)
        self.dnm_rep = DnmResponseData(l2id)
        self.dmm = DmmData(l2id, self.vehicle_data.turn_signal)
        
    def unpack_msg_type(self, packet: bytes, _fmt: str = None) -> int:
        if _fmt is None:
            _fmt = self.header_fmt
        magic, msg_type, crc16, packet_len = unpack(_fmt, packet[:7])
        return msg_type

    def set_obu_data(self, data: bytes):
        msg_type = self.unpack_msg_type(data)
        if msg_type == 4:
            self.obu_module.send_obu_data(DnmResponseData(self.l2id))

        obu_data = MSG_TYPE[msg_type]().unpack_data(data)
        

    def set_vehicle_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError
        
        self.vehicle_data.update_data(data)

    def update_data(self):
        vehicle_data = self.vehicle_data
        vehicle_module = self.vehicle_module
        if not vehicle_module.is_connected:
            return False
        
        vehicle_data.update_data(vehicle_module.get_data())
        self.bsm.__dict__.update(vehicle_data.to_dict())

        return True
    
    def put_obu_queue(self, *argv):
        self.obu_module.send_queue.append(argv)

    def check_module_state(self)->bool:
        if not self.l2id:
            self.obu_module.put_queue_data(L2idRequestData())
            return False
        if not self.vehicle_module.is_connected:
            print(f"Disconnected...")
            return False
        return True


    def process(self):
        check_state = self.check_module_state
        _interval = self.config.update_interval
        
        
        while 1:
            if not check_state():
                sleep(3)
                continue

            _vehicle_data = self.vehicle_data
            if _vehicle_data.turn_signal:
                self.obu_module.put_queue_data(DmmData(self.l2id, _vehicle_data.turn_signal))

            