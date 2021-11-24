import sys
import time
import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders

RECEIVERS_copy = ['604638487@qq.com','3567741421@qq.com','3080002996@qq.com']
RECEIVERS_self = ['604638487@qq.com']

def get_machine():
    pass

def send_email(title, content, send_self, retry_times):
    receiver_list = RECEIVERS_self if send_self else RECEIVERS_copy
    machine = get_machine()
    mail_host = "smtp.qq.com"
    mail_user = "604638487"
    mail_pass = "tcoyxslsopdmbbdb"
    MAIL_POSTFIX = "qq.com"
    sender = '604638487@qq.com'
    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = Header(machine + title,"utf-8")
    message['To'] = ";".join(receiver_list)
    message['From'] = '604638487@qq.com'
    try:
        server = smtplib.SMTP(port=465)
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(sender, receiver_list, message.as_string())
        server.close()
        print("send email secceed")
        return True
    except Exception as err:
        print (err)
        time.sleep(60)
        if retry_times > 0:
            send_email(title, content, receiver_list, retry_times-1)
