import time
import os
import datetime
import send_email

FILE_PATH = 'C:/github/'

def start_mining(if_restart, CONFIG_DICT):
    print ("start mining")
    miner_software, start_file_path = CONFIG_DICT['miner_info'].split(',')[:2]

    os.chdir(FILE_PATH)
    if 'qskg' not in miner_software:
        with open(start_file_path, 'w') as w:
            if 't-rex' in miner_software:
                w.write(miner_software + ' -a ethash -o ' + CONFIG_DICT['pool'] + ' -u ' + CONFIG_DICT['wallet'] + ' -p x -w ' + str(send_email.get_machine()) + ' ' + CONFIG_DICT['overclock_info'] + '\n' + 'pause')
            elif 'nbminer' in miner_software:
                w.write(miner_software + ' -a ethash -o ' + CONFIG_DICT['pool'] + ' -u ' + CONFIG_DICT['wallet'] + '.' + str(send_email.get_machine()) + ' ' + CONFIG_DICT['overclock_info'] + '\n' + 'pause')
            elif 'teamredminer' in miner_software:
                w.write("set GPU_MAX_ALLOC_PERCENT=100\nset GPU_SINGLE_ALLOC_PERCENT=100\nset GPU_MAX_HEAP_SIZE=100\nset GPU_USE_SYNC_OBJECTS=1\n" + miner_software + ' -a ethash -o ' + CONFIG_DICT['pool'] + ' -u ' + CONFIG_DICT['wallet'] + '.' + str(send_email.get_machine()) + ' ' + CONFIG_DICT['overclock_info'] + ' -p x'
        os.startfile(start_file_path + '-copy.lnk')
    else:
        os.startfile(start_file_path + '-copy.lnk')
