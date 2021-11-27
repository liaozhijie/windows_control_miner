import os
import datetime
import time
import download_config_apply
import miner
import monitor
import send_email
import sys
from multiprocessing import Process

CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
DOWNLOAD_GAP_TIME = 60
machaine = '1'

def monitor_process():
    os.system("C:/github/windows_control_miner-main/monitor.py")

if __name__ == '__main__':
    #send_email.send_email("open compute", "open compute", 0, 3)
    download_config_apply.download(1)
    CONFIG_DICT = download_config_apply.get_config_data(CONFIG_PATH)
    #miner.start_mining(0, CONFIG_DICT)
    
    p = Process(target=monitor_process, args=('start_monitor',))
    p.start()
    
    #send_email.send_email("start mining", "start mining", 0, 3)
    while True:
        print ("in while loop")
        time.sleep(DOWNLOAD_GAP_TIME)
        download_config_apply.download(1)
