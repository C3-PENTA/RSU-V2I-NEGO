import os
import sys
from threading import Thread
from time import sleep

from config.loggers import sys_log
from src.obu.middleware import run_middleware

module_list = {'RSU':Thread(),}
def run_modules():
    while True:
        for name, module in module_list.items():
            if module is not None:
                if not module.is_alive():
                    module_thread = Thread(target=run_middleware, daemon=True, name=name)
                    module_list[name] = module_thread
                    module_thread.start()
                    sys_log.info(f"Start {name} module.")
            sleep(3)



# divide rsu module from vehicle
if __name__ == '__main__':
    run_modules()