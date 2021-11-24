import os
import datetime
import time

DOWNLOAD_GAP_TIME = 600
machaine = '1'


if __name__ == '__main__':
    download_config_and_apply
    send_email("open")
    start_miner_and_monitor
    send_email("start_miner")
    while True:
        download_config_and_apply
        time.sleep(DOWNLOAD_GAP_TIME)
