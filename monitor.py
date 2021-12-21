# encoding: utf-8
import time
from datetime import datetime
import os
import sys
from send_email import send_email
from send_email import get_machine
import download_config_apply

def read_nbminer_data(file_path, gap_time, urgent, num_of_gpu, limint_hashrate):
    gpu_name = '3060'
    accepted_num = [0] * num_of_gpu
    temp_list = [0] * num_of_gpu
    local_hashrate_list = [0] * num_of_gpu
    pool_hashrate_list = [0] * num_of_gpu
    reject_num = [0] * num_of_gpu
    count_list = [0] * num_of_gpu

    internet_break_time = 0
    disconnect_time = ''
    connect_time = ''

    last_avg_hash = 0
    last_pool_hash = 0
    total_run_time = 0
    last_sign_list = [1] * 3
    total_submit = 0

    hang_on_monitor_list = []
    hang_on_monitor = 0

    with open(file_path, 'r', encoding='UTF-8') as f:
        text = f.read().split('\n')
        text.reverse()
        for line in text:
            if 'Team Red Miner version 0.8.4' in line or line == '' or line[:5] == 'ERROR':
                continue
            if 'Summary ' in line and (datetime.now() - datetime.strptime(line.split("Summary ")[1].strip("=").strip(' '), '%Y-%m-%d %H:%M:%S')).total_seconds() > gap_time:
                break
            if 'Share accepted' in line:
                found_gpu = int(line.split('DEVICE ')[1][0])
                accepted_num[found_gpu] += 1
            if 'Share rejected' in line:
                found_gpu = int(line.split('DEVICE ')[1][0])
                reject_num[found_gpu] += 1
            if gpu_name in line and '|' in line and 'USER:' not in line and 'NVIDIA GeForce RTX' not in line and 'Total' not in line and 'accepted' not in line:
                try:
                    gpu_num = int(line.replace(' ','').split('|')[1])
                except:
                    print (line)
                temp_list[gpu_num] += int(line.replace(' ','').split('|')[8])
                if int(line.replace(' ','').split('|')[8]) >= 65 and urgent == 1:
                        send_email("温度较高", ', 显卡%s温度%s度' % (gpu_num, int(line.replace(' ','').split('|')[8])), 0, 3)
                        break
                if int(line.split('|')[5].strip(' ')) > 999 and urgent == 1:
                    send_email(" 无效", "存在无效，停止监控", 0, 3)
                    #os.system("shutdown -r")
                    sys.exit(-1)

                local_hashrate_list[gpu_num] += float(line.replace(' ','').split('|')[3].strip('M'))
                #if hang_on_monitor == 1:
                    #hang_on_monitor_list.append(float(line[line.index('ethash')+8:line.index('ethash')+13]))
                #pool_hashrate_list[gpu_num] += float(line[line.index('pool')+5:line.index('pool')+10])
                count_list[gpu_num] += 1

            if 'Login succeeded' in line:
                connect_time = datetime.strptime(line[1:9], '%H:%M:%S')
            if 'Connection refused' in line:
                disconnect_time = datetime.strptime(line[1:9], '%H:%M:%S')
                if connect_time != '':
                    print(disconnect_time,connect_time,(connect_time - disconnect_time).seconds)
                    internet_break_time += (connect_time - disconnect_time).seconds
                    disconnect_time = ''
                    connect_time = ''

            if last_sign_list[0] == 1 and last_sign_list[1] == 1 and 'Total' in line and 'Uptime:' in line:
                #last_avg_hash = float(line[line.index('avg')+4:line.index('avg')+9])
                #last_pool_hash = float(line[line.index('pool ')+5:line.index('pool ')+10])
                total_submit = int(line.split("|")[2].strip(' '))
                last_sign_list[0] = 0
                last_sign_list[1] = 0

            if last_sign_list[2] == 1 and 'Uptime:' in line:
                days = int(line.split("|")[6].split('D')[0].replace(' ','').split(':')[1])
                hours = int(line.split("|")[6].split('D')[1].split('CPU')[0].strip(' ').split(':')[0])
                mins = int(line.split("|")[6].split('D')[1].split('CPU')[0].strip(' ').split(':')[1])
                total_run_time = days * 24 + hours + round(mins / 60, 1)
                last_sign_list[2] = 0

            '''
            if 'Total' in line:
                hang_on_monitor = 1
            if len(hang_on_monitor_list) == 6 and urgent == 1:
                if hang_on_monitor_list.count(0) == 1:
                    hang_on_monitor_list.reverse()
                    gpu_num = hang_on_monitor_list.index(0)
                    send_email("gpu挂起，电脑重启", machine + " gpu%s挂起，电脑重启"%gpu_num)
                    os.system("shutdown -r")
                    sys.exit(-1)
                    hang_on_monitor = 0
                    hang_on_monitor_list = []
                else:
                    hang_on_monitor = 0
                    hang_on_monitor_list = []
            '''



    if disconnect_time == '' and connect_time != '':
        print ((gap_time - (datetime.now() - connect_time).seconds))
        if total_run_time >= 2:
            internet_break_time += (gap_time - (datetime.now() - connect_time).seconds)
    if disconnect_time != '' and connect_time == '':
        print ((datetime.now() - disconnect_time).seconds)
        internet_break_time += (datetime.now() - disconnect_time).seconds
    internet_break_time = '%.1f' % (internet_break_time / 60)


    if count_list[0] == 0:
        return "no data"
    if urgent == 1:
        if sum(local_hashrate_list)/count_list[0] < limint_hashrate:
            send_email("机器算力异常", ' 平均算力: %s' % (sum(local_hashrate_list)/count_list[0]) + '<br/>' + '最低算力卡: %s, 算力: %s' % (local_hashrate_list.index(min(local_hashrate_list)), min(local_hashrate_list)/count_list[0]), 0, 3)

    res_str = '提交：%s ， 拒绝：%s ， 本地平均算力：%s ， 池平均算力：%s ， 网络断开时间：%s分钟 <br/><br/> ' % (sum(accepted_num), sum(reject_num), '%.1f' % (sum(local_hashrate_list)/count_list[0]), '%.1f' % (sum(pool_hashrate_list)/count_list[0]), internet_break_time)
    for i in range(len(accepted_num)):
        res_str = res_str + 'GPU%s: 提交：%s, 拒绝：%s, 平均温度：%s, ' \
                                '平均算力：%s' % (str(i),accepted_num[i],reject_num[i],'%.1f' % (temp_list[i]/count_list[0]),
                                                      '%.1f' % (local_hashrate_list[i]/count_list[0])) + '<br/>'
    # 标准提交个数：48.9Mh 每分钟提交一个
    res_str += "<br/>总开机时间：%s小时, 总提交：%s, 实际算力：%s" % (total_run_time,total_submit,'%.1f' % (8 * 48.9 * total_submit / (total_run_time * 60)))
    return res_str



