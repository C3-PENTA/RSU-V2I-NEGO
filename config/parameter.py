


class RemoteAddress:
    VEHICLE_BIND = ('localhost', 20000)
    TABLET_BIND = ('192.168.11.100', 63113)
    OBU_BIND = ("192.168.11.204", 63112)
    #tester
    # OBU_BIND = ('localhost',63112)
    # TABLET_BIND = ('localhost', 63113)


class HostAddress:
    VEHICLE_BIND = ('localhost', 28000)
    OBU_BIND = ('192.168.11.200',63112)
    #tester
    # OBU_BIND = ('localhost',50004)


class CommunicatorConfig:
    name = ''
    remote_bind = ''
    host_bind = ''

    update_rate: int = 10  # unit: hz
    update_interval = 1/update_rate
    
    buffer: int = 1024


class ObuSocketParam(CommunicatorConfig):
    name = 'OBU'
    remote_bind = RemoteAddress.OBU_BIND
    host_bind = HostAddress.OBU_BIND
    tablet_bind = RemoteAddress.TABLET_BIND


class VehicleSocketParam(CommunicatorConfig):
    name = 'vehicle'
    remote_bind = RemoteAddress.VEHICLE_BIND
    host_bind = HostAddress.VEHICLE_BIND


class MiddleWareParam:
    update_rate: int = 10
    update_interval = 1/update_rate
    nearby_data_timeout = 3
    target_bsm_l2id = 5555


class VehicleSpec:
    WIDTH: int = 182  # unit: cm
    LENGTH: int = 446  # unit: cm
    
    
class LoggerParam:
    backup: bool = False
    backup_recv_raw: bool = False
    backup_send_raw: bool = False
    backup_recv_data: bool = False
    backup_send_data: bool = False


if __name__ == '__main__':
    a = ObuSocketParam
    print(a.name)