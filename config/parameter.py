


class RemoteAddress:
    VEHICLE_BIND = ('localhost', 29000)
    # OBU_BIND = ('',63113)
    #tester
    OBU_BIND = ('localhost',63113)


class HostAddress:
    VEHICLE_BIND = ('localhost', 29001)
    # OBU_BIND = ('',50002)
    #tester
    OBU_BIND = ('localhost',50002)


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
    
if __name__ == '__main__':
    a = ObuSocketParam
    print(a.name)