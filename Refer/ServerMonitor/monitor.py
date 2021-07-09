from apscheduler.schedulers.blocking import BlockingScheduler
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formatdate
import time
import smtplib
import sys
import psutil

memoryThreshold = 1024;  # 内存报警阈值，单位M，如果需要GB请使用8*1024这种格式
cpuThreshold = 70  # CPU使用率报警阈值，单位百分百

minutes = 0;  # 检查间隔/分钟
seconds = 1;  # 检查间隔/秒

smtpHost = ""
smtpPort = 465;
smtpWithSSL = True;
username = "";
password = "";

fromMail = username;
toMail = "";

# end definitions

lastOverThreshold = False;


# Python获取计算机内存硬盘CPU信息  部分代码参考
# https://blog.csdn.net/zhangnr/article/details/83651282

def GetTime():
    return time.strftime("%Y-%m-%d %H-%M", time.localtime())


def GetDiskInfo():
    list = psutil.disk_partitions()  # 磁盘列表
    ilen = len(list)  # 磁盘分区个数
    i = 0
    retlist1 = []
    retlist2 = []
    while i < ilen:
        diskinfo = psutil.disk_usage(list[i].device)
        total_disk = round((float(diskinfo.total) / 1024 / 1024 / 1024), 2)  # 总大小
        used_disk = round((float(diskinfo.used) / 1024 / 1024 / 1024), 2)  # 已用大小
        free_disk = round((float(diskinfo.free) / 1024 / 1024 / 1024), 2)  # 剩余大小
        syl_disk = diskinfo.percent

        retlist1 = [i, list[i].device, total_disk, used_disk, free_disk, syl_disk]  # 序号，磁盘名称，
        retlist2.append(retlist1)
        i = i + 1
    return retlist2


def GetCpuInfo():
    # cpu_count = psutil.cpu_count(logical=False)  #1代表单核CPU，2代表双核CPU
    # xc_count = psutil.cpu_count()                #线程数，如双核四线程
    cpu_slv = (psutil.cpu_percent(1, True))  # cpu使用率
    list = cpu_slv
    return list


def GetMemoryInfo():
    memory = psutil.virtual_memory()
    total_nc = round((float(memory.total) / 1024 / 1024), 2)  # 总内存
    used_nc = round((float(memory.used) / 1024 / 1024), 2)  # 已用内存
    free_nc = round((float(memory.free) / 1024 / 1024), 2)  # 空闲内存
    syl_nc = round((float(memory.used) / float(memory.total) * 100), 2)  # 内存使用率

    ret_list = [total_nc, used_nc, free_nc, syl_nc]
    return ret_list


def SendAMail(memInfo):
    cpuInfo = "";
    i = 0;
    for cpu in GetCpuInfo():
        cpuInfo += f"[{i}]   {cpu}%\n";
        i += 1;

    disksInfo = "";
    for disk in GetDiskInfo():
        index = disk[0];
        dev = disk[1];
        used = disk[3];
        free = disk[4];
        percent = disk[5];
        disksInfo += f"[{index}]    {dev}    {used}Gb({percent}%)\n";
    del i;

    i = format(memInfo[1], ".0f");
    subject = f"服务器资源警告";
    body = f"内存:{GetMemoryInfo()[1]}MB\n\nCPU: \n{cpuInfo}\n磁盘剩余空间: \n{disksInfo}";

    encoding = 'utf-8';
    mail = MIMEText(body.encode(encoding), 'plain', encoding);
    mail['Subject'] = Header(subject, encoding);
    mail['From'] = fromMail;
    mail['To'] = toMail;
    mail['Date'] = formatdate();

    smtp = smtplib.SMTP_SSL(smtpHost, smtpPort) if smtpWithSSL else smtplib.SMTP(smtpHost, smtpPort);
    smtp.login(username, password);
    smtp.sendmail(fromMail, toMail, mail.as_string())
    smtp.close();


aaa = 0


def JobA():
    global aaa
    global lastOverThreshold;
    memInfo = GetMemoryInfo();
    cpuInfo = GetCpuInfo()

    om = memInfo[1] >= memoryThreshold;
    oc = False

    average = 0
    for ci in cpuInfo:
        average += ci
    average = average / len(cpuInfo)

    if average >= cpuThreshold:
        aaa += 1
    else:
        aaa = max(0, aaa - 1)

    if aaa > 6 * 3:  # 3min
        oc = True
        aaa = 0
    else:
        oc = False

    print(cpuInfo)

    if (om or oc) and not lastOverThreshold:
        SendAMail(memInfo);
        print(GetTime() + ": sent a mail");
    lastOverThreshold = (om or oc);
    print(str(om) + "/" + str(oc) + '   aaa: ' + str(aaa))


print("Started")
scheduler = BlockingScheduler();
task = scheduler.add_job(JobA, 'interval', minutes=minutes, seconds=seconds);
scheduler.start();
print("Exit..")