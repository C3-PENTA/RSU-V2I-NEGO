from collections import deque
from time import time, sleep
import socket
import json
from threading import Thread

from config.parameter import VehicleSocketParam, ObuSocketParam, CommunicatorConfig
from obu.middleware import Middleware


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
        self.run_thread = Thread(target=self.process, name=self.name, daemon=True)
        self.run_thread.start()
    
    def create_socket(self, bind = None, protocol = None):
        if protocol == 'udp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            sock = socket.socket()
            sock.settimeout(self.config.update_interval*2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bind is None:
            bind = self.host_bind
        sock.bind(bind)

        self.sock = sock
        return sock 
    
    
    def connect_remote(self, sock: socket.socket = None, remote_bind = None):
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
        except Exception as err:
            print(f'{err = }')
            self.is_connected = False
            return False

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
    def __init__(self, config: ObuSocketParam, middle_ware: Middleware) -> None:
        super().__init__(config)
        self.send_queue = deque([])
        self.middle_ware = middle_ware

        self.sock = self.create_socket()
    
        self.run_send = True
        self.run_recv = True


    def put_queue_data(self, data):
        self.send_queue.append(data)
    
    def recv_obu_data(self):
        _sock = self.sock
        _config = self.config

        while 1:
            try:
                raw_data, server_addr, recv_time = _sock.recvfrom(_config.buffer), time()
            
            except socket.timeout:
                sleep(1)
            except Exception as err:
                print(f"{err =}")
            
    def send_obu_data(self):
        _config = self.config
        _exist_sock = False if self.sock is None else True
        _sock = self.sock
        
        _remote_bind = self.remote_bind

        _update_interval = _config.update_interval
        
        is_l2id = False
        
        sync_time = time()

        bsm = self.middleware.bsm
        cim = self.middleware.cim
            
        while 1:
            try:
                if not is_l2id:
                    _sock.sendto('l2id_req', _remote_bind)
                    sleep(1)
                    continue
                
                _sock.sendto("bsm", _remote_bind)
                _sock.sendto("cim", _remote_bind)
                
                if "turn_signal":
                    _sock.sendto("dmm",_remote_bind)
            
                if "reponse":
                    _sock.sendto("dnm_rep", _remote_bind)
            
            except Exception as err:
                print(f"RSU sned ERROR::{err = }")
                sleep(0.05)
            
            
            
            dt = time() - sync_time
            if _update_interval - dt >0:
                sleep(_update_interval - dt)
            sync_time = time()

    def run(self):
        self.threading_recv = Thread()
        self.threading_send = Thread()
        
        while 1:
            if not self.run_recv and self.threading_recv.is_alive():
                self.threading_recv = Thread(target=self.recv_obu_data)
                self.threading_recv.start()
                
            if not self.run_send and self.threading_send.is_alive():
                self.threading_send = Thread(target=self.send_obu_data)
                self.threading_send.start()

            sleep(3)
            
            
class VehicleSocket(SocketModule):
    def __init__(self, config: VehicleSocketParam) -> None:
        self.json_data = {'time':time()}
        super().__init__(config)

        # self.threading_run = Thread(target=self.process, daemon=True)
        
    def set_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError
        
        self.json_data['time'] = time()
        self.json_data.update(data)
    
    def dump_json(self, data=None):
        if data is None:
            data = self.json_data
        dump_data = json.dumps(data)
        return dump_data

    def load_json(self, data):
        load_data = json.load(data)
        return load_data
    
    def process(self):
        
        _data = self.dump_json
        load_json = self.load_json
        _buffer = self.config.buffer
        _interval = self.config.update_interval
        
        update_count = 0
        sync_time = time()
        
        while 1:
            if not self.is_connected:
                _sock = self.create_socket()
                if self.connect_remote(_sock):
                    self.is_connected = True
                else:
                    self.is_connected = False
                    sleep(2)
                sync_time = time()
                continue

            try:
                
                _sock.send(_data())
                
                raw_vehicle = _sock.recv(_buffer)
                self.recv_data.update(load_json(raw_vehicle))
                # update_count += 1
            
            except socket.timeout:
                update_count = 0
                print(f'Socket Timeout...')
                
                
            dt = time() - sync_time
            if dt < _interval:
                sleep(_interval-dt)
                sync_time = time()
