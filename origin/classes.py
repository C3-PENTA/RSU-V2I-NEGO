from time import time, sleep, strftime, localtime
from struct import pack, unpack


class Message():
    
    KEYS = ['name', 'status', 'lastUpdate', 'updateCount', 'updateRate']
    
    def __init__(self) -> None:
        self.name = ''
        self.status = STATE.DISCONNECTED
        self.lastUpdate = time()
        self.updateCount = 0
        self.updateRate = 0
        
    def get_stat(self):
        return {'name': self.name,
                'status': self.status,
                'lastUpdate': self.lastUpdate,
                'updateCount': self.updateCount,
                'updateRate': self.updateRate}
    
    def get_stat_string(self):
        return f'{self.name},{self.status},{self.lastUpdate},{self.updateCount},{self.updateRate}'


class GPSData(Message):
    NAME = 'GPSDATA'
    KEYS = MSG_COMMON_KEYS + [
        'utc', 'insStat', 'lat', 'lon', 'hgt', 'northVel', 'eastVel', 'upVel', 'roll', 'pitch', 'azimuth',
        'solStat', 'rtkStat', 'bestLat', 'bestLon', 'bestHgt', 'bestLatSig', 'bestLonSig', 'bestHgtSig',
        'latency', 'age', 'horSpd', 'heading', 'verSpd',
        'northing', 'easting', 'utmHgt', 'northSig', 'eastSig', 'hgtSig',
        'gpsVel', 'accuracy']
    
    def __init__(self):
        super().__init__()
        self.name = GPSData.NAME
        self.isAlive = False
        
        self.utc = 0
        self.week = 0
        self.seconds = 0
        
        self.insStat = 0
        self.lat = 0
        self.lon = 0
        self.hgt = 0
        self.northVel = 0
        self.eastVel = 0
        self.upVel = 0
        self.roll = 0
        self.pitch = 0
        self.azimuth = 0
        
        self.solStat = 2
        self.rtkStat = 0
        self.bestLat = 0
        self.bestLon = 0
        self.bestHgt = 0
        self.bestLatSig = 0
        self.bestLonSig = 0
        self.bestHgtSig = 0
        
        self.latency = 0
        self.age = 0
        self.horSpd = 0
        self.heading = 0
        self.verSpd = 0
        
        self.northing = 0
        self.easting = 0
        self.utmHgt = 0
        self.northSig = 0
        self.eastSig = 0
        self.hgtSig = 0
        self.zoneNumber = 0
        self.zoneLetter = ''
        
        self.gpsVel = 0
        self.accuracy = 0
        self.avgError = 0
        self.azimuth_rad = 0.0
        self.front_easting = 0.0
        self.front_northing = 0.0

    def set_values_from_string(self, data: str):
        funcName = f'set_values_from_string'
        
        data = data.split(',')
        if data[0] != self.name:
            return False
        
        self.status, self.lastUpdate, self.updateCount, self.updateRate = int(data[1]), float(data[2]), int(data[3]), float(data[4])
        self.utc = float(data[5])
        
        self.insStat = int(data[6])
        self.lat, self.lon, self.hgt, self.northVel, self.eastVel, self.upVel, self.roll, self.pitch, self.azimuth = [float(i) for i in data[7:16]]
        
        self.solStat, self.rtkStat = [int(i) for i in data[16:18]]
        self.bestLat, self.bestLon, self.bestHgt, self.bestLatSig, self.bestLonSig, self.bestHgtSig = [float(i) for i in data[18:24]]
        
        self.latency, self.age, self.horSpd, self.heading, self.verSpd = [float(i) for i in data[24:29]]

        self.northing, self.easting, self.utmHgt, self.northSig, self.eastSig, self.hgtSig = [float(i) for i in data[29:35]]
        
        self.gpsVel, self.accuracy = [float(i) for i in data[35:37]]
        
        return True
        
    def get_string(self):
        inspvasString = f'{self.insStat},{self.lat},{self.lon},{self.hgt},{self.northVel},{self.eastVel},{self.upVel},{self.roll},{self.pitch},{self.azimuth}'
        bestposString = f'{self.solStat},{self.rtkStat},{self.bestLat},{self.bestLon},{self.bestHgt},{self.bestLatSig},{self.bestLonSig},{self.bestHgtSig}'
        bestvelString = f'{self.latency},{self.age},{self.horSpd},{self.heading},{self.verSpd}'
        bestutmString = f'{self.northing},{self.easting},{self.utmHgt},{self.northSig},{self.eastSig},{self.hgtSig}'
        
        return f'{self.get_stat_string()},{self.utc},{inspvasString},{bestposString},{bestvelString},{bestutmString},{self.gpsVel},{self.accuracy}'