def read_trexminer_data(file_path, gap_time, urgent, count_algo, drop_algo, num_of_gpu, limint_hashrate):
    accepted_num = [0] * num_of_gpu
    temp_list = [0] * num_of_gpu
    mem_temp_list = [0] * num_of_gpu
    local_hashrate_list = [0] * num_of_gpu
    pool_hashrate_list = [0] * num_of_gpu
    reject_num = [0] * num_of_gpu
    count_list = [0]*num_of_gpu

    internet_break_time = 0
    disconnect_time = ''
    connect_time = ''

    last_avg_hash = 0
    last_pool_hash = 0
    total_run_time = 0
    last_sign_list = [1] * 3
    restart_num = 0
    algo_swich = 0

    hang_on_monitor_list = []
    hang_on_monitor = 0

    with open(file_path, 'r', encoding='UTF-8') as f:
        text = f.read().split('\n')
        text.reverse()
        for line in text:
            if 'Algo: ' + count_algo in line:
                algo_swich = 1
            if 'Algo: ' + drop_algo in line:
                algo_swich = 0
            if 'T-Rex NVIDIA GPU miner' in line or line == '' or '-----' in line:
                continue
            try:
                if (datetime.now() - datetime.strptime(line[:17], '%Y%m%d %H:%M:%S')).total_seconds() > gap_time:
                    break
            except:
                pass
            if '[ OK ]' in line:
                found_gpu = int(line.split('#')[1])
                accepted_num[found_gpu] += 1
            if 'Share rejected' in line:
                found_gpu = int(line[line.index('DEVICE') + 7])
                reject_num[found_gpu] += 1
            if algo_swich == 1 and ('RTX 3060' in line or '3080 Ti' in line) and 'GPU' in line and 'LHR' in line:

                try:
                    gpu_num = int(line.split('#')[1][0])
                except:
                    print (line)
                temp_list[gpu_num] += int(line.split('T:')[1][:2])
                if line.split('T:')[1][2] == '/':
                    mem_temp_list[gpu_num] += int(line.split('T:')[1][3:5])
                if int(line.split('T:')[1][:2]) >= 65 and urgent == 1:
                        send_email("温度较高", ', 显卡%s温度%s度' % (gpu_num, int(line.split('T:')[1][:2])), 0, 3)
                        break
                if line.split('T:')[1][2] == '/' and int(line.split('T:')[1][3:5]) >= 105 and urgent == 1:
                        send_email("显存温度较高", ', 显卡%s显存温度%s度' % (gpu_num, int(line.split('T:')[1][3:5])), 0, 3)
                        if line.split('T:')[1][2] == '/' and int(line.split('T:')[1][3:5]) >= 110 and urgent == 1:
                            send_email("显存温度较高，自动关机", ', 显卡%s显存温度%s度' % (gpu_num, int(line.split('T:')[1][3:5])), 0, 3)
                            os.system("shutdown -s -t 5")
                            break
                        break
                #if int(line.split('|')[5].strip(' ')) > 999 and urgent == 1:
                #    send_email(machine + " 无效", "存在无效，停止监控")
                #    #os.system("shutdown -r")
                #    sys.exit(-1)
                try:
                    local_hashrate_list[gpu_num] += float(line.split(' MH/s')[0][-5:])
                except:
                    print (line)
                #if hang_on_monitor == 1:
                    #hang_on_monitor_list.append(float(line[line.index('ethash')+8:line.index('ethash')+13]))
                #pool_hashrate_list[gpu_num] += float(line[line.index('pool')+5:line.index('pool')+10])
                count_list[gpu_num] += 1

            if 'Login succeeded' in line:
                connect_time = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
            if 'Connection refused' in line:
                disconnect_time = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
                if connect_time != '':
                    print(disconnect_time,connect_time,(connect_time - disconnect_time).seconds)
                    internet_break_time += (connect_time - disconnect_time).seconds
                    disconnect_time = ''
                    connect_time = ''

            if last_sign_list[0] == 1 and last_sign_list[1] == 1 and 'WD' in line and 'restarts' in line:
                #last_avg_hash = float(line[line.index('avg')+4:line.index('avg')+9])
                #last_pool_hash = float(line[line.index('pool ')+5:line.index('pool ')+10])
                restart_num = int(line.split('restarts ')[-1])
                last_sign_list[0] = 0
                last_sign_list[1] = 0


            if last_sign_list[2] == 1 and 'Uptime: ' in line:
                #days = int(line.split("|")[6].split('D')[0].replace(' ','').split(':')[1])
                #hours = int(line.split("|")[6].split('D')[1].split('CPU')[0].strip(' ').split(':')[0])
                #mins = int(line.split('Uptime: ')[1].split(' min')[0])
                mins = 60
                total_run_time = round(mins / 60, 1)
                last_sign_list[2] = 0

            '''
            if 'Total' in line:
                hang_on_monitor = 1
            if len(hang_on_monitor_list) == 6 and urgent == 1:
                if hang_on_monitor_list.count(0) == 1:
                    hang_on_monitor_list.reverse()
                    gpu_num = hang_on_monitor_list.index(0)
                    send_email("gpu挂起，电脑重启", machine + " gpu%s挂起，电脑重启"%gpu_num)
                    os.system("shutdown -r")
                    sys.exit(-1)
                    hang_on_monitor = 0
                    hang_on_monitor_list = []
                else:
                    hang_on_monitor = 0
                    hang_on_monitor_list = []
            '''



    if disconnect_time == '' and connect_time != '':
        print ((gap_time - (datetime.now() - connect_time).seconds))
        if total_run_time >= 2:
            internet_break_time += (gap_time - (datetime.now() - connect_time).seconds)
    if disconnect_time != '' and connect_time == '':
        print ((datetime.now() - disconnect_time).seconds)
        internet_break_time += (datetime.now() - disconnect_time).seconds
    internet_break_time = '%.1f' % (internet_break_time / 60)


    if count_list[0] == 0:
        return "no data"
    if urgent == 1:
        if sum(local_hashrate_list)/count_list[0] < limint_hashrate:
            send_email("机器算力异常", ' 平均算力: %s' % (sum(local_hashrate_list)/count_list[0]) + '<br/>' + '最低算力卡: %s, 算力: %s' % (local_hashrate_list.index(min(local_hashrate_list)), min(local_hashrate_list)/count_list[0]), 0, 3)

    res_str = '提交：%s ， 拒绝：%s ， 本地平均算力：%s ， 池平均算力：%s ， 网络断开时间：%s分钟 <br/><br/> ' % (sum(accepted_num), sum(reject_num), '%.1f' % (sum(local_hashrate_list)/count_list[0]), '%.1f' % (sum(pool_hashrate_list)/count_list[0]), internet_break_time)
    for i in range(len(accepted_num)):
        res_str = res_str + 'GPU%s: 提交：%s, 拒绝：%s, 温度：%s, 显存温度：%s, ' \
                                '算力：%s' % (str(i),accepted_num[i],reject_num[i],'%.1f' % (temp_list[i]/count_list[0]),'%.1f' % (mem_temp_list[i]/count_list[0]),
                                                      '%.1f' % (local_hashrate_list[i]/count_list[0])) + '<br/>'
    # 标准提交个数：48.9Mh 每分钟提交一个
    if count_algo == 'ethash':
        res_str = res_str + '<br/><br/>' + read_trexminer_data(file_path, gap_time, urgent, drop_algo, count_algo, num_of_gpu, limint_hashrate)
    else:
        res_str += "<br/>总开机时间：%s小时, 内核重启次数：%s," % (total_run_time,restart_num)
    return res_str




