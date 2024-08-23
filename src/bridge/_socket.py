import json
import socket
from collections import defaultdict, deque
import sys
from threading import Thread
from time import sleep, time

from config.loggers import (
    backup_recv_raw_log,
    backup_send_log,
    backup_send_raw_log,
    error_log,
    sys_log,
)

# from src.obu.middleware import Middleware
from config.obu_contant import ManeuverCommandType, MessageType
from config.parameter import CommunicatorConfig, ObuSocketParam, VehicleSocketParam

# from src.obu.middleware import Middleware
from src.obu.classes import (
    L2idRequestData,
    ObuToVehicleData,
    VehicleData,
    _MessageHeader,
)

# import Middleware


class SocketModule:
    def __init__(self, config: ObuSocketParam = None) -> None:
        self.config = config
        self.name = config.name
        self.host_bind = config.host_bind
        self.remote_bind = config.remote_bind
        
        self.sock = None
        self.status = None
        self.recv_data = {}
        self.is_connected: bool = False

        # self.run()
        # self.run_thread = Thread(target=self.process, name=self.name, daemon=True)
        # self.run_thread.start()
    
    def create_socket(self, bind = None, protocol = None):
        if protocol == 'udp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # sock.settimeout(self.config.update_interval*5)
        else:
            sock = socket.socket()
            sock.settimeout(self.config.update_interval*10)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bind is None:
            bind = self.host_bind
            print(f"{self.__class__.__name__} host bind: {self.host_bind}")
        sock.bind(bind)

        # self.sock = sock
        return sock 
    
    
    def connect_remote(self, sock = None, remote_bind = None):
        func_name = f'{self.__class__.__name__}::{sys._getframe().f_code.co_name}'
        if sock is None:
            if self.sock is not None:
                sock = self.sock
            else:
                print(f"Don't exist socket")
                return False
        if remote_bind is None:
            if self.remote_bind is not None:
                remote_bind = self.remote_bind
                print(f"{self.__class__.__name__} remote bind: {remote_bind}")
            
        try:
            sys_log.info(f"{func_name},Connecting {remote_bind}...")
            sock.connect(remote_bind)
        except socket.timeout:
            print(f'connect time out')
            return False
        except Exception as err:
            sock.close()
            # sys_log.error(f"{func_name},Raise connection error: {err}")
            error_log.error(f"{func_name},Raise connection error: {err}")
            self.is_connected = False
            return False

        sys_log.info(f"{func_name},Connected {self.__class__.__name__} socket.")
        return True

    def dump_json(self, data=None):
        if data is None or not data:
            result_data = {}
        else:
            result_data = data
        dump_data = json.dumps(result_data)
        # self.json_data.clear()
        # print(f"{dump_data = }")
        return dump_data

    def load_json(self, data):
        load_data = json.loads(data)
        # print(f"{load_data = }")
        return load_data
    
    
    def get_data(self) -> dict:
        if not self.is_connected:
            return None

        return self.recv_data
    
    def process(self):
        _config = self.config
        _exist_sock = False
        
        _host_bind = self.host_bind
        _remote_bind = self.remote_bind
        _create_socket = self.create_socket
        _connect_socket = self.connect_remote

        _update_interval = _config.update_interval
        _buffer = _config.buffer
        
        sync_time = time()
        while 1:
            if not self.is_connected:
                if not _exist_sock:
                    _sock =  _create_socket(_host_bind)
                    # _sock.settimeout(1/_update_interval)
                    _exist_sock = True
                if _connect_socket(_sock, _remote_bind):
                    self.is_connected = True
                else:
                    self.is_connected = False
                    sleep(3)
                    continue
            
            try:
                _sock.send('temp')

                _raw_data, recv_time = _sock.recv(_buffer), time()
                self.recv_data.update(json.loads(_raw_data))
            except _sock.timeout:
                print(f"Raise {self.name} socket timeout...")

            except Exception as err:
                print(f"{err= }")
                self.is_connected = False
                _sock.close()
                _exist_sock = False
                
                
            dt = time() - sync_time
            if _update_interval - dt >0:
                sleep(_update_interval - dt)
            sync_time = time()
            

