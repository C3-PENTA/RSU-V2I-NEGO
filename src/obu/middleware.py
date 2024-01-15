from collections import deque
from time import sleep, time

from ..bridge._socket import ObuSocket, VehicleSocket
from config.parameter import ObuSocketParam, VehicleSocketParam, MiddleWareParam
from .classes import *

class Middleware:
    def __init__(self) -> None:
        self.__init_data()
        self.config = MiddleWareParam

        self.comm_state = False
        self.obu_queue = deque([])
        
        
    def __init_data(self):
        self.l2id = 0
        self.bsm = BsmData()
        self.cim = CimData(self.l2id)
        self.vehicle_data = VehicleData()
    
    def _create_post_l2id(self, l2id: int):

        self.dnm_rep = DnmResponseData(l2id)
        self.dmm = DmmData(l2id, self.vehicle_data.turn_signal)
        self.cim.sender = self.l2id
        
    def unpack_msg_type(self, packet: bytes, _fmt: str = None) -> int:
        if _fmt is None:
            _fmt = self.bsm.header_fmt
        magic, msg_type, crc16, packet_len = unpack(_fmt, packet[:7])
        return msg_type

    def set_obu_data(self, data: bytes):
        msg_type = self.bsm.unpack_header(data)
        # msg_type = self.unpack_msg_type(data)
        obu_data = MSG_TYPE[msg_type](l2id = self.l2id)
        obu_data.unpack_data(data)
        if msg_type == 4:
            self.receiver = obu_data.sender
            self.obu_module.put_queue_data(DnmResponseData(self.l2id, self.receiver))
        elif msg_type == 102:
            self.l2id = obu_data.l2id
            self.bsm.l2id = self.l2id
            self.cim.sender = self.l2id

        self.vehicle_module.set_dict_data(obu_data.to_dict())
        
    def set_vehicle_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError
        
        self.vehicle_data.update_data(data)
        self.update_data()

    def update_data(self):
        vehicle_data = self.vehicle_data
        vehicle_module = self.vehicle_module
        if not vehicle_module.is_connected:
            return False
        
        # vehicle_data.update_data(vehicle_module.get_data())
        self.bsm.__dict__.update(vehicle_data.to_dict())

        return True
    
    def put_obu_queue(self, *argv):
        self.obu_module.send_queue.append(argv)

    def check_module_state(self)->bool:
        if not self.l2id:
            self.obu_module.put_queue_data(L2idRequestData())
            self.comm_state = False
            return False
        return True

    def process(self):
        self.vehicle_module = VehicleSocket(VehicleSocketParam, self)
        self.obu_module = ObuSocket(ObuSocketParam, self)
        check_state = self.check_module_state
        _update_interval = self.config.update_interval
        put_obu_queue = self.obu_module.put_queue_data


        sync_time = time()
        while 1:
            if not check_state():
                sleep(3)
                continue

            _vehicle_data = self.vehicle_data
            if _vehicle_data.turn_signal:
                put_obu_queue(DmmData(self.l2id, _vehicle_data.turn_signal))

            dt = time() - sync_time
            if _update_interval > dt:
                sleep(_update_interval - dt)
            sync_time = time()
            
def run_middleware():
    mw = Middleware()
    mw.process()
            
if __name__ == '__main__':
    mw = Middleware()
    mw.process()