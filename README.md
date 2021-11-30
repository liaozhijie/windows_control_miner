# windows_control_miner
visit Github issue : https://www.cnblogs.com/golinuxstudy/p/15605476.html  (or https://github.com/dotnetcore/fastgithub/releases)



# usage (trexminer for example)

1.mkdir: C:/github, C:/github/cp_github, C:/miner_log

2.download windows_control_miner.zip, tar to : C:/github/

3.download miner to : C:/github/trexminer

4.create lnk from miner.bat(rename as "miner.bat-copy"), and let it starts by adminitrator

5.create file "miner_number.txt" on C:/github, write machine name on it.(contact config.txt)

6.pip install: requests, psutil

7.copy base_control.py and fake_download.py to auto_start path.


# attention

1.Can not add above 1 order opreation on config.txt

2.Do not update download_config_apply.py and other file at the same time, cause download_config_apply.py would not effect when first download, but others would effect.

3.If change config.txt, need to restart_monitor.