class ObuSocket(SocketModule):
    def __init__(self, config: ObuSocketParam, middle_ware) -> None:
        self.run_recv = False
        self.run_send = False
        self.send_queue = deque([])
        self.middle_ware = middle_ware
        super().__init__(config)

        self.sock = self.create_socket(protocol='udp')
    
        self.thread_process = Thread(target=self.process, daemon=True)
        self.thread_process.start()

    def put_queue_data(self, data):
        self.send_queue.append(data)
    
    def recv_obu_data(self):
        func_name = f'{self.__class__.__name__}::{sys._getframe().f_code.co_name}'
        _sock = self.sock
        _config = self.config
        _buffer = _config.buffer
        middle_ware = self.middle_ware
        set_data = middle_ware.set_obu_data

        while self.run_recv:            
            try:
                raw_data, server_addr = _sock.recvfrom(_buffer)
                backup_recv_raw_log.info(f"{raw_data.hex()}")
                recv_time = time()
                set_data(raw_data)
            
            except socket.timeout:
                pass
            except (
                ConnectionError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
            ) as err:
                # sys_log.error(f"{func_name},Disconnected: {self.__class__.__name__}({self.remote_bind}).")
                error_log.error(f"{func_name},Disconnected: {self.__class__.__name__}({self.remote_bind}).")

            
    def send_obu_data(self):
        _config = self.config
        _sock = self.sock
        _remote_bind = self.remote_bind
        
        tablet_sock = self.create_socket(_config.host_bind,'udp')
        tablet_bind = _config.tablet_bind  # ETRI 태블릿 정보 추가할 것

        _update_interval = _config.update_interval
        middle_ware = self.middle_ware
        
        _bsm = middle_ware.ego_bsm
        _cim = middle_ware.cim
        _tablet_bsm = middle_ware.tablet_bsm
        
        sync_time = time()

        send_queue = self.send_queue
        while self.run_send:
            # try:
            if not middle_ware.ego_l2id:
                if send_queue:
                    queue_data = send_queue.popleft()
                    # print(f"{queue_data = }")
                    _sock.sendto(queue_data.pack_data(), _remote_bind)
                    # print(f"Request L2ID: {queue_data}")
                sleep(_update_interval)
                continue
            if send_queue:
                queue_data = send_queue.popleft()
                pack_data = queue_data.pack_data()
                _sock.sendto(pack_data, _remote_bind)
                log_msg = ''
                for key, val in queue_data.to_dict().items():
                    log_msg += f"{key}={val}"
                backup_send_log.info(f"{log_msg}")
                backup_send_raw_log.info(f"{pack_data.hex()}")
            _sock.sendto(_bsm.pack_data(), _remote_bind)
            _sock.sendto(_cim.pack_data(), _remote_bind)
            tablet_sock.sendto(_tablet_bsm.pack_data(), tablet_bind)
                # print(f"BSM DATA:: {bsm}")
                # print(f"CIM DATA:: {cim}")
                    # print(f'{queue_data = }')
                
            # except Exception as err:
            #     print(f"RSU send ERROR::{err = }")
            #     sleep(3)
            
            dt = time() - sync_time
            if _update_interval > dt:
                sleep(_update_interval - dt)
            sync_time = time()

    def process(self):
        self.threading_recv = Thread()
        self.threading_send = Thread()
        # self.run_recv = False
        sys_log.info(f"Run {self.__class__.__name__} modules process")
        while 1:
            if not self.run_recv and not self.threading_recv.is_alive():
                self.threading_recv = Thread(target=self.recv_obu_data)
                self.run_recv = True
                self.threading_recv.start()

            if not self.run_send and not self.threading_send.is_alive():
                self.threading_send = Thread(target=self.send_obu_data)
                self.run_send = True
                self.threading_send.start()
                
            sleep(1)
            
class VehicleSocket(SocketModule):
    def __init__(self, config: VehicleSocketParam, middle_ware) -> None:
        self.middle_ware = middle_ware
        self.json_data = defaultdict(lambda: None)
        self.send_queue = deque([])
        super().__init__(config)

        self.threading_run = Thread(target=self.process, daemon=True)
        self.threading_run.start()
        
    def set_obu_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError
        
        obu2veh_data = ObuToVehicleData()
        obu2veh_data.obu_message = data
        if data.get('dmm') is not None and data.get('dmm').msg_type == MessageType.DMM_NOIT:
            obu2veh_data.msg_type = MessageType.DMM_NOIT
            obu2veh_data.maneuver_command = ManeuverCommandType.SLOW_DOWN
        elif data.get('edm') is not None and data.get('edm').msg_type == MessageType.EDM_NOIT:
            obu2veh_data.msg_type = MessageType.EDM_NOIT
            obu2veh_data.maneuver_command = ManeuverCommandType.SLOW_DOWN
        elif data.get('bsm') is not None and data.get('bsm').msg_type == MessageType.BSM_NOIT:
            obu2veh_data.msg_type = MessageType.BSM_NOIT
            obu2veh_data.maneuver_command = ManeuverCommandType.SLOW_DOWN
        else:
            obu2veh_data.msg_type = MessageType.UNKNOWN
            obu2veh_data.maneuver_command = ManeuverCommandType.NONE

        self.send_queue.append(obu2veh_data)
        
    
    def process(self):
        func_name = f'{self.__class__.__name__}::{sys._getframe().f_code.co_name}'
        
        _dump_data = self.dump_json
        _load_json = self.load_json
        _send_queue = self.send_queue
        _buffer = self.config.buffer
        _interval = self.config.update_interval
        
        sync_time = time()
        _middle_ware = self.middle_ware
        sys_log.info(f"Run {self.__class__.__name__} modules process")
        _sock = None
        while 1:
            if _sock is None:
                _sock = self.create_socket()
            if not self.is_connected:
                if self.connect_remote(_sock):
                    self.is_connected = True
                    sync_time = time()
                else:
                    self.is_connected = False
                    sleep(2)
                continue

            try:
                if _send_queue:
                    obu2veh_data = _send_queue.popleft()
                else:
                    obu2veh_data = ObuToVehicleData()
                _sock.send(_dump_data(obu2veh_data.to_dict()).encode())
                
                raw_vehicle = _sock.recv(_buffer).decode()
                # print(f"{raw_vehicle = }")
                # vehicle_data = VehicleData()
                _middle_ware.set_vehicle_data(_load_json(raw_vehicle))
                # vehicle_data.update_data(_load_json(raw_vehicle))
                # print(f"{vehicle_data = }")
                # vehicle_data.from_json(raw_vehicle)
                # self.recv_data.update(_load_json(raw_vehicle))
                # update_count += 1
            
            except socket.timeout:
                print(f'Socket Timeout...')
            except (
                ConnectionError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
            ) as err:
                # sys_log.error(f"{func_name},Disconnected: {self.__class__.__name__}({self.remote_bind}).")
                error_log.error(f"{func_name},Disconnected: {self.__class__.__name__}({self.remote_bind}).")
                _sock.close()
                _sock = None
                self.is_connected = False
                
                
            dt = time() - sync_time
            if dt < _interval:
                sleep(_interval-dt)
            sync_time = time()
