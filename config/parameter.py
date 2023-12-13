


class RemoteAddress:
    VEHICLE_BIND = ('localhost', 29000)
    OBU_BIND = ('',29001)


class CommunicatorConfig:
    update_rate: int = 10  # unit: hz
    update_interval = 1/update_rate
    
    buffer: int = 1024