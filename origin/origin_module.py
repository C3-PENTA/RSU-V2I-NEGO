import socket
from time import time, sleep
from threading import Thread

from origin.classes import ObuMessage, GPSData

class ObuOrigin:
    def __init__(self) -> None:
        self.gps = GPSData()
        
    def _update_rsu(self):  # send
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