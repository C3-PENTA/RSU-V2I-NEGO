import os
import sys
from time import sleep
from threading import Thread
from origin.origin_module import ObuOrigin, run_rsu

module_list = {'rsu':None,}

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
                    module_thread = Thread(target=run_rsu, daemon=True, name=name)
                    module_list[name] = module_thread
                    module_thread.start()

            sleep(1)


# divide rsu module from vehicle
if __name__ == '__main__':
    run_modules()