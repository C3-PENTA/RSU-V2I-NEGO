from collections import deque
from time import time, sleep
import socket
import json
from threading import Thread

from config.parameter import CommunicatorConfig


class SocketModule:
    def __init__(self, name, host_bind: tuple, remote_bind: tuple, *argv, **kward) -> None:
        self.name = name
        self.host_bind = host_bind
        self.remote_bind = remote_bind
        self.socket_type = kward.get('type') if kward.get('type') else 'tcp'
        
        self.config = CommunicatorConfig

        self.sock = None
        self.is_connected: bool = False


        self.run_thread = Thread(target=self.run, name='run', daemon=True)
        self.run_thread.start()
    
    def create_socket(self, bind = None):
        sock = socket.socket()
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
            
        try:
            sock.connect(remote_bind)
        except Exception as err:
            print(f'{err = }')
            return False

        return True
    
    def set_data(self, data):
        self.send_data = json.dumps(data)
    
    
    def get_data(self):
        if not self.is_connected:
            return None

        return self.raw_data
    
    
    
    
    
    def run(self):
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
                _sock.send(self.send_data)

                _raw_data, recv_time = _sock.recv(_buffer), time()
                self.raw_data = json.loads(_raw_data)
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
    def __init__(self, name, host_bind: tuple, remote_bind: tuple, *argv, **kward) -> None:
        super().__init__(name, host_bind, remote_bind, *argv, **kward)
        self.send_queue = deque([])

    

    def queue_data(self, data):
        self.send_queue.append(data)
    
    
    def run(self):
        _config = self.config
        _exist_sock = False
        
        _host_bind = self.host_bind
        _remote_bind = self.remote_bind
        _connect_socket = self.connect_remote

        _update_interval = _config.update_interval
        _buffer = _config.buffer
        
        _sock = self.create_socket(_host_bind)
        sync_time = time()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        dt = time() - sync_time
        if _update_interval - dt >0:
            sleep(_update_interval - dt)
        sync_time = time()