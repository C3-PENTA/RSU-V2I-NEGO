import logging
from datetime import datetime
from logging import handlers
from pathlib import Path
from time import sleep, time


class Counter:
    def __init__(self, max_num = None) -> None:
        if max_num is None:
            max_num = 255  # 0~127 1 byte
        self.max_num = max_num
        self.count = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.max_num < self.count:
            self.count = 0
        return self.count
    

class LoggerManager(handlers.RotatingFileHandler):
    
    def __parse_filename__(self, filePath: Path, fileName: str) -> None:
        filePath.replace("\\", "/")
        self._path = filePath

        j = fileName.find(".")
        if j >= 0:
            self._filename = fileName[:j]
            self._file_ext = fileName[j+1:]
        else:
            self._filename = fileName
            self._file_ext = ""
    
    
    def __init__(self, filePath, fileName, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None) -> None:
        try:
            
            self.__parse_filename__(filePath, fileName)
            
            time_now = time()
            log_path_str = "."
            datetime_str = ""
            log_path_exists = False
            for i in range(2, -1, -1):
                datetime_now = datetime.fromtimestamp(time_now - i)
                datetime_str = datetime.strftime(datetime_now, "%Y%m%d_%H%M%S")
                (date_str, time_str) = datetime_str.split("_")
                log_path_str = f"{self._path}/{date_str}/{time_str}"
                if Path(log_path_str).exists():
                    log_path_exists = True
                    break
            
            if not log_path_exists:
                Path(log_path_str).mkdir(parents=True)
            
            new_filename = f"{log_path_str}/{self._filename}_{datetime_str}.{self._file_ext}"
        except Exception as err:
            print(f"LOGGER ERROR: {type(err)}, {err}")
            return
        
        super().__init__(
            new_filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount,
            encoding=encoding, delay=delay, errors=errors)
        
    
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        
        datetime_str = datetime.strftime(datetime.now(), "%Y%m%d_%H%M%S")
        dfn = f"{self._path}/{self._filename}_{datetime_str}.{self._file_ext}"
        self.rotate(self.baseFilename, dfn)
        
        if not self.delay:
            self.stream = self._open()
            
            
def get_logger(name: str = "ums",
    stream: bool = False, streamLevel: int = 20,
    filePath: str = "./logs", fileName: str = None,
    fileLevel: int = 10, maxBytes: int = 0, backup_data = False, working = True) -> logging.Logger:
    # 10MB = 10485760Bytes
    logger = logging.getLogger(name)
    if not working:
        logger.setLevel(99)
        return logger
    else:
        logger.setLevel(logging.DEBUG)
    
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(streamLevel)
        
        date_format = "%y%m%d %H:%M:%S"
        stream_format = "%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s"
        formatter_stream = logging.Formatter(stream_format, date_format)
        stream_handler.setFormatter(formatter_stream)
        
        logger.addHandler(stream_handler)
    
    if fileName:
        file_handler = LoggerManager(
            filePath=filePath, fileName=fileName, mode="a", maxBytes=maxBytes, backupCount=999)
        file_handler.setLevel(fileLevel)
        
        date_format = "%Y-%m-%d %H:%M:%S"
        file_format = "%(asctime)s.%(msecs)03d,%(name)s,%(levelname)s,%(message)s"
        if backup_data: 
            file_format = "%(asctime)s.%(msecs)03d,%(message)s"
        formatter_file = logging.Formatter(file_format, date_format)
        file_handler.setFormatter(formatter_file)
        
        logger.addHandler(file_handler)
    
    return logger