class ObuMessage():
    
    def __init__(self, test_mode = False) -> None:

        self.test_mode = test_mode
        self.logging_mode = True
        if self.logging_mode:
            self._set_log_file()
            
        self.__init_default()
    
    def __init_default(self):

        # self.__init_data()
        self.set_msg_type = {
            '01': self.set_bsm,
            '03': self.set_dmm,
            '04': self.set_dnm_req,
            '06': self.set_dnm_done,
            '07': self.set_edm,
            '21': self.set_bsm_light,
            '66': self.set_l2id_rep,
            }
        
        self.sender = 0
        self.receiver = 0
        self.dmm_receiver = 0
        
        self.__init_data()

        # common
        self.tmp_id: int = 0
        
        # bsm
        self.bsm_count: int = 0
        
        # l2id
        self.is_l2id = False
    
    def __init_data(self):
        
        self.msg_count: int = 0  # 1byte unsigned int
        self.tmp_id: int = 0  # 4bytes unsigned int
        self.dsecond: int = 0  # 2bytes unsigned int, units of millisec
        self.lat: int = 0  # 4bytes signed int, unit of micro degree
        self.lon: int = 0  # 4bytes signed int, unit of micro degree
        self.elevation: int = 0  # 2bytes unsigned int, unit of 0.1 meters, start value: -4096
        self.semi_major = 0  # 1byte, unknown...
        self.semi_minor = 0  # 1byte, unknown...
        self.orientation = 0  # 2bytes, unknown
        self.transmission_and_speed: int = 0  # 4bytes, unsigned int, unit of 0.02m/s
        self.heading: int = 0  # 2bytes, unsigned int, unit of 0.0125 degree
        self.steering_wheel_angle = 0  # 2bytes
        self.accel_long = 0  # 2bytes
        self.accel_lat = 0  # 2bytes
        self.accel_vert = 0  # 1byte
        self.yaw_rate = 0  # 2bytes
        self.brake_system_status = 0  # 2bytes
        self.width: int = 0  # 2bytes, unsigned int, unit of cm
        self.length: int = 0  # 2bytes, unsigned int, unit of cm
        self.l2id = 0  # 4bytes, usigned int
        
    def __del__(self):
        self.hex_log.close()
        self.data_log.close()
        
        print(f"close log file...")
    
    def _set_log_file(self):
        sync_str_time = strftime('%Y%m%d_%H_%M_%S', localtime())

        self.hex_log = open(f'logs/obu/hex/{sync_str_time}.log', 'a')
        self.data_log = open(f'logs/obu/data/{sync_str_time}.log', 'a')
        

    def set_bsm(self, data: bytes):

        unpack_data  = unpack('>BIHiiHBBHH HbHHBHHHHI', data[7:])
        bsm_data = {
        'msg_type': '01',
        'msg_count' : unpack_data[0],  # 1byte unsigned int
        'tmp_id' : unpack_data[1],  # 4bytes unsigned int
        'dsecond' : unpack_data[2],  # 2bytes unsigned int, units of millisec
        'lat' : unpack_data[3],  # 4bytes signed int, unit of micro degree
        'lon' : unpack_data[4],  # 4bytes signed int, unit of micro degree
        'elevation' : unpack_data[5],  # 2bytes unsigned int, unit of 0.1 meters, start value: -4096
        'semi_major' : unpack_data[6],  # 1byte, unknown...
        'semi_minor' : unpack_data[7],  # 1byte, unknown...
        'orientation' : unpack_data[8],  # 2bytes, unknown
        'transmission_and_speed' : round((unpack_data[9]&0b111111111111)*3.6*0.02,3),  # 1bytes, unsigned int, unit of 0.02m/s
        'heading' : unpack_data[10]*0.0125,  # 2bytes, unsigne9d int, unit of 0.0125 degree
        'steering_wheel_angle' : unpack_data[11],  # 1bytes
        'accel_long' : unpack_data[12],  # 2bytes
        'accel_lat' : unpack_data[13],  # 2bytes
        'accel_vert' : unpack_data[14],  # 1byte
        'yaw_rate' : unpack_data[15],  # 2bytes
        'brake_system_status' : unpack_data[16],  # 2bytes
        'width' : unpack_data[17],  # 2bytes, unsigned int, unit of cm
        'length' : unpack_data[18],  # 2bytes, unsigned int, unit of cm
        'l2id' : unpack_data[19],  # 4bytes, unknown...
        }

        if self.logging_mode:
            self.save_obu_data(bsm_data)

        return True

    def set_dmm(self, data: bytes):
        unpack_data = unpack('>IIHB',data[7:])
        dmm_data = {
            'msg_type': '03',
            'sender': unpack_data[0],
            'receiver': unpack_data[1],
            'maneuver_type': unpack_data[2],
            'remain_dist': unpack_data[3],
        }
        self.dmm_receiver = dmm_data['receiver']

        if self.logging_mode:
            self.save_obu_data(dmm_data)
            
        return True
            
    def set_bsm_light(self, data: bytes):
        unpack_data = unpack('>BIHiiHBBHHHbHHBHHHHIH', data[7:])
        bsm_data = {
            'msg_type': '33',
            'msg_count': unpack_data[0],  # 1byte unsigned int
            'tmp_id': unpack_data[1],  # 4bytes unsigned int
            'dsecond': unpack_data[2],  # 2bytes unsigned int, units of millisec
            'lat': unpack_data[3],  # 4bytes signed int, unit of micro degree
            'lon': unpack_data[4],  # 4bytes signed int, unit of micro degree
            'elevation': (unpack_data[5]-4096)*0.1,  # 2bytes unsigned int, unit of 0.1 meters, start value: -4096
            'semi_major': unpack_data[6],  # 1byte, unknown...
            'semi_minor': unpack_data[7],  # 1byte, unknown...
            'orientation': unpack_data[8],  # 2bytes, unknown
            'transmission_and_speed': round(unpack_data[9]&0b1111111111111*0.02*3.6,3),  # 2bytes, unsigned int, unit of 0.02m/s
            'heading': unpack_data[10]*0.0125,  # 2bytes, unsigned int, unit of 0.0125 degree
            'steering_wheel_angle': unpack_data[11],  # 1bytes
            'accel_long': unpack_data[12],  # 2bytes
            'accel_lat': unpack_data[13],  # 2bytes
            'accel_vert': unpack_data[14],  # 1byte
            'yaw_rate': unpack_data[15],  # 2bytes
            'brake_system_status': unpack_data[16],  # 2bytes
            'width': unpack_data[17],  # 2bytes, unsigned int, unit of cm
            'length': unpack_data[18],  # 2bytes, unsigned int, unit of cm
            'l2id': unpack_data[19],  # 4bytes, unknown...
            'light': unpack_data[20],  # 2bytes, unknown...
        }
        if self.logging_mode:
            self.save_obu_data(bsm_data)

        return True
        
    def set_dnm_req(self, data: bytes):
        unpack_data = unpack('>IIB',data[7:])
        # print(f'{unpack_data = }')

        dnm_req = {
            'msg_type': 4,
            'sender': unpack_data[0],
            'receiver': unpack_data[1],
            'remain_dist': unpack_data[2],
        }
        self.sender = dnm_req['receiver']
        self.receiver = dnm_req['sender']

        if self.logging_mode:
            self.save_obu_data(dnm_req)
        
        return True
            
    def set_dnm_done(self, data: bytes):
        unpack_data = unpack('>IIB',data[7:])
        dnm_done = {
            'msg_type': 6,
            'sender': unpack_data[0],
            'receiver': unpack_data[1],
            'nego_driving_done': unpack_data[2],
        }

        if self.logging_mode:
            self.save_obu_data(dnm_done)
        
        return True
            
    def set_edm(self, data: bytes):
        unpack_data = unpack('>IHB',data[7:])
        edm_data = {
            'msg_type': 7,
            'sender': unpack_data[0],
            'maneuver_type': unpack_data[1],
            'remain_dist': unpack_data[2],
        }
        if self.logging_mode:
            self.save_obu_data(edm_data)
            
        return True
    
    def set_l2id_rep(self, data: bytes):
        temp_data = 'f1f1661cab000b00554433'
        unpack_data = unpack('>HBHHI', data)
        l2id_data = {
            'magic':unpack_data[0],
            'msg_type': unpack_data[1],
            'crc-16':unpack_data[2],
            'packet_len':unpack_data[3],
            'l2id':unpack_data[4],
        }
        self.update_l2id(l2id_data['l2id'])
        if self.logging_mode:
            self.save_obu_data(l2id_data)
    
    def get_l2id_req(self):
        l2id_data = {
            'magic':61937,
            'msg_type': 101,
            'crc-16':0,
            'packet_len':7,
        }
        
        return pack('>HBHH',*l2id_data.values())

    def get_bsm_bytes(self, gps: GPSData):
        if self.test_mode:
            return bytes.fromhex('F1F1010000002B00000000010000165E581A4B776578000000000000000000000000000000000000000000C801F400000000')
            
        bsm_data = {
        'magic': 61937,
        'msg_type': 1,
        'crc-16': 0,
        'packet_len': 50,
        'msg_count': self.bsm_count,  # 1byte unsigned int
        'tmp_id': self.tmp_id,  # 4bytes unsigned int
        'dsecond': 0,  # 2bytes unsigned int, units of millisec
        'lat': int(gps.lat*10**6),  # 4bytes signed int, unit of micro degree
        'lon': int(gps.lon*10**6),  # 4bytes signed int, unit of micro degree
        'elevation': int(gps.hgt*10)+4096,  # 2bytes unsigned int, unit of 0.1 meters, start value: -4096
        'semi_major': 0,  # 1byte, unknown...
        'semi_minor': 0,  # 1byte, unknown...
        'orientation': 0,  # 2bytes, unknown
        'transmission_and_speed': int(gps.gpsVel*50),  # 1bytes, unsigned int, unit of 0.02m/s
        'heading': int(gps.heading*80),  # 2bytes, unsigned int, unit of 0.0125 degree
        'steering_wheel_angle': 0,  # 1bytes
        'accel_long': 0,  # 2bytes
        'accel_lat': 0,  # 2bytes
        'accel_vert': 0,  # 1byte
        'yaw_rate': 0,  # 2bytes
        'brake_system_status': 0,  # 2bytes
        'width': 182,  # 2bytes, unsigned int, unit of cm
        'length': 447,  # 2bytes, unsigned int, unit of cm
        'l2id': self.l2id,  # 4bytes, unknown...
        }

        pack_data = pack('>HBHHBIHiiHBBHHHbHHBHHHHI', *bsm_data.values())
        
        if self.bsm_count < 127:
            self.bsm_count += 1
        else:
            self.bsm_count = 0

        return pack_data
    
    def get_dmm_bytes(self, type = 3):
        dmm_data = {
            'magic': 61937,
            'msg_type': 3,
            'crc-16': 0,
            'packet_len': 18,
            'sender':self.l2id,
            'receiver': 0xffffffff,
            'maneuver_type': 0b1000,
            'remain_dist': 0,  # unit: m
        }
        
        return pack('>HBHHIIHB', *dmm_data.values())
    
    def get_cim_bytes(self):
        if self.test_mode:
            return bytes.fromhex('F1F1010000000300000000000000FFFFFF')

        cim_data = {
                    'magic': 61937,
                    'msg_type': 9,
                    'crc-16': 0,
                    'packet_len': 18,
                    'sender':self.l2id,
                    'vehicle_type': 10,
                    # 'vehicle_color': 0xffffff
                    }
        vehicle_color = [0,0,0,255,255,255]
        return pack('>HBHHIB', *cim_data.values()) + bytes(vehicle_color)
    
    def get_dnm_rep_bytes(self):
        
        dnm_rep_data = {
            'magic': 61937,
            'msg_type': 5,
            'crc-16': 0,
            'packet_len': 16,
            'sender': self.l2id,
            'receiver': self.receiver,
            'agreement_flag': 1,
        }
        print(f'{dnm_rep_data.values() = }')
        return pack('>HBHHIIB', *dnm_rep_data.values())
    
    # def save_obu_data(self, value: str):
    #     sync_str_time = strftime('%Y%m%d_%X', localtime())
    #     str_data = f"{sync_str_time} - {value}"
    
    def update_l2id(self, id):
        self.l2id = id
        self.is_l2id = True
    
    def save_obu_data(self, value: dict):
        sync_str_time = strftime('%Y%m%d_%X', localtime())
        log = self.data_log
        log_print = sync_str_time + ' ::'
        log.write(f"{sync_str_time} -")
        for key, val in value.items():
            log.write(f" {key}={val}")
            log_print += f" {key}={val}"
        log.write('\n')
        log.flush()
        print(log_print)
        return True

    def save_obu_hex_data(self, data: bytes):
        sync_str_time: str = strftime('%Y%m%d_%X', localtime())
        value = data.hex()
        str_data = f"{sync_str_time} - {value}"
        # self.hex_log.write(str_data)
        print(str_data, file=self.hex_log)
        self.hex_log.flush()
        return True
    
    def set_obu_data(self, data: bytes) -> bool:
        self.save_obu_hex_data(data)
        # try:
        msg_type = data.hex()[4:6]
        result = self.set_msg_type[msg_type](data)
        
        # except Exception as err:
        #     print(f'{err = }')
        #     return False
            
        return result