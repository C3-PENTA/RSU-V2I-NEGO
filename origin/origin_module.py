import socket
from time import time, sleep
from threading import Thread

from origin.classes import ObuMessage, GPSData

class ObuOrigin:
    def __init__(self) -> None:
        self._runUpdateRsu = True
        self.vehicle_is_connected = False
        self.gps = GPSData()

        self.vehicle_thread = Thread()

        self.obu_thread = Thread(target=self._update_obu_data)
        self.obu_thread.start()
    
    def update_vehicle(self):
        update_rate = 10
        update_interval = 1 / update_rate
        remote_addr = ("localhost",29000)
        
        self.vehicle_is_connected = False

        sync_time = time()
        while 1:
            if not self.vehicle_is_connected:
                try:
                    vehicle_sock = socket.socket()
                    vehicle_sock.bind(("localhost",29001))
                    vehicle_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    vehicle_sock.settimeout(1)
                    vehicle_sock.connect()
                    self.vehicle_is_connected = True
                except Exception as err:
                    print(f"{err = }")
                    sleep(1)
                    continue
                
            try:
                vehicle_sock.send('all'.encode())
                recv_data = vehicle_sock.recv(1024)
                self.gps = recv_data['gps']
                self.vcan = recv_data['vcan']

            except Exception as err:
                print(f"{err = }")
                vehicle_sock.close()
                self.vehicle_is_connected = False
            
            dt = time() - sync_time
            if update_interval < dt:
                continue
            sleep(update_interval - dt)
        
        
    def _update_obu_data(self):  # send
        update_rate = 1 / 10
        remote_addr = ("192.168.1.153", 63113)  # OBU addr
        # remote_addr = ('112.216.45.26',50003)  # 상암 8208

        test_mode = False
        self.rsu_data = ObuMessage(test_mode)
        self.rep_q = []
        _rsu_data = self.rsu_data
        pre_turn_signal = 0

        rsu_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rsu_sock.bind(("", 50004))
        rsu_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rsu_sock.settimeout(1)

        thread_recv = Thread(target=self.thread_rsu_recv, args=(rsu_sock,))
        thread_recv.start()

        s_time = time()
        while self._runUpdateRsu:
            try:
                if not self.vehicle_is_connected:
                    sleep(3)
                    continue
                if not _rsu_data.is_l2id:
                    rsu_sock.sendto(_rsu_data.get_l2id_req(), remote_addr)
                    sleep(1)
                    continue
                # rsu_sock.sendto(bsm_bytes, remote_addr)
                rsu_sock.sendto(_rsu_data.get_bsm_bytes(self.gps), remote_addr)
                rsu_sock.sendto(_rsu_data.get_cim_bytes(), remote_addr)

                # current_turn_signal = self.vcan.turn_signal
                # if current_turn_signal != pre_turn_signal:
                #     if current_turn_signal:
                #         rsu_sock.sendto(
                #             _rsu_data.get_dmm_bytes(current_turn_signal + 1),
                #             remote_addr,
                #         )
                #     pre_turn_signal = current_turn_signal

                current_turn_signal = self.vcan.turn_signal
                if 0 < current_turn_signal < 3:
                    rsu_sock.sendto(
                        _rsu_data.get_dmm_bytes(current_turn_signal + 1),
                        remote_addr,
                    )
                    # print(f'{_rsu_data.get_dmm_bytes(current_turn_signal) = }')

                # sleep(0.1)
                if self.rep_q:
                    self.rep_q.pop()
                    rsu_sock.sendto(_rsu_data.get_dnm_rep_bytes(), remote_addr)
                    # print(f'{_rsu_data.get_dnm_rep_bytes() = }')

            except Exception as err:
                print(f"RSU sned ERROR::{err = }")
                sleep(0.05)
                continue

            e_time = time()
            dt = e_time - s_time
            s_time = e_time
            if dt > update_rate:
                continue
            sleep(update_rate - dt)

    def thread_rsu_recv(self, sock):  # recv
        rsu_data = self.rsu_data

        while self._runUpdateRsu:
            try:
                raw_data, server_addr = sock.recvfrom(1024)
                rsu_data.set_obu_data(raw_data)
                hex_data = raw_data.hex()
                # print(f'{hex_data = }')
                msg_type = hex_data[4:6]
                if msg_type == "04":
                    self.rep_q.append(1)
                    print(f"Send {msg_type} rep")
            except socket.timeout:
                # print(f"RSU Server Socket timeout")
                self.rep_q.clear()


def run_rsu():
    rsu = ObuOrigin()