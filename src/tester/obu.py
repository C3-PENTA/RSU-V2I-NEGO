import socket
from time import time, sleep
from collections import deque
from random import choice
from threading import Thread

from config.obu_contant import DataFormat
from config.parameter import RemoteAddress
from src.obu.classes import *
from src.tester.test_data import TEST_DATA, SEND_INTERVAL, SEND_RANDOM, SEND_DNM


class ObuTest():
    def __init__(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(RemoteAddress.OBU_BIND)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.2)
        self.sock = sock
        self.addr = None
        self.l2id = 1234
        self.is_l2id = False

        self._update_interval = 0.1
        self.queue = deque([], maxlen=5)

    def recv_threading(self):
        sock = self.sock
        bsm = BsmData()
        l2id = self.l2id
        while 1:
            try:
                recv_raw, _addr = sock.recvfrom(1024)
                self.addr = _addr
                msg_type = bsm.unpack_header(recv_raw)                    
                if msg_type == 101:
                    self.queue.append(L2idResponseData(l2id).pack_data(DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_RESPONSE))
                    self.is_l2id = True
                    # print(f"{msg_type = }")
                elif msg_type == 5:
                    self.queue.append(TEST_DATA["DNM_DONE"])
                # elif msg_type == 8:
                #     print(f"{recv_raw = }")
                obu_data = MSG_TYPE[msg_type](l2id=l2id)
                obu_data.unpack_data(recv_raw)
                if msg_type != 8 and msg_type != 9:
                    print(f"{obu_data = }")
            except TimeoutError:
                pass
            except (
                ConnectionError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
            ):
                pass

    def process(self):
        recv_thread = Thread(target=self.recv_threading, daemon=True)
        recv_thread.start()
        # send_thread = Thread(target=self.send_threading, daemon=True, args=(sock, addr, is_l2id))
        # send_thread.start()
        sock = self.sock
        _update_interval = self._update_interval
        count = 0
        sync_time = time()
        while 1:
            if self.addr is None or not self.is_l2id:
                sleep(1)
                continue
            byte_data = choice(SEND_RANDOM)
            sock.sendto(byte_data, self.addr)
            if self.queue:
                byte_data = self.queue.popleft()
                sock.sendto(byte_data, self.addr)
                
            if not count%10:
                byte_data = choice(SEND_INTERVAL)
                sock.sendto(byte_data, self.addr)
            if not count%20:
                byte_data = SEND_DNM
                sock.sendto(byte_data, self.addr)
            count += 1

            dt = time() - sync_time
            if _update_interval > dt:
                sleep(_update_interval - dt)
            sync_time = time()

if __name__ == "__main__":
    test = ObuTest()
    test.process()