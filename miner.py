import time
import os
import datetime
import send_email

FILE_PATH = 'C:/github/'

def start_mining(if_restart, CONFIG_DICT):
    print ("start mining")
    miner_software, start_file_path = CONFIG_DICT['miner_info'].split(',')[:2]
    if if_restart == 1 and '轻松旷工' not in miner_software:
        os.system(r'taskkill /F /IM miner.exe')
        time.sleep(30)
    elif if_restart == 1 and '轻松旷工' in miner_software:
        send_email.send_email("operation fail", "can not restart miner on qskg", 1, 3)

    os.chdir(FILE_PATH)
    if '轻松旷工' not in miner_software:
        with open(start_file_path, 'w') as w:
            if 't-rex' in miner_software:
                w.write(miner_software + ' -a ethash -o ' + CONFIG_DICT['pool'] + ' -u ' + CONFIG_DICT['wallet'] + ' -p x -w ' + str(send_email.get_machine()) + ' ' + CONFIG_DICT['overclock_info'] + '\n' + 'pause')
            elif 'nbminer' in miner_software:
                w.write(miner_software + ' -a ethash -o ' + CONFIG_DICT['pool'] + ' -u ' + CONFIG_DICT['wallet'] + '.' + str(send_email.get_machine()) + ' ' + CONFIG_DICT['overclock_info'] + '\n' + 'pause')
        os.startfile(start_file_path + '-copy.lnk')
    else:
        os.startfile(start_file_path + '-copy.lnk')
