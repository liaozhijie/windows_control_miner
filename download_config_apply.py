import os
import sys
import datetime
import time
import send_email
import requests
import zipfile
import miner
from multiprocessing import Process


GITHUB_LINK = 'https://github.com/liaozhijie/windows_control_miner/archive/refs/heads/main.zip'
FILE_PATH = 'C:/github/'
CP_PATH = 'C:/github/cp_github/'
NEED_OPERATION = False


def get_operation(file_path):
    machine = send_email.get_machine()
    start_count = 0
    with open(file_path, 'r') as f:
        for line in f:
            if 'operation info' in line:
                start_count = 1
            if start_count == 0:
                continue
            if str(machine) + '|' in line:
                print ("operation: ", line)
                return line.strip(str(machine) + '|').strip('\n')
    print ("cat not find machine overclock param, check the config.txt")
    return False



def check_two_files(file1, file2):
    file1_list, file2_list = [], []
    with open(file1, 'rb') as f1:
        file1_list = f1.read()
    with open(file2, 'rb') as f1:
        file2_list = f1.read()

    if file1_list != file2_list:
        return False
    
    return True


def download(if_apply_operation, retry_times = 3):
    print ("start download")
    NEED_OPERATION = False
    if_send_fail_email = 0
    try:
        r = requests.get(GITHUB_LINK)
        with open(FILE_PATH + "main.zip", "wb") as code:
            code.write(r.content)
        zip_file = zipfile.ZipFile(FILE_PATH + "main.zip")
        zip_list = zip_file.namelist()
        for f in zip_list[1:]:
            f_copy = f
            zip_file.extract(f_copy, CP_PATH)
            if os.path.exists(FILE_PATH + f) is False:
                zip_file.extract(f, FILE_PATH)
                if 'config' in f:
                    NEED_OPERATION = True
                if_send_fail_email = 1

            elif 'config.txt' in f and get_operation(CP_PATH + f) != get_operation(FILE_PATH + f):
                if_send_fail_email = 1
                zip_file.extract(f, FILE_PATH)
                NEED_OPERATION = True

            elif check_two_files(CP_PATH + f, FILE_PATH + f) is False:
                if_send_fail_email = 1
                zip_file.extract(f, FILE_PATH)

        zip_file.close()

    except Exception as err:
        print (err)
        if retry_times > 0:
            download(retry_times-1)
        else:
            print (datetime.datetime.now(), "download fail 3 times")
            if if_send_fail_email == 1:
                send_email.send_email("download git fail", err, 1, 3)

    if if_apply_operation == 1:
        print ("start apply")
        print ("NEED_OPERATION: ", NEED_OPERATION)
        apply_operation(NEED_OPERATION)

        
def get_process():
    import psutil
    process_list = []
    pids = psutil.pids()
    for pid in pids:
        process_list.append(psutil.Process(pid).name())
    return process_list
    
def get_current_log():
    CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
    config_dict = get_config_data(CONFIG_PATH)
    miner_software, start_file, num_of_gpu, limint_hashrate = config_dict['miner_info'].split(',')
    log_file = config_dict['log'] + max(os.listdir(config_dict['log'])) if 't-rex' not in miner_software else config_dict['log'] + 'trex_log.txt'
    with open(log_file, 'r') as f:
        return ('\n'.join(f.read().split('\n')[-50:]))
    
def stop_monitor():
    CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
    CONFIG_DICT = get_config_data(CONFIG_PATH)
    with open(CONFIG_DICT['log'] + 'if_stop_monitor.txt', 'w') as f:
        f.write("1")
        
def monitor_process():
    os.system("python C:/github/windows_control_miner-main/monitor.py")
        

def apply_operation(NEED_OPERATION):

    supported_order_list = ['get_current_log', 'start_miner', 'restart_miner', 'stop_miner', 'restart_monitor', 'shutdown', 'restart_compute']
    order_list = []
    if NEED_OPERATION == True:

        order_list = get_operation(FILE_PATH + "windows_control_miner-main/config.txt").split(',')
        print ('order_list',order_list)
        if order_list == False or len(order_list) > 1:
            send_email.send_email("get operation fail or order more than 1", "get operation fail or order more than 1", 1, 3)
            order_list = []
    config_dict = get_config_data(FILE_PATH + "windows_control_miner-main/config.txt")
    print ("config_dict", config_dict)
    process_list = get_process()
    
    for order in supported_order_list:
        if order == 'get_current_log' and order in order_list:
            content = get_current_log()
            send_email.send_email("get current log", content, 1, 3)
        elif order == 'stop_miner' and order in order_list:
            if 'cmd.exe' in process_list:
                os.system(r'taskkill /F /IM cmd.exe')
            elif 'qskg.exe' in process_list:
                os.system(r'taskkill /F /IM qskg.exe')
            send_email.send_email("stop_miner done", "stop_miner done", 1, 3)
            time.sleep(30)
        elif order == 'start_miner' and order in order_list:
            miner.start_mining(0, config_dict)
            send_email.send_email("start_miner done", "start_miner done", 1, 3)
            time.sleep(10)
        elif order == 'restart_miner' and order in order_list:
            if 'cmd.exe' in process_list:
                os.system(r'taskkill /F /IM cmd.exe')
                time.sleep(30)
            elif 'qskg.exe' in process_list:
                os.system(r'taskkill /F /IM qskg.exe')
                time.sleep(30)
            miner.start_mining(1, config_dict)
            send_email.send_email("restart_miner done", "restart_miner done", 1, 3)
            time.sleep(10)
        elif order == 'restart_monitor' and order in order_list:
            stop_monitor()
            time.sleep(30)
            p = Process(target=monitor_process)
            p.start()
            send_email.send_email("restart_monitor done", "restart_monitor done", 1, 3)
            time.sleep(10)
        elif order == 'shutdown' and order in order_list:
            os.system("shutdown -s -t 120")
            send_email.send_email("shutdown", "shutdown done", 1, 3)
        elif order == 'restart_compute' and order in order_list:
            os.system("shutdown -r -t 10")
            send_email.send_email("restart_compute", "restart_compute done", 1, 3)



def get_config_data(config_path):
    machine = send_email.get_machine()
    miner_info,overclock_info = 0, 0
    config_dict = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if 'miner info' in line:
                    miner_info = 1
                if 'overclock info' in line:
                    overclock_info = 1
                    miner_info = 0
                if 'operation info' in line:
                    overclock_info = 0

                if 'wallet' in line:
                    config_dict['wallet'] = line.split('|')[1].strip('\n')
                if 'pool' in line:
                    config_dict['pool'] = line.split('|')[1]
                if 'log|' in line:
                    config_dict['log'] = line.split('|')[1]
                if miner_info == 1 and str(machine) + '|' in line:
                    config_dict['miner_info'] = line.split('|')[1]
                if overclock_info == 1 and str(machine) + '|' in line:
                    config_dict['overclock_info'] = line.split('|')[1]
    except Exception as err:
        send_email.send_email("get config fail", err, 1, 3)
    return config_dict
