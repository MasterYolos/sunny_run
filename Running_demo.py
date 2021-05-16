import requests
import json
import time
import hashlib
import random
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
msg_from = 'xxxx@qq.com'  # 发送方邮箱
passwd = 'xxxxxxxx'       # 就是邮箱的授权码
to = ['xxxxxxx@qq.com']   # 接受方邮箱

#发送IMEI过期信息
def Send_Imei_Wrong():
    msg = MIMEMultipart()
    conntent = "少爷,IMEI过期了！！！！"
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    msg['Subject'] = "少爷,IMEI过期了！！！！"
    msg['From'] = msg_from
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, to, msg.as_string())
#发送跑步成功信息
def Send_succes_run():
    msg = MIMEMultipart()
    conntent = "少爷,今天早上跑完啦！！！！"
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    msg['Subject'] = "少爷,今天早上跑完啦！！！！"
    msg['From'] = msg_from
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, to, msg.as_string())
#发送IMEI过期信息
def Send_fail_run():
    msg = MIMEMultipart()
    conntent = "少爷,没跑完，出问题啦！！！！"
    msg.attach(MIMEText(conntent, 'plain', 'utf-8'))
    msg['Subject'] = "少爷,没跑完，出问题啦！！！！"
    msg['From'] = msg_from
    s = smtplib.SMTP_SSL("smtp.qq.com", 465)
    s.login(msg_from, passwd)
    s.sendmail(msg_from, to, msg.as_string())

# Generate table Randomly
alphabet = list('abcdefghijklmnopqrstuvwxyz')
random.shuffle(alphabet)
table = ''.join(alphabet)[:10]

def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()

def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    # print(result)
    return result

def Run(IMEI='xxxxxxxxxx'):#你的IMEI码
    if IMEI is None:
        # Input to IMEI
        if(len(sys.argv) > 1):
            IMEI = sys.argv[1]
        else:
            IMEI = str(input("Please Input Your IMEI Arg:"))
        if(len(IMEI) != 32):
            exit("IMEI Format Error!")

        if (len(sys.argv) > 2 and sys.argv[2].upper() == 'Y'):
            pass
        else:
            print("Your IMEI Code:", IMEI)
            Sure = str(input("Sure?(Y/N)"))
            if(Sure == 'Y' or Sure == 'y'):
                pass
            else:
                exit("User Aborted.")

    API_ROOT = 'http://client3.aipao.me/api'  # client3 for Android
    Version = '2.14'

    # Login
    headers1 = {'version': '2.40', 'Host': 'client3.aipao.me', 'Connection': 'Keep-Alive'}
    TokenRes = requests.get(
        API_ROOT + '/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode=' + IMEI,headers=headers1)
    TokenJson = json.loads(TokenRes.content.decode('utf8', 'ignore'))
    # headers
    state = TokenJson['Success']
    if state == False:
        print('IMEI过期了')
        Send_Imei_Wrong()
        exit("User Aborted.")
    else:
        print('登录成功')
    token = TokenJson['Data']['Token']
    userId = str(TokenJson['Data']['UserId'])
    timespan = str(time.time()).replace('.', '')[:13]
    auth = 'B' + MD5(MD5(IMEI)) + ':;' + token
    nonce = str(random.randint(100000, 10000000))
    sign = MD5(token + nonce + timespan + userId).upper()  # sign为大写

    header = {'nonce': nonce, 'timespan': timespan,
              'sign': sign, 'version': Version, 'Accept': None, 'User-Agent': None, 'Accept-Encoding': None, 'Connection': 'Keep-Alive'}

    # Get User Info

    GSurl = API_ROOT + '/' + token + '/QM_Users/GS'
    GSres = requests.get(GSurl, headers=header, data={})
    GSjson = json.loads(GSres.content.decode('utf8', 'ignore'))

    Lengths = GSjson['Data']['SchoolRun']['Lengths']

    print('User Info:',GSjson['Data']['User']['UserID'],GSjson['Data']['User']['NickName'],GSjson['Data']['User']['UserName'],GSjson['Data']['User']['Sex'])
    print('Running Info:',GSjson['Data']['SchoolRun']['Sex'],GSjson['Data']['SchoolRun']['SchoolId'],GSjson['Data']['SchoolRun']['SchoolName'],GSjson['Data']['SchoolRun']['MinSpeed'],
        GSjson['Data']['SchoolRun']['MaxSpeed'],GSjson['Data']['SchoolRun']['Lengths'])

    # Start Running
    SRSurl = API_ROOT + '/' + token + \
        '/QM_Runs/SRS?S1=30.534736&S2=114.367788&S3=' + str(Lengths)
    SRSres = requests.get(SRSurl, headers=header, data={})
    SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))

    # Generate Runnig Data Randomly
    RunTime = str(random.randint(720, 1000))  # seconds
    RunDist = str(Lengths + random.randint(0, 3))  # meters
    RunStep = str(random.randint(1300, 1600))  # steps

    # Running Sleep
    StartT = time.time()
    for i in range(int(RunTime)):
        time.sleep(1)
        print("Current Minutes: %d Running Progress: %.2f%%\r" %
              (i / 60, i * 100.0 / int(RunTime)), end='')
    print("")
    print("Running Seconds:", time.time() - StartT)

    # print(SRSurl)
    # print(SRSjson)

    RunId = SRSjson['Data']['RunId']

    # End Running
    EndUrl = API_ROOT + '/' + token + '/QM_Runs/ES?S1=' + RunId + '&S4=' + \
        encrypt(RunTime) + '&S5=' + encrypt(RunDist) + \
        '&S6=&S7=1&S8=' + table + '&S9=' + encrypt(RunStep)

    EndRes = requests.get(EndUrl, headers=header)
    EndJson = json.loads(EndRes.content.decode('utf8', 'ignore'))

    print("-----------------------")
    print("Time:", RunTime)
    print("Distance:", RunDist)
    print("Steps:", RunStep)
    print("-----------------------")

    if(EndJson['Success']):
        Send_succes_run()
        print("[+]OK:", EndJson['Data'])
    else:
        Send_fail_run()
        print("[!]Fail:", EndJson['Data'])
def main():
    Run()
if __name__ == '__main__':
    main()