def read_teamredminer_data(line_list, gap_time, urgent, num_of_gpu, limint_hashrate):
    accepted_num = [0] * num_of_gpu
    temp_list = [0] * num_of_gpu
    local_hashrate_list = [0] * num_of_gpu
    pool_hashrate_list = [0] * num_of_gpu
    reject_num = [0] * num_of_gpu
    count_list = [0] * num_of_gpu

    internet_break_time = 0
    disconnect_time = ''
    connect_time = ''

    last_avg_hash = 0
    last_pool_hash = 0
    total_run_time = 0
    last_sign_list = [1] * 3

    hang_on_monitor_list = []
    hang_on_monitor = 0

    for line in line_list:
        if 'Team Red Miner version 0.8.' in line or line == '':
            continue
        if (datetime.now() - datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')).total_seconds() > gap_time:
            break
        if 'share accepted' in line:
            found_gpu = int(line[line.index('GPU') + 3])
            accepted_num[found_gpu] += 1
        if 'share rejected' in line:
            found_gpu = int(line[line.index('GPU') + 3])
            reject_num[found_gpu] += 1
        if 'GPU' in line and 'ethash: ' in line:
            gpu_num = int(line[line.index('GPU') + 4])
            temp_list[gpu_num] += int(line.split(',')[0][-3:][:2])
            if int(line.split(',')[0][-3:][:2]) >= 63 and urgent == 1:
                send_email("温度较高", ', 显卡%s温度%s度' % (gpu_num, int(line.split(',')[0][-3:][:2])), 0, 3)
                break
            if int(line.split('hw:')[1]) > 50 and urgent == 1:
                send_email(" 重启", "存在无效，重启电脑", 0, 3)
                os.system("shutdown -r")
                sys.exit(-1)
            local_hashrate_list[gpu_num] += float(line[line.index('ethash') + 8:line.index('ethash') + 13])
            if hang_on_monitor == 1:
                hang_on_monitor_list.append(float(line[line.index('ethash') + 8:line.index('ethash') + 13]))
            pool_hashrate_list[gpu_num] += float(line[line.index('pool') + 5:line.index('pool') + 10])
            count_list[gpu_num] += 1

        if 'login succeeded' in line:
            connect_time = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
        if 'connection was closed due to an error' in line:
            disconnect_time = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
            if connect_time != '':
                print(disconnect_time, connect_time, (connect_time - disconnect_time).seconds)
                internet_break_time += (connect_time - disconnect_time).seconds
                disconnect_time = ''
                connect_time = ''

        if last_sign_list[0] == 1 and last_sign_list[1] == 1 and 'Total' in line and 'ethash' in line:
            last_avg_hash = float(line[line.index('avg') + 4:line.index('avg') + 9])
            last_pool_hash = float(line[line.index('pool ') + 5:line.index('pool ') + 10])
            last_sign_list[0] = 0
            last_sign_list[1] = 0
        if last_sign_list[2] == 1 and 'Stats Uptime' in line:
            days = int(line.split('Stats Uptime: ')[1].split(', ')[0].split(' ')[0])
            hours = int(line.split('Stats Uptime: ')[1].split(', ')[1].split(':')[0])
            mins = int(line.split('Stats Uptime: ')[1].split(', ')[1].split(':')[1])
            total_run_time = days * 24 + hours + round(mins / 60, 1)
            last_sign_list[2] = 0

        if 'Total' in line:
            hang_on_monitor = 1
        if len(hang_on_monitor_list) == 6 and urgent == 1:
            if hang_on_monitor_list.count(0) == 1:
                hang_on_monitor_list.reverse()
                gpu_num = hang_on_monitor_list.index(0)
                send_email("gpu挂起，电脑重启", " gpu%s挂起，电脑重启" % gpu_num, 0, 3)
                os.system("shutdown -r")
                sys.exit(-1)
                hang_on_monitor = 0
                hang_on_monitor_list = []
            else:
                hang_on_monitor = 0
                hang_on_monitor_list = []

    if disconnect_time == '' and connect_time != '':
        print((gap_time - (datetime.now() - connect_time).seconds))
        if total_run_time >= 2:
            internet_break_time += (gap_time - (datetime.now() - connect_time).seconds)
    if disconnect_time != '' and connect_time == '':
        print((datetime.now() - disconnect_time).seconds)
        internet_break_time += (datetime.now() - disconnect_time).seconds
    internet_break_time = '%.1f' % (internet_break_time / 60)

    if count_list[0] == 0:
        return "no data"
    if urgent == 1:
        if sum(local_hashrate_list) / count_list[0] < limint_hashrate:
            send_email("机器算力异常", ' 平均算力: %s' % (
                        sum(local_hashrate_list) / count_list[0]) + '<br/>' + '最低算力卡: %s, 算力: %s' % (
                       local_hashrate_list.index(min(local_hashrate_list)), min(local_hashrate_list) / count_list[0]), 0, 3)

    res_str = '提交：%s ， 拒绝：%s ， 本地平均算力：%s ， 池平均算力：%s ， 网络断开时间：%s分钟 <br/><br/> ' % (
    sum(accepted_num), sum(reject_num), '%.1f' % (sum(local_hashrate_list) / count_list[0]),
    '%.1f' % (sum(pool_hashrate_list) / count_list[0]), internet_break_time)
    for i in range(len(accepted_num)):
        res_str = res_str + 'GPU%s: 提交：%s, 拒绝：%s, 平均温度：%s, ' \
                            '平均算力：%s' % (
                  str(i), accepted_num[i], reject_num[i], '%.1f' % (temp_list[i] / count_list[0]),
                  '%.1f' % (local_hashrate_list[i] / count_list[0])) + '<br/>'

    res_str += "<br/>总开机时间：%s小时, 总平均算力：%s, 总池算力：%s, 算力损失：%s" % (
    total_run_time, last_avg_hash, last_pool_hash, '%.1f%%' % (100 * (last_pool_hash - last_avg_hash) / last_avg_hash))
    return res_str


def read_lines(file_path, read_lines):
    read_list = []
    f = open(file_path, 'rb')
    try:
        f.seek(-(read_lines * 120), 2)
    except:
        print("log's line not enough")
    line = f.readlines()[1:]
    for i in line:
        read_list.append(str(i, encoding='utf-8').strip('\r\n'))
    f.close()
    read_list.reverse()
    return read_list


def get_current_log(config_dict):
    miner_software, start_file, num_of_gpu, limint_hashrate = config_dict['miner_info'].split(',')
    log_file = config_dict['log'] + max(os.listdir(config_dict['log'])) if 't-rex' not in miner_software else config_dict['log'] + 'trex_log.txt'
    with open(log_file, 'r') as f:
        return ('\n'.join(f.read().split('\n')[-50:]))


def stop_monitor():
    CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
    CONFIG_DICT = download_config_apply.get_config_data(CONFIG_PATH)
    with open(CONFIG_DICT['log'] + 'if_stop_monitor.txt', 'w') as f:
        f.write("1")

if __name__ == '__main__':
    CONFIG_PATH = 'C:/github/windows_control_miner-main/config.txt'
    CONFIG_DICT = download_config_apply.get_config_data(CONFIG_PATH)
    urgent_statistics_count = 0

    # file_path = log_path + max(os.listdir(log_path))
    # line_list = read_lines(file_path,150000)
    # send_email(machine + "每4小时报告", read_data(line_list, 14400, 0), 1, 3)
    # sys.exit(-1)

    miner_software, start_file, num_of_gpu, limint_hashrate = CONFIG_DICT['miner_info'].split(',')
    num_of_gpu = int(num_of_gpu.strip("gpu_num"))
    limint_hashrate = int(limint_hashrate.strip("gpu_hr"))
    log_path = CONFIG_DICT['log']
    machine = get_machine()

    with open(log_path + 'if_stop_monitor.txt','w') as f:
        f.write("0")


    def start_teamredminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate):
        def get_if_stop():
            with open(log_path + 'if_stop_monitor.txt','r') as f:
                return f.read() == "0"
        while get_if_stop():
            file_path = log_path + "log.txt"
            if datetime.now().strftime('%H:%M:%S')[:5] == '23:00':
                line_list = read_lines(file_path, 150000)
                send_email("每二十四小时报告", read_teamredminer_data(line_list, 86400, 0, num_of_gpu, limint_hashrate), 0, 3)
            if datetime.now().strftime('%H:%M:%S')[3:5] == '00' and int(datetime.now().strftime('%H:%M:%S')[:2]) % 4 == 0:
                line_list = read_lines(file_path, 25000)
                result_str = read_teamredminer_data(line_list, 14400, 0, num_of_gpu, limint_hashrate)
                send_email("每4小时报告", result_str, 0, 3)
            if urgent_statistics_count >= 3600:
                line_list = read_lines(file_path, 10000)
                result_str = read_teamredminer_data(line_list, urgent_statistics_count, 1, num_of_gpu, limint_hashrate)
                urgent_statistics_count = 0

            time.sleep(60)
            urgent_statistics_count += 60
        if get_if_stop() == False:
            print ("stop monitor done")
            # send_email("stop monitor done", "stop monitor done", 1, 3)


    def start_trexminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate):
        def get_if_stop():
            with open(log_path + 'if_stop_monitor.txt', 'r') as f:
                return f.read() == "0"

        while get_if_stop():
            file_path = log_path + 'trex_log.txt'
            
            # send_email("每二十四小时报告", read_trexminer_data(file_path, 86400, 0, 'ethash', 'kawpow', num_of_gpu, limint_hashrate), 0, 3)
            
            if datetime.now().strftime('%H:%M:%S')[:5] == '23:00':
                send_email("每二十四小时报告", read_trexminer_data(file_path, 86400, 0, 'ethash', 'kawpow', num_of_gpu, limint_hashrate), 0, 3)
            if datetime.now().strftime('%H:%M:%S')[3:5] == '00' and int(
                    datetime.now().strftime('%H:%M:%S')[:2]) % 4 == 0:
                result_str = read_trexminer_data(file_path, 14400, 0, 'ethash', 'kawpow', num_of_gpu, limint_hashrate)
                send_email("每4小时报告", result_str, 0, 3)
            if urgent_statistics_count >= 3600:
                result_str = read_trexminer_data(file_path, urgent_statistics_count, 1, 'ethash', 'kawpow', num_of_gpu, limint_hashrate)
                urgent_statistics_count = 0

            time.sleep(60)
            urgent_statistics_count += 60
        if get_if_stop() == False:
            print ("stop monitor done")
            # send_email("stop monitor done", "stop monitor done", 1, 3)



    def start_nbminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate):
        def get_if_stop():
            with open(log_path + 'if_stop_monitor.txt', 'r') as f:
                return f.read() == "0"

        while get_if_stop():
            file_path = log_path + max(os.listdir(log_path))
            if datetime.now().strftime('%H:%M:%S')[:5] == '23:00':
                send_email("每二十四小时报告",read_nbminer_data(file_path, 86400, 0, num_of_gpu, limint_hashrate), 0,3)
            if datetime.now().strftime('%H:%M:%S')[3:5] == '00' and int(datetime.now().strftime('%H:%M:%S')[:2]) % 4 == 0:
                result_str = read_nbminer_data(file_path, 14400, 0, num_of_gpu, limint_hashrate)
                send_email("每4小时报告", result_str, 0, 3)
            if urgent_statistics_count >= 3600:
                result_str = read_nbminer_data(file_path, urgent_statistics_count, 1, num_of_gpu,limint_hashrate)
                urgent_statistics_count = 0

            time.sleep(60)
            urgent_statistics_count += 60
        if get_if_stop() == False:
            print ("stop monitor done")
            # send_email("stop monitor done", "stop monitor done", 1, 3)


    try:
        if 't-rex' in miner_software:
            start_trexminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate)
        elif 'nbminer' in miner_software:
            start_nbminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate)
            print ("monitor start")
        elif 'teamredminer' in miner_software:
            start_teamredminer_monitor(urgent_statistics_count, log_path, num_of_gpu, limint_hashrate)
            print ("monitor start")
    except Exception as err:
        send_email("monitor crash", err, 1, 3)
        
        
