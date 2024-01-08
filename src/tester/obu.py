import socket
from time import time, sleep

from config.obu_contant import DataFormat
from config.parameter import RemoteAddress
from src.obu.classes import *


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RemoteAddress.OBU_BIND)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

bsm = BsmData()
_update_interval = 0.1
sync_time = time()
while 1:
    recv_raw, addr = sock.recvfrom(1024)
    msg_type = bsm.unpack_header(recv_raw)
    # print(MSG_TYPE[msg_type](l2id = 1234))
    if msg_type == 101:
        a = L2idResponseData(1234)
        sock.sendto(a.pack_data(DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_RESPONSE), addr)
        # print(f'{L2idResponseData(1234).pack_data(DataFormat.BYTE_ORDER+DataFormat.HEADER+DataFormat.L2ID_RESPONSE)}')
    sock.sendto(bsm.pack_data(), addr)
    
    sock.sendto(EdmData().pack_data(), addr)
    
    sock.sendto(DnmRequestData().pack_data(), addr)

    sock.sendto(DnmDoneData().pack_data(), addr)


    dt = time() - sync_time
    if _update_interval > dt:
        sleep(_update_interval - dt)
    sync_time = time()