from collections import deque
from time import time, sleep
import socket
import json
from threading import Thread

# from src.obu.middleware import Middleware
from config.parameter import VehicleSocketParam, ObuSocketParam, CommunicatorConfig
from src.obu.classes import L2idRequestData
# import Middleware


class SocketModule:
    def __init__(self, config: CommunicatorConfig = None) -> None:
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
            sock.settimeout(self.config.update_interval*2)
        else:
            sock = socket.socket()
            sock.settimeout(self.config.update_interval*2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bind is None:
            bind = self.host_bind
        sock.bind(bind)

        self.sock = sock
        return sock 
    
    
    def connect_remote(self, sock = None, remote_bind = None):
        if sock is None:
            if self.sock is not None:
                sock = self.sock
            else:
                print(f"Don't exist socket")
                return False
        if remote_bind is None:
            if self.remote_bind is not None:
                remote_bind = self.remote_bind
            
        try:
            sock.connect(remote_bind)
        except socket.timeout:
            return False
        # except Exception as err:
        #     print(f'{err = }')
        #     self.is_connected = False
        #     return False

        return True

    
    def get_data(self) -> dict:
        if not self.is_connected:
            return None

        return self.recv_data
    
    def update_status(self, count):
        pass
    
    
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
                    _sock.settimeout(1/_update_interval)
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
        _sock = self.sock
        _config = self.config
        _buffer = _config.buffer
        middle_ware = self.middle_ware
        set_data = middle_ware.set_obu_data

        while self.run_recv:            
            try:
                raw_data, server_addr = _sock.recvfrom(_buffer)
                recv_time = time()
                set_data(raw_data)
            
            except socket.timeout:
                pass
            # except Exception as err:
            #     print(f"{err = }")
            
    def send_obu_data(self):
        _config = self.config
        _sock = self.sock
        
        _remote_bind = self.remote_bind

        _update_interval = _config.update_interval
        middle_ware = self.middle_ware
        
        bsm = middle_ware.bsm
        cim = middle_ware.cim
        
        sync_time = time()

        send_queue = self.send_queue
        while self.run_send:
            try:
                if not middle_ware.l2id:
                    queue_data = send_queue.popleft()
                    _sock.sendto(queue_data.pack_data(), _remote_bind)
                    sleep(1)
                    continue
                _sock.sendto(bsm.pack_data(), _remote_bind)
                _sock.sendto(cim.pack_data(), _remote_bind)
                if send_queue:
                    queue_data = send_queue.popleft()
                    _sock.sendto(queue_data.pack_data(), _remote_bind)
                    # print(f'{queue_data = }')
                
            except Exception as err:
                print(f"RSU sned ERROR::{err = }")
                sleep(3)
            
            dt = time() - sync_time
            if _update_interval > dt:
                sleep(_update_interval - dt)
            sync_time = time()

    def process(self):
        self.threading_recv = Thread()
        self.threading_send = Thread()
        # self.run_recv = False
        while 1:
            if not self.run_send and not self.threading_send.is_alive():
                self.threading_send = Thread(target=self.send_obu_data)
                self.run_send = True
                self.threading_send.start()
                
            if not self.run_recv and not self.threading_recv.is_alive():
                self.threading_recv = Thread(target=self.recv_obu_data)
                self.run_recv = True
                self.threading_recv.start()
            sleep(1)
            
class VehicleSocket(SocketModule):
    def __init__(self, config: VehicleSocketParam) -> None:
        self.json_data = {}
        super().__init__(config)

        self.threading_run = Thread(target=self.process, daemon=True)
        self.threading_run.start()
        
    def set_dict_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError
        
        self.json_data['time'] = time()
        self.json_data.update(data)
    
    def dump_json(self, data=None):
        if data is None:
            data = self.json_data
        dump_data = json.dumps(data)
        self.json_data.clear()
        return dump_data

    def load_json(self, data):
        load_data = json.load(data)
        return load_data
    
    def process(self):
        
        _data = self.dump_json
        _load_json = self.load_json
        _buffer = self.config.buffer
        _interval = self.config.update_interval
        
        sync_time = time()
        
        while 1:
            if not self.is_connected:
                _sock = self.create_socket()
                if self.connect_remote(_sock):
                    self.is_connected = True
                    sync_time = time()
                else:
                    self.is_connected = False
                    sleep(2)
                continue

            try:
                _sock.send(_data())
                
                raw_vehicle = _sock.recv(_buffer)
                self.recv_data.update(_load_json(raw_vehicle))
                # update_count += 1
            
            except socket.timeout:
                print(f'Socket Timeout...')
                
                
            dt = time() - sync_time
            if dt < _interval:
                sleep(_interval-dt)
            sync_time = time()
