import os
import sys
import datetime
import time
import send_email
import requests
import zipfile

GITHUB_LINK = 'https://github.com/liaozhijie/windows_control_miner/archive/refs/heads/main.zip'
FILE_PATH = 'C:/github/'
CP_PATH = 'C:/github/cp_github/'
NEED_OPERATION = False

def get_machine():
    pass

def get_operation(file_path):
    machine = get_machine()
    start_count = 0
    with open(file_path) as f:
        for line in f.split('\n'):
            if 'operation info' in line:
                start_count = 1
            if start_count == 0:
                continue
            if str(machine) + '|' in line:
                print ("operation: ", line)
                return line.strip(str(machine) + '|')
    print ("cat not find machine overclock param, check the config.txt")
    return False



def check_two_files(file1, file2):
    file1_list, file2_list = [], []
    with open(FILE_PATH + file1, 'r') as f1:
        for i in f1.split('\n'):
            file1_list.append(i.strip(' '))
    with open(FILE_PATH + file2, 'r') as f1:
        for i in f1.split('\n'):
            file2_list.append(i.strip(' '))

    if len(file1_list) != len(file2_list):
        return False
    else:
        for i in range(len(file1_list)):
            if file1_list[i] != file2_list[i]:
                return False
    return True


def download(retry_times = 3):
    try:
        r = requests.get(GITHUB_LINK)
        with open(FILE_PATH + "main.zip", "wb") as code:
            code.write(r.content)
        zip_file = zipfile.ZipFile(FILE_PATH + "main.zip")
        zip_list = zip_file.namelist()
        for f in zip_list:
            zip_file.extract(f, CP_PATH)
            if os.path.exists(FILE_PATH + f.split('/')[-1]) is False:
                zip_file.extract(f, FILE_PATH)
            elif 'config' in f and get_operation(CP_PATH + f) != get_operation(FILE_PATH + f.split('/')[-1]):
                zip_file.extract(f, FILE_PATH)
                NEED_OPERATION = True
            elif check_two_files(CP_PATH + f, FILE_PATH + f.split('/')[-1]) is False:
                zip_file.extract(f, FILE_PATH)

        zip_file.close()

    except Exception as err:
        time.sleep(60)
        if retry_times > 0:
            download(retry_times-1)
        else:
            send_email.send_email("download git fail", err, 1, 3)

def apply_operation():
    supported_order_list = ['get_current_log', 'stop_miner', 'start_miner', 'restart_miner', 'restart_monitor', 'shutdown', 'restart_compute']
    order_list = []
    if NEED_OPERATION == True:
        order_list = get_operation(FILE_PATH + "windows_control_miner-main/config.txt").split(',')
    
    for order in supported_order_list:
        if order == 'get_current_log' and order in order_list:
            pass
        elif order == 'stop_miner' and order in order_list:
            pass
        elif order == 'start_miner' and order in order_list:
            pass
        elif order == 'restart_miner' and order in order_list:
            pass
        elif order == 'restart_monitor' and order in order_list:
            pass
        elif order == 'shutdown' and order in order_list:
            pass
        elif order == 'restart_compute' and order in order_list:
            pass