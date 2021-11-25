import os
import datetime
import time
import download_config_apply
import miner
import monitor
import send_email

CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
DOWNLOAD_GAP_TIME = 600
machaine = '1'
CONFIG_DICT = download_config_apply.get_config_data(CONFIG_PATH)

if __name__ == '__main__':
    send_email.send_email("open compute", "open compute", 0, 3)
    download_config_apply.download()
    download_config_apply.apply_operation()
    miner.start_mining(0, CONFIG_DICT)
    monitor.start_monitor(0, CONFIG_DICT)
    send_email.send_email("start mining", "start mining", 0, 3)
    while True:
        time.sleep(DOWNLOAD_GAP_TIME)
        download_config_apply.download()
        download_config_apply.apply_operation()