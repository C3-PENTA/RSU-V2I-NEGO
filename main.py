import os
import sys
from time import sleep
from threading import Thread
from origin.origin_module import ObuOrigin, run_rsu
from src.obu.middleware import run_middleware

module_list = {'rsu':Thread(),}

def run_modules():
    thread_list = []
    while True:
        for name, module in module_list.items():
            if module is None:
                module_thread = Thread(target=run_rsu, daemon=True, name=name)
                module_list[name] = module_thread
                module_thread.start()
            else:
                if not module.is_alive():
                    module_thread = Thread(target=run_middleware, daemon=True, name=name)
                    module_list[name] = module_thread
                    module_thread.start()
            sleep(3)



# divide rsu module from vehicle
if __name__ == '__main__':
    run_modules()