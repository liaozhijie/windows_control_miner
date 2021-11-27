import requests
import time
import datetime

if __name__ == '__main__':
    link = "https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe"
    t3 = 0
    while True:
        t1, t2 = 0, 0
        try:
            t1=datetime.datetime.now()
            r = requests.get(link)
            t2=datetime.datetime.now()
            t3=(t1-t2).total_seconds()
            print ('succees')
        except:
            print ('fail')
        print ("cost time:",t3)
        if t3 < 1800:
            time.sleep(1200 - t3)
