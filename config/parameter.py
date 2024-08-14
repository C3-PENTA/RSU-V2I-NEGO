


class RemoteAddress:
    VEHICLE_BIND = ('localhost', 20000)
    # OBU_BIND = ('',63113)
    #tester
    # OBU_BIND = ('localhost',63113)
    OBU_BIND = ("192.168.20.150", 63113)


class HostAddress:
    VEHICLE_BIND = ('localhost', 28000)
    # OBU_BIND = ('',50002)
    #tester
    OBU_BIND = ('192.168.20.2',50004)


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
    

class VehicleSocketParam(CommunicatorConfig):
    name = 'vehicle'
    remote_bind = RemoteAddress.VEHICLE_BIND
    host_bind = HostAddress.VEHICLE_BIND

class MiddleWareParam:
    update_rate: int = 10
    update_interval = 1/update_rate
    nearby_data_timeout = 3

class VehicleSpec:
    WIDTH: int = 182  # unit: cm
    LENGTH: int = 446  # unit: cm
    
if __name__ == '__main__':
    a = ObuSocketParam
    print(a.name)