import socket
from collections import deque
from random import choice
from threading import Thread
from time import sleep, time

from config.obu_contant import DataFormat, MessageType
from config.parameter import MiddleWareParam, ObuSocketParam, RemoteAddress
from src.obu.classes import MSG_TYPE, BsmData, DmmData, EdmData, L2idResponseData
from src.tester.test_data import SEND_RANDOM, TEST_DATA


class ObuTest():
    def __init__(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.bind(('localhost', 59450))
        sock.bind(('192.168.11.200', 59450))
        # sock.bind(RemoteAddress.OBU_BIND)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.2)
        self.sock = sock
        self.addr = None
        self.l2id = 1234
        self.is_l2id = False

        self.slow_bsm_trigger = False
        self.dmm_trigger = False
        self.edm_trigger = False
        
        self._update_interval = MiddleWareParam.update_interval
        self.queue = deque([], maxlen=5)

    def recv_threading(self):
        sock = self.sock
        bsm = BsmData()
        l2id = self.l2id
        l2id_rep = L2idResponseData()
        l2id_rep.l2id = l2id
        while 1:
            try:
                recv_raw, _addr = sock.recvfrom(1024)
                # print(f"{recv_raw = }")
                self.addr = _addr
                msg_type = bsm.unpack_header(recv_raw)                    
                if msg_type == 101:
                    self.queue.append(l2id_rep.pack_data(DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_RESPONSE))
                    print(f"{l2id_rep = }")
                    self.is_l2id = True
                    # print(f"{msg_type = }")
                elif msg_type == 5:
                    self.queue.append(TEST_DATA["DNM_DONE"])
                # elif msg_type == 8:
                #     print(f"{recv_raw = }")
                obu_data = MSG_TYPE[msg_type](l2id=l2id)
                obu_data.unpack_data(recv_raw)
                # if msg_type != 8 and msg_type != 9:
                #     print(f"{obu_data = }")
            except TimeoutError:
                pass
            except (
                ConnectionError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
            ):
                pass

    def input_command(self):
        # TODO: Input을 넣어도 상위에서 반응이 없음
        
        while 1:
            input_cmd = input(f'BSM:1({self.slow_bsm_trigger}) DMM:3({self.dmm_trigger}) EDM:7({self.edm_trigger}) : ')
            if not str.isdigit(input_cmd):
                print(f"input command is not integer. Command type is only int")
                continue
            cmd_type = int(input_cmd)
            
            if cmd_type == MessageType.BSM_NOIT:
                if self.slow_bsm_trigger:
                    self.slow_bsm_trigger = False
                else:
                    self.slow_bsm_trigger = True
            elif cmd_type == MessageType.DMM_NOIT:
                if self.dmm_trigger:
                    self.dmm_trigger = False
                else:
                    self.dmm_trigger = True
            elif cmd_type == MessageType.EDM_NOIT:
                if self.edm_trigger:
                    self.edm_trigger = False
                else:
                    self.edm_trigger = True
            else:
                print(f"It's an unknown command type")
                

    def process(self):
        recv_thread = Thread(target=self.recv_threading, daemon=True)
        # recv_thread.start()
        input_thread = Thread(target=self.input_command, daemon=True)
        input_thread.start()
        # send_thread = Thread(target=self.send_threading, daemon=True, args=(sock, addr, is_l2id))
        # send_thread.start()
        sock = self.sock
        tablet_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # tablet_sock.bind(('localhost',63114))
        tablet_sock.bind(('192.168.11.200',63115))
        tablet_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tablet_addr = ObuSocketParam.tablet_bind
        _update_interval = self._update_interval
        count = 0
        sync_time = time()
        
        dmm_data = DmmData()
        dmm_data.sender = 4321
        slow_bsm_data = BsmData()
        slow_bsm_data.transmission_and_speed = 9
        slow_bsm_data.l2id = MiddleWareParam.target_bsm_l2id

        dmm_data.maneuver_type = 1
        
        
        edm_data = EdmData()
        edm_data.maneuver_type = 2
        edm_data.sender = 4321
        self.addr = ('192.168.11.200', 63112)
        self.is_l2id = True
        while 1:
            if self.addr is None or not self.is_l2id:
                sleep(1)
                continue
            # byte_data = choice(SEND_RANDOM)
            # sock.sendto(byte_data, self.addr)
            # tablet_sock.sendto(byte_data, tablet_addr)
            if self.queue:
                byte_data = self.queue.popleft()
                sock.sendto(byte_data, self.addr)
                
            if self.slow_bsm_trigger:
                sock.sendto(slow_bsm_data.pack_data(), self.addr)
            
            if self.dmm_trigger:
                sock.sendto(dmm_data.pack_data(), self.addr)
                # print(f"{dmm_data = }")
                
            if self.edm_trigger:
                sock.sendto(edm_data.pack_data(), self.addr)
                # print(f"{edm_data = }")
                
                
            # if not count%10:
            #     byte_data = choice(SEND_INTERVAL)
            #     sock.sendto(byte_data, self.addr)
            # if not count%20:
            #     byte_data = SEND_DNM
            #     sock.sendto(byte_data, self.addr)
            count += 1

            dt = time() - sync_time
            if _update_interval > dt:
                sleep(_update_interval - dt)
            sync_time = time()

if __name__ == "__main__":
    test = ObuTest()
    test.process()