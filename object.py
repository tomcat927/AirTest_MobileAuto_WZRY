#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2023-11-10            #
# Build  : 2023-11-10            #
# What   : IOS/Android 自动化任务  #
#################################
# .......
from datetime import datetime, timezone, timedelta
import time
from airtest.core.settings import Settings as ST
import logging
import sys
import os
import numpy as np
import random
import traceback
# 重写函数#
from airtest.core.api import Template, connect_device, sleep
from airtest.core.api import exists as exists_o
from airtest.core.api import touch as touch_o
from airtest.core.api import swipe as swipe_o
from airtest.core.api import start_app as start_app_o
from airtest.core.api import stop_app as stop_app_o
# from airtest.core.api import touch as touch
# from airtest.core.api import swipe as swipe
# from airtest.core.api import exists as exists


def connect_status(times=10):
    png = Template(r"tpl_target_pos.png", record_pos=(-0.28, 0.153), resolution=(960, 540))
    for i in np.arange(times):
        try:
            exists_o(png)
            return True
        except:
            print(f"cndaqiang: 无法连接设备,重试中{i}")
            sleep(1)
            continue
    print("cndaqiang: 设备失去联系")
    return False


def exists(*args, **kwargs):
    try:
        result = exists_o(*args, **kwargs)
    except:
        traceback.print_exc()
        print("cndaqiang: exists失败")
        sleep(1)
        try:
            result = exists_o(*args, **kwargs)
        except:
            traceback.print_exc()
            print("cndaqiang: 再次尝试仍失败")
            result = False
    return result


def touch(*args, **kwargs):
    try:
        result = touch_o(*args, **kwargs)
    except:
        traceback.print_exc()
        print("cndaqiang: touch失败")
        sleep(1)
        try:
            traceback.print_exc()
            result = touch_o(*args, **kwargs)
        except:
            print("cndaqiang: 再次尝试仍失败")
            result = False
    return result


def swipe(*args, **kwargs):
    try:
        result = swipe_o(*args, **kwargs)
    except:
        traceback.print_exc()
        print("cndaqiang: swipe失败")
        sleep(1)
        try:
            result = swipe_o(*args, **kwargs)
        except:
            traceback.print_exc()
            print("cndaqiang: 再次尝试仍失败")
            result = False
    return result


def start_app(*args, **kwargs):
    try:
        result = True
        start_app_o(*args, **kwargs)
    except:
        traceback.print_exc()
        print("cndaqiang: start_app失败")
        sleep(1)
        try:
            result = True
            start_app_o(*args, **kwargs)
        except:
            traceback.print_exc()
            print("cndaqiang: 再次尝试仍失败")
            result = False
        if not connect_status():
            TimeErr("start_app:"+"连接不上设备")
            return False
    return result


def stop_app(*args, **kwargs):
    try:
        result = True
        stop_app_o(*args, **kwargs)
    except:
        traceback.print_exc()
        print("cndaqiang: stop_app失败")
        sleep(1)
        try:
            result = True
            stop_app_o(*args, **kwargs)
        except:
            traceback.print_exc()
            print("cndaqiang: 再次尝试仍失败")
            result = False
        if not connect_status():
            TimeErr("start_app:"+"连接不上设备")
            return False
    return result


# ........................
logger = logging.getLogger("airtest")
logger.setLevel(logging.WARNING)
# python -m pip install --upgrade --no-deps --force-reinstall airtest
ST.OPDELAY = 1
# 全局阈值的范围为[0, 1]
ST.THRESHOLD_STRICT = 0.8  # assert_exists语句touch(Template(r"tpl1689665366952.png", record_pos=(-0.425, -0.055), resolution=(960, 540)))的默认阈值，一般比THRESHOLD更高一些
ST.THRESHOLD = 0.8  # 其他语句的默认阈值
# ST.FIND_TIMEOUT=10 #*2 #获取截图的时间限制
# ST.FIND_TIMEOUT_TMP=1#匹配图形的时间限制, 也许可以再改小些加速
# 时间参数
# 防止服务器时区不同,设定时间为东八区
# 创建一个表示东八区时区的 timedelta 对象
eastern_eight_offset = timedelta(hours=8)
# 创建一个时区对象
eastern_eight_tz = timezone(eastern_eight_offset)
# 这个设置可以极低的降低airtest输出到屏幕的信息

# 设置,虚拟机,android docker, iphone, etc,主要进行设备的连接和重启


def TimeECHO(info="None", end=""):
    # 获取当前日期和时间
    current_datetime = datetime.now(eastern_eight_tz)
    # 格式化为字符串（月、日、小时、分钟、秒）
    formatted_string = current_datetime.strftime("[%m-%d %H:%M:%S]")
    modified_args = formatted_string+info
    if len(end) > 0:
        print(modified_args, end=end)
    else:
        print(modified_args)
    # 如果airtest客户端报错,python命令行不报错.就制定airtest的oython路径为anaconda的python


def TimeErr(info="None"):
    TimeECHO("NNNN:"+info)


def uniq_array_order(arr):
    if not arr:  # 如果输入的列表为空
        return []
    #
    seen = set()
    unique_elements = []
    for item in arr:
        if item not in seen:
            unique_elements.append(item)
            seen.add(item)
    return unique_elements


class DQWheel:
    def __init__(self, var_dict_file='var_dict_file.txt', prefix="", mynode=-10, totalnode=-10, 容器优化=False):
        self.timedict = {}
        self.容器优化 = 容器优化
        self.辅助同步文件 = "NeedRebarrier.txt"
        self.mynode = mynode
        self.totalnode = totalnode
        self.prefix = prefix
        if self.mynode >= 0:
            self.prefix = f"({mynode})"+self.prefix
        #
        self.barrierlimit = 60*20  # 同步最大时长
        self.filelist = []  # 建立的所有文件，用于后期clear
        self.var_dict_file = var_dict_file
        self.var_dict = self.read_dict(self.var_dict_file)
        self.savepos = True
        #
        self.stopnow = False
        self.stopfile = ".tmp.barrier.EXIT.txt"
        self.stopinfo = ""
        self.connecttimes = 0
        self.connecttimesMAX = 20
        self.独立同步文件 = self.prefix+"NeedRebarrier.txt"
        self.removefile(self.独立同步文件)

    def list_files(self, path):
        files = []
        with os.scandir(path) as entries:
            for entry in entries:
                files.append(entry.name)
        return files
    #

    def init_clean(self):
        # 不要删除这个文件,开局采用同步的方式进行统一删除,不然时间差会导致很多问题
        # self.removefile(self.辅助同步文件)
        # os.listdir(".")不显示隐藏文件
        for name in self.list_files("."):
            text = ".tmp.barrier."
            if text == name[:len(text)]:
                TimeECHO(self.prefix+f"清理旧文件:{name}")
                self.removefile(name)
    #

    def timelimit(self, timekey="", limit=0, init=True):
        if self.容器优化:
            limit = limit+120  # 容器中比较卡,多反应一会
        if len(timekey) == 0:
            timekey = "none"
        if not timekey in self.timedict.keys():
            init = True
        if init:
            self.timedict[timekey] = time.time()
            return False
        else:
            if time.time()-self.timedict[timekey] > limit:
                TimeECHO(self.prefix+f"[{timekey}]>{limit}s")
                self.timedict[timekey] = time.time()
                return True
            else:
                return False

    def removefile(self, filename):
        TimeECHO(self.prefix+f"remove[{filename}]")
        if os.path.exists(filename):
            try:
                os.remove(filename)
                TimeECHO(self.prefix+"删除["+filename+"]成功")
            except:
                traceback.print_exc()
                TimeECHO(self.prefix+"删除["+filename+"]失败")
                return False
            if os.path.exists(filename):
                TimeErr(self.prefix+"["+filename+"]还存在")
                return False
            else:
                return True
        else:
            TimeECHO(self.prefix+"不存在["+filename+"]")
            return False
        return False

    def touchfile(self, filename, content=""):
        TimeECHO(self.prefix+f"touchfile[{filename}]")
        content = str(content)
        if len(content) > 0:
            self.removefile(filename)
        f = open(filename, 'w')
        f.write(content)
        f.close()
        end = ""
        if len(content) > 0:
            end = f"with ({content})"
        TimeECHO(self.prefix+f"创建[{filename}] {end} 成功")

    def touchstopfile(self, content="stop"):
        self.touchfile(self.stopfile, content=content)
        self.stopnow = True
        self.stopinfo = content

    def readstopfile(self):
        if os.path.exists(self.stopfile):
            self.stopinfo = self.readfile(self.stopfile)[0]
            self.stopnow = True
        else:
            self.stopnow = False
        return self.stopnow

    def readfile(self, filename):
        try:
            f = open(filename, 'r')
            content = f.readlines()
            f.close()
            TimeECHO(self.prefix+"Read["+filename+"]成功")
            return content
        except:
            TimeECHO(self.prefix+"Read["+filename+"]失败")
            return [""]

    #
    def touch同步文件(self, 同步文件=""):
        同步文件 = 同步文件 if len(同步文件) > 1 else self.辅助同步文件
        TimeECHO(f">{self.prefix}"*10)
        TimeECHO(self.prefix+f"创建同步文件{同步文件}")
        self.touchfile(同步文件)
        TimeECHO(f"<{self.prefix}"*10)
        # 该文件不添加到列表,仅在成功同步后才删除
        # self.filelist.append(self.辅助同步文件)

    def 存在同步文件(self, 同步文件=""):
        if len(同步文件) > 1:
            if os.path.exists(同步文件):
                TimeECHO(self.prefix+f"存在同步文件[{同步文件}]")
                return True
            else:
                return False
        #
        if os.path.exists(self.辅助同步文件):
            TimeECHO(self.prefix+f"存在辅助同步文件[{self.辅助同步文件}]")
            return True
        # 每个进程的独立文件不同,不同节点不会误判
        if os.path.exists(self.独立同步文件):
            TimeECHO(self.prefix+f"存在独立同步文件[{self.独立同步文件}]")
            return True
        return False

    def clean文件(self):
        for i in self.filelist:
            if os.path.exists(i):
                self.removefile(i)
        self.filelist = []
    #

    def barriernode(self, mynode, totalnode, name="barrierFile"):
        if totalnode < 2:
            return True
        if self.存在同步文件():
            TimeErr(self.prefix+f"同步{name}.检测到同步文件")
            return True
        filelist = []
        ionode = mynode == 0 or totalnode == 1
        #
        if ionode:
            TimeECHO(self.prefix+"."*10)
            TimeECHO(self.prefix+f">>>>>同步开始>{name}")
        #
        for i in np.arange(1, totalnode):
            filename = f".tmp.barrier.{i}.{name}.txt"
            if ionode:
                if os.path.exists(filename):
                    TimeErr(self.prefix+"完蛋,barriernode之前就存在同步文件")
                self.touchfile(filename)
            filelist.append(filename)
            self.filelist.append(filename)
        #
        self.timelimit(timekey=name, limit=self.barrierlimit, init=True)
        times = 0
        while not self.timelimit(timekey=name, limit=self.barrierlimit, init=False):
            times = times+1
            if self.存在同步文件():
                return True
            if ionode:
                barrieryes = True
                for i in filelist:
                    barrieryes = barrieryes and not os.path.exists(i)
                    if not barrieryes:
                        break
                if barrieryes:
                    TimeECHO(self.prefix+"."*10)
                    TimeECHO(self.prefix+f"<<<<<同步完成>{name}")
                    return True
                if times % 3 == 0:
                    TimeECHO(self.prefix+f"同步{name}检测中")
            else:
                if self.removefile(filelist[mynode-1]):
                    return True
            sleep(10)
        if ionode:
            for i in filelist:
                self.removefile(i)
            # 不清除也没事,start时会自动清除
        TimeErr(self.prefix+f":barriernode>{name}<同步失败,创建同步文件")
        self.touch同步文件()
        return False
    # 读取变量

    def read_dict(self, var_dict_file="position_dict.txt"):
        global 辅助
        # if 辅助: return {}
        import pickle
        var_dict = {}
        if os.path.exists(var_dict_file):
            TimeECHO(self.prefix+"读取"+var_dict_file)
            with open(var_dict_file, 'rb') as f:
                var_dict = pickle.load(f)
        return var_dict
        # 保存变量

    def save_dict(self, var_dict, var_dict_file="position_dict.txt"):
        global 辅助
        # if 辅助: return True
        import pickle
        f = open(var_dict_file, "wb")
        pickle.dump(var_dict, f)
        f.close

    def bcastvar(self, mynode, totalnode, var, name="bcastvar"):
        if totalnode < 2:
            return var
        dict_file = name+".txt"
        if mynode == 0:
            self.save_dict(var, dict_file)
        self.barriernode(mynode, totalnode, name)
        if self.存在同步文件():
            return var
        #
        var_new = self.read_dict(dict_file)
        for key in var:
            var[key] = var_new[key]
        return var

    def 存在任一张图(self, array, strinfo=""):
        array = uniq_array_order(array)
        判断元素集合 = array
        strinfo = strinfo if len(strinfo) > 0 else "图片"
        for idx, i in enumerate(判断元素集合):
            TimeECHO(self.prefix+f"判断{strinfo}:{i}")
            if exists(i):
                TimeECHO(self.prefix+f"找到{strinfo}:{i}")
                # 交换元素位置
                判断元素集合[0], 判断元素集合[idx] = 判断元素集合[idx], 判断元素集合[0]
                return True, 判断元素集合
        TimeECHO(self.prefix+"不在房间中")
        return False, 判断元素集合

    def existsTHENtouch(self, png=Template(r"1.png"), keystr="", savepos=False):
        savepos = savepos and len(keystr) > 0 and self.savepos
        #
        if self.connecttimes > self.connecttimesMAX:  # 大概率连接失败了,判断一下
            if connect_status(max(2, self.connecttimesMAX-self.connecttimes+10)):  # 出错后降低判断的次数
                self.connecttimes = 0
            else:
                self.connecttimes = self.connecttimes+1
                self.touch同步文件(self.独立同步文件)
                return False
        #
        if savepos:
            if keystr in self.var_dict.keys():
                touch(self.var_dict[keystr])
                TimeECHO(self.prefix+"touch (saved) "+keystr)
                sleep(0.1)
                return True
        pos = exists(png)
        if pos:
            self.connecttimes = 0
            touch(pos)
            if len(keystr) > 0:
                TimeECHO(self.prefix+"touch "+keystr)
            if savepos:
                self.var_dict[keystr] = pos
                self.save_dict(self.var_dict, self.var_dict_file)
            return True
        else:
            self.connecttimes = self.connecttimes+1
            if len(keystr) > 0:
                TimeECHO(self.prefix+"NotFound "+keystr)
            return False

    #
    # touch的总时长timelimit s, 或者总循环次数<10
    def LoopTouch(self, png=Template(r"1.png"), keystr="", limit=0, loop=10, savepos=False):
        timekey = "LOOPTOUCH"+keystr+str(random.randint(1, 500))
        if limit + loop < 0.5:
            limit = 0
            loop = 1
        self.timelimit(timekey=timekey, limit=limit, init=True)
        runloop = 1
        while self.existsTHENtouch(png=png, keystr=keystr+f".{runloop}", savepos=savepos):
            if limit > 0:
                if self.timelimit(timekey=timekey, limit=limit, init=False):
                    TimeErr(self.prefix+"TOUCH"+keystr+"超时.....")
                    break
            if runloop > loop:
                TimeErr(self.prefix+"TOUCH"+keystr+"超LOOP.....")
                break
            sleep(10)
            runloop = runloop+1
        #
        if exists(png):
            TimeErr(keystr+"图片仍存在")
            return True
        else:
            return False
    # 这仅针对辅助模式,因此同步文件取self.辅助同步文件

    def 必须同步等待成功(self, mynode, totalnode, 同步文件="", sleeptime=60*5):
        同步文件 = 同步文件 if len(同步文件) > 1 else self.辅助同步文件
        if totalnode < 2:
            self.removefile(同步文件)
            return True
        if self.存在同步文件(同步文件):  # 单进程各种原因出错时,多进程无法同步时
            if self.readstopfile():
                return
            TimeECHO(self.prefix+"-."*20)
            TimeECHO(self.prefix+f"存在同步文件({同步文件}),第一次尝试同步同步程序")
            start_timestamp = int(time.time())
            # 第一次尝试同步
            self.同步等待(mynode, totalnode, 同步文件, sleeptime)
            # 如果还存在说明同步等待失败,那么改成hh:waitminu*N时刻进行同步
            while self.存在同步文件(同步文件):
                if self.readstopfile():
                    return
                waitminu = int(min(59, 5*totalnode))
                TimeErr(self.prefix+f"仍然存在同步文件,进行{waitminu}分钟一次的循环")
                hour, minu, sec = self.time_getHMS()
                minu = minu % waitminu
                if minu > totalnode:
                    sleepsec = (waitminu-minu)*60-sec
                    TimeECHO(self.prefix+f"等待{sleepsec}s")
                    sleep(sleepsec)
                    continue
                end_timestamp = int(time.time())
                sleepNtime = max(10, sleeptime-(end_timestamp-start_timestamp))+mynode*5
                self.同步等待(mynode, totalnode, 同步文件, sleepNtime)
        TimeECHO(self.prefix+"-+"*20)
        return not self.存在同步文件(同步文件)

    # 这仅针对辅助模式,因此同步文件取self.辅助同步文件
    def 同步等待(self, mynode, totalnode, 同步文件="", sleeptime=60*5):
        同步文件 = 同步文件 if len(同步文件) > 1 else self.辅助同步文件
        if totalnode < 2:
            self.removefile(同步文件)
            return True
        ionode = mynode == 0 or totalnode == 1
        # 同步等待是为了处理,程序因为各种原因无法同步,程序出粗.
        # 重新校验各个进程
        # Step1. 检测到主文件{同步文件} 进入同步状态
        # Step2. 确定所有进程均检测到主文件状态
        # Step3. 检测其余进程是否都结束休息状态
        prefix = f"({mynode})"
        主辅节点通信完成 = False
        发送信标 = True
        # 一个节点、一个节点的check
        if not os.path.exists(同步文件):
            return True
        TimeECHO(self.prefix+":进入同步等待")
        同步成功 = True
        name = 同步文件
        全部通信成功文件 = 同步文件+".同步完成.txt"
        全部通信失败文件 = 同步文件+".同步失败.txt"
        self.filelist.append(全部通信成功文件)
        # 前两个节点首先进行判定,因此先进行删除
        if mynode < 2:
            self.removefile(全部通信失败文件)
        # 最后一个通过才会删除成功文件,避免残留文件干扰
        self.removefile(全部通信成功文件)
        for i in np.arange(1, totalnode):
            if mynode > 0 and mynode != i:
                continue
            TimeECHO(self.prefix+f":进行同步循环{i}")
            sleep(mynode*5)
            if not os.path.exists(同步文件):
                TimeECHO(self.prefix+f"不存在同步文件{同步文件},退出")
                return True
            if self.readstopfile():
                return
            #
            主辅通信成功 = False
            filename = f".tmp.barrier.{i}.{name}.in.txt"
            if ionode:
                hour, minu, sec = self.time_getHMS()
                # myrandom=str(random.randint(totalnode+100, 500))+f"{hour}{minu}{sec}"
                myrandom = f"{i}{totalnode}{hour}{minu}{sec}"
                self.touchfile(filename, content=myrandom)
                lockfile = f".tmp.barrier.{myrandom}.{i}.{name}.in.txt"
                self.touchfile(lockfile)
                sleep(5)
                self.filelist.append(filename)
                self.filelist.append(lockfile)
                # 开始通信循环
                主辅通信成功 = False
                for sleeploop in np.arange(60*5):
                    if self.readstopfile():
                        return
                    if not os.path.exists(lockfile):
                        主辅通信成功 = True
                        self.removefile(filename)
                        break
                    sleep(1)
                # 判断通信成功与否
                同步成功 = 同步成功 and 主辅通信成功
                if 同步成功:
                    TimeECHO(prefix+f"同步{i}成功")
                else:
                    TimeECHO(prefix+f"同步{i}失败")
                    self.touchfile(全部通信失败文件)
                    return False
                continue
            else:
                同步成功 = False
                # 辅助节点,找到特定,就循环5分钟
                myrandom = str(-100)
                myrandom_new = myrandom
                lockfile = f".tmp.barrier.{myrandom}.{i}.{name}.in.txt"
                TimeECHO(self.prefix+f":进行同步判定{i}")
                sleeploop = 0
                for sleeploop in np.arange(60*5*(totalnode-1)):
                    if self.readstopfile():
                        return
                    # 主辅通信循环
                    if os.path.exists(filename):
                        if sleeploop % 5 == 0:
                            myrandom_new = self.readfile(filename)[0].strip()
                    if len(myrandom_new) > 0 and myrandom_new != myrandom:
                        myrandom = myrandom_new
                        TimeECHO(prefix+f"同步文件更新myrandom={myrandom}")
                        lockfile = f".tmp.barrier.{myrandom}.{i}.{name}.in.txt"
                        sleep(10)
                        主辅通信成功 = self.removefile(lockfile)
                    if not 主辅通信成功 and len(myrandom) > 0:
                        TimeECHO(prefix+f"还存在{lockfile}")
                        主辅通信成功 = self.removefile(lockfile)
                    # 避免存在旧文件没有删除的情况,这里不断读取å
                    if 主辅通信成功:
                        hour, minu, sec = self.time_getHMS()
                        if sleeploop % 10 == 0:
                            TimeECHO(prefix+f"正在寻找全部通信成功文件>{全部通信成功文件}<")
                        if os.path.exists(全部通信成功文件):
                            TimeECHO(prefix+f"监测到全部通信成功文件{全部通信成功文件}")
                            同步成功 = True
                            break
                        if os.path.exists(全部通信失败文件):
                            TimeErr(prefix+f"监测到全部通信失败文件{全部通信失败文件}")
                            return False
                    sleep(1)
        # 到此处完成
        # 因为是逐一进行同步的,所以全部通信成功文件只能由最后一个node负责删除
        同步成功 = 同步成功 and not os.path.exists(全部通信失败文件)
        if 同步成功:
            TimeECHO(prefix+"同步等待成功")
            file_sleeptime = ".tmp.barrier.sleeptime.txt"
            if ionode:
                TimeECHO(prefix+f"存储sleeptime到[{file_sleeptime}]")
                self.touchfile(filename=file_sleeptime, content=str(sleeptime))
                TimeECHO(prefix+"开始删建文件")
                self.clean文件()
                self.touchfile(全部通信成功文件)
                self.removefile(同步文件)
                self.removefile(全部通信失败文件)
            else:
                TimeECHO(prefix+"开始读取sleeptime")
                sleeptime_read = self.readfile(file_sleeptime)[0].strip()
                if len(sleeptime_read) > 0:
                    sleeptime = int(sleeptime_read)
        else:
            TimeErr(prefix+"同步等待失败")
            return False

        #
        self.barriernode(mynode, totalnode, "同步等待结束")
        TimeECHO(self.prefix+f"需要sleep{sleeptime}")
        sleep(sleeptime)
        return not os.path.exists(同步文件)

    def time_getHM(self):
        current_time = datetime.now(eastern_eight_tz)
        hour = current_time.hour
        minu = current_time.minute
        return hour, minu

    def time_getHMS(self):
        current_time = datetime.now(eastern_eight_tz)
        hour = current_time.hour
        minu = current_time.minute
        sec = current_time.second
        return hour, minu, sec

    def time_getYHMS(self):
        current_time = datetime.now(eastern_eight_tz)
        year = current_time.hour
        hour = current_time.hour
        minu = current_time.minute
        sec = current_time.second
        return year, hour, minu, sec

    def stoptask(self):
        TimeErr(self.prefix+f"停止Airtest控制,停止信息"+self.stopinfo)
        return
        # 该命令无法结束,直接return吧
        # sys.exit()

    # 旧脚本,适合几个程序,自动商量node编号

    def autonode(self, totalnode):
        if totalnode < 2:
            return 0
        node = -10
        PID = os.getpid()
        filename = "init_node."+str(totalnode)+"."+str(PID)+".txt"
        self.touchfile(filename)
        TimeECHO(self.prefix+"自动生成node中:"+filename)
        PID_dict = {}
        for i in np.arange(60):
            for name in os.listdir("."):
                if "init_node."+str(totalnode)+"." in name:
                    PID_dict[name] = name
            if len(PID_dict) == totalnode:
                break
            sleep(5)
        if len(PID_dict) != totalnode:
            self.removefile(filename)
            TimeECHO(self.prefix+"文件数目不匹配")
            return node
        #
        strname = np.array(list(PID_dict.keys()))
        PIDarr = np.zeros(strname.size)
        for i in np.arange(PIDarr.size):
            PIDarr[i] = int(strname[i].split(".")[2])
        PIDarr = np.sort(PIDarr)
        for i in np.arange(PIDarr.size):
            TimeECHO(self.prefix+"i="+str(i)+". PID="+str(PID)+". PIDarr[i]="+str(PIDarr[i]))
            if PID == PIDarr[i]:
                node = i

        if node < 0:
            TimeECHO(self.prefix+"node < 0")
            self.removefile(filename)
            return node
        #
        TimeECHO(self.prefix+"mynode:"+str(node))
        if self.barriernode(node, totalnode, "audfonode"):
            self.removefile(filename)
            return node


class deviceOB:
    def __init__(self, 设备类型="IOS", mynode=0, totalnode=1, LINK="ios:///http://192.168.12.130:8100", APPID=None):
        self.LINK = LINK
        self.LINKport = self.LINK.split(":")[-1]
        self.LINKhead = self.LINK[:-len(self.LINKport)]
        self.device = None
        self.控制端 = sys.platform.lower()
        if "darwin" in self.控制端:  # 避免和windows一致
            self.控制端 = "macos"
        self.设备类型 = 设备类型.lower()
        # 设备ID,用于控制设备重启关闭省电等,为docker和虚拟机使用
        self.设备ID = None
        self.mynode = mynode
        self.prefix = f"({self.mynode})"
        self.totalnode = totalnode
        self.PID = -10  # Windows+Blustack专用,关闭特定虚拟机
        #
        self.连接设备()
        # APPID
        self.APPID = "com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.APPID = APPID if APPID else self.APPID
        # start_app(self.APPID);sleep(5)
        #
        self.实体终端 = False
        self.实体终端 = "mac" in self.控制端 or "ios" in self.设备类型
        self.容器优化 = "linux" in self.控制端 and "android" in self.设备类型
        #

    # 尝试连接timesMax次,当前是times次
    def 连接设备(self, times=1, timesMax=3):
        self.device = False
        TimeECHO(self.prefix+f"{self.LINK}:开始第{times}/{timesMax+1}次连接")
        try:
            self.device = connect_device(self.LINK)
            if self.device:
                TimeECHO(self.prefix+f"{self.LINK}:链接成功")
                return True
        except:
            TimeErr(self.prefix+f"{self.LINK}:链接失败")
            if "ios" in self.设备类型:
                TimeECHO(self.prefix+"重新插拔数据线")
        #
        if times <= timesMax:
            TimeECHO(self.prefix+f"{self.LINK}:链接失败,重启设备再次连接")
            self.启动设备()
            return self.连接设备(times+1, timesMax)
        else:
            TimeErr(self.prefix+f"{self.LINK}:链接失败,无法继续")
            return False

    def 启动设备(self):
        if "ios" in self.设备类型:
            try:
                TimeECHO(self.prefix+f"IOS测试重启中")
                import subprocess
                result = subprocess.getstatusoutput("tidevice list")
                if 'ConnectionType.USB' in result[1]:
                    # wdaproxy这个命令会同时调用xctest和relay，另外当wda退出时，会自动重新启动xctest
                    # tidevice不支持企业签名的WDA
                    self.LINKport = str(int(self.LINKport)+1)
                    self.LINK = self.LINKhead+self.LINKport
                    os.system(f"tidevice $(cat para.txt) wdaproxy -B com.facebook.WebDriverAgentRunner.cndaqiang.xctrunner --port {self.LINKport} > tidevice.result.txt 2>&1 &")
                else:
                    TimeErr(self.prefix+": tidevice list 无法找到设备, IOS重启失败")
                    #
            except:
                TimeECHO(self.prefix+f"IOS重启失败")
            sleep(20)
            return True
        # android
        try:
            if "mac" in self.控制端 or "127.0.0.1" not in self.LINK:
                TimeECHO(self.prefix+f"测试远程连接安卓设备by adb reconnect")
                command = "adb disconnect "+self.LINK.split("/")[-1]
                command = command+"; adb connect "+self.LINK.split("/")[-1]
            elif "win" in self.控制端:  # BlueStack虚拟机
                CMDtitle = "cndaqiangHDPlayer"+str(self.mynode)
                command = f"start \"{CMDtitle}\" /MIN C:\Progra~1\BlueStacks_nxt\HD-Player.exe --instance Nougat32_%{self.mynode}"
            elif "linux" in self.控制端:  # 容器
                虚拟机ID = f"androidcontain{self.mynode}"
                command = f"docker restart {虚拟机ID}"
            exit_code = os.system(command)
            if exit_code == 0:
                sleep(60)  # 等待设备启动过程
                TimeECHO(self.prefix+f"启动成功")
                return True
            else:
                TimeErr(self.prefix+f"启动失败")
                return False
        except:
            TimeErr(self.prefix+f"启动失败")
            return False

    def 关闭设备(self):
        # ios
        if "ios" in self.设备类型:
            if "mac" in self.控制端 or "127.0.0.1" in self.LINK:
                TimeECHO(self.prefix+f"测试本地IOS关闭中")
                command = "tidevice reboot"
            else:
                TimeECHO(self.prefix+f"当前模式无法关闭IOS")
                return False
            try:
                exit_code = os.system(command)
                if exit_code == 0:
                    TimeECHO(self.prefix+f"关闭成功")
                    sleep(60)
                    return True
                else:
                    TimeECHO(self.prefix+f"关闭失败")
                    return False
            except:
                TimeErr(self.prefix+f"关闭失败")
                return False
        # android
        try:
            if "mac" in self.控制端 or "127.0.0.1" not in self.LINK:
                TimeECHO(self.prefix+f"测试远程断开安卓设备by adb disconnect")
                command = "adb disconnect "+self.LINK.split("/")[-1]
            elif "win" in self.控制端:  # BlueStack虚拟机
                CMDtitle = "cndaqiangHDPlayer"+str(mynode)
                command = f"start \"{CMDtitle}\" /MIN C:\Progra~1\BlueStacks_nxt\HD-Player.exe --instance Nougat32_%{self.mynode}"
                if int(self.PID) > 0:
                    command = f'taskkill /F /FI "PID eq {self.PID}"'
                else:  # 关闭所有虚拟机，暂时用不到
                    command = 'taskkill /f /im HD-Player.exe'
            elif "linux" in self.控制端:  # 容器
                虚拟机ID = f"androidcontain{self.mynode}"
                command = f"docker stop {虚拟机ID}"
            #
            exit_code = os.system(command)
            if exit_code == 0:
                TimeECHO(self.prefix+f"关闭成功")
                return True
            else:
                TimeECHO(self.prefix+f"关闭失败")
                return False
        except:
            TimeErr(self.prefix+f"关闭失败")
            return False
    #

    def 重启设备(self, sleeptime=0):
        TimeECHO(self.prefix+f"重新启动{self.LINK}")
        self.关闭设备()
        sleeptime = max(10, sleeptime-60)
        printtime = max(30, sleeptime/10)
        TimeECHO(self.prefix+"sleep %d min" % (sleeptime/60))
        for i in np.arange(int(sleeptime/printtime)):
            TimeECHO(self.prefix+f"...taskkill_sleep: {i}", end='\r')
            sleep(printtime)
        self.启动设备()
        self.连接设备()

    #
    def 关闭APP(self):
        TimeECHO(self.prefix+f"关闭APP[{self.APPID}]中")
        if not stop_app(self.APPID):
            TimeErr(self.prefix+"关闭失败,可能失联")
            return False
        else:
            return True

    def 打开APP(self):
        TimeECHO(self.prefix+f"打开APP[{self.APPID}]中")
        if not start_app(self.APPID):
            TimeErr(self.prefix+"打开失败,可能失联")
            return False
        else:
            sleep(20)
        if "com.tencent.tmgp.sgame" in self.APPID:  # IOS
            sleep(30)  # ipSE的打开APP是在是太慢了
        return True

    def 重启APP(self, sleeptime=0):
        TimeECHO(self.prefix+f"重启APP中")
        try:
            self.关闭APP()
        except:
            TimeErr(self.prefix+f"关闭APP失败")
        sleep(10)
        sleeptime = max(10, sleeptime)  # 这里的单位是s
        printtime = max(30, sleeptime/10)
        if sleeptime > 60*60:  # >1h
            self.重启设备(sleeptime)
        else:
            print("sleep %d min" % (sleeptime/60))
            nstep = int(sleeptime/printtime)
            for i in np.arange(nstep):
                TimeECHO(self.prefix+f"...taskkill_sleep: {i}/{nstep}", end='\r')
                sleep(printtime)
        TimeECHO(self.prefix+f"打开程序")
        if self.打开APP():
            TimeECHO(self.prefix+f"打开程序成功,sleep60*2")
            sleep(60*2)
            return True
        else:
            TimeECHO(self.prefix+f"打开程序失败")
            return False


class wzyd_libao:
    def __init__(self, prefix="", APPID="com.tencent.gamehelper.smoba"):
        self.体验币成功 = False
        self.营地活动 = True
        self.APPID = APPID
        # 这里prefix+,是用于输出到屏幕
        # 输入的prefix是mynode
        self.prefix = f"({prefix})王者营地:"
        self.营地初始化FILE = prefix+".营地初始化.txt"
        self.营地需要登录FILE = prefix+".营地需要登录.txt"
        # 使用输入的prefix,才可以用一套同步文件
        self.Tool = DQWheel(prefix=self.prefix)
        self.IOS = "smobagamehelper" in self.APPID
        # 这两个图标会根据活动变化,可以用下面的注入替换
        self.个人界面图标 = Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960))
        self.游戏界面图标 = Template(r"tpl1704381547456.png", record_pos=(0.187, 0.726), resolution=(540, 960))
        self.每日福利图标 = Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960))
        self.一键领取按钮 = Template(r"tpl1706338731419.png", record_pos=(0.328, -0.365), resolution=(540, 960))
        if self.IOS:
            self.每日福利图标 = Template(r"tpl1700272452555.png", record_pos=(-0.198, -0.002), resolution=(640, 1136))
        self.营地大厅元素 = []
        self.营地大厅元素.append(self.个人界面图标)
        self.营地大厅元素.append(self.游戏界面图标)
        self.营地大厅元素.append(self.每日福利图标)
    #

    def 判断营地大厅中(self):
        self.营地大厅元素.append(self.个人界面图标)
        self.营地大厅元素.append(self.游戏界面图标)
        self.营地大厅元素.append(self.每日福利图标)
        存在, self.营地大厅元素 = self.Tool.存在任一张图(self.营地大厅元素, "营地大厅元素")
        return 存在

    def RUN(self):
        if not start_app(self.APPID):
            TimeECHO(self.prefix+"营地无法打开,返回")
            return False
        #
        sleep(20)  # 等待营地打开
        if os.path.exists(self.营地初始化FILE):
            TimeECHO(self.prefix+f":注入营地初始化代码({self.营地初始化FILE})")
            exec_insert = self.Tool.readfile(self.营地初始化FILE)
            for i_insert in exec_insert:
                trim_insert = i_insert.strip()
                if len(trim_insert) < 1:
                    continue
                if '#' == trim_insert[0]:
                    continue
                try:
                    exec(i_insert)
                    if "TimeE" not in i_insert:
                        TimeECHO(self.prefix+".营地初始化.run: "+i_insert[:-1])
                except:
                    TimeErr(self.prefix+".营地初始化.Error run: "+i_insert[:-1])
        #
        # 判断营地是否登录的界面
        if os.path.exists(self.营地需要登录FILE):
            TimeECHO(self.prefix+f"检测到{self.营地需要登录FILE}, 不领取礼包")
            return False
        if not self.判断营地大厅中():
            self.Tool.touchfile(self.营地需要登录FILE)
            TimeECHO(self.prefix+"营地没有登录,不领取礼包")
            return False
        #
        # 体验服只有安卓客户端可以领取
        if not self.IOS:
            self.体验服礼物()
        self.每日签到任务()
        self.营地币兑换碎片()
        stop_app(self.APPID)

    def 体验服礼物(self, times=1):
        #
        if times == 1:
            self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=False):
                TimeECHO(self.prefix+f"体验服礼物{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"体验币{times}")
        if times > 0:
            sleep(5)
        stop_app(self.APPID)
        start_app(self.APPID)
        sleep(10)
        times = times+1
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.游戏界面图标, self.prefix+"游戏界面图标", savepos=True)
        sleep(5)
        # 判断是否在体验服框架
        # 这里需要提前手动把体验服加到选择界面
        体验服判断图标 = Template(r"tpl1704381586249.png", record_pos=(-0.293, -0.026), resolution=(540, 960))
        体验服大头图标 = Template(r"tpl1704381887267.png", record_pos=(-0.42, -0.787), resolution=(540, 960))
        体验服入口 = False
        for i in range(5):
            if exists(体验服判断图标):
                体验服入口 = True
                break
            self.Tool.existsTHENtouch(体验服大头图标, "体验服大头图标", savepos=False)
        if not 体验服入口:
            TimeECHO(self.prefix+f"没有找到体验服入口,有可能营地有更新")
            return self.体验服礼物(times)
        #
        奖励兑换图标 = Template(r"tpl1704381904053.png", record_pos=(-0.209, -0.026), resolution=(540, 960))
        self.Tool.existsTHENtouch(奖励兑换图标, self.prefix+"体验服奖励兑换图标", savepos=True)
        sleep(5)
        奖励兑换网页图标 = Template(r"tpl1704381965060.png", rgb=True, target_pos=7, record_pos=(0.243, -0.496), resolution=(540, 960))
        if not self.Tool.existsTHENtouch(奖励兑换网页图标, self.prefix+"奖励兑换网页图标", savepos=False):
            sleep(20)
            if not self.Tool.existsTHENtouch(奖励兑换网页图标, self.prefix+"奖励兑换网页图标", savepos=False):
                return self.体验服礼物(times)
        # 有时候会让重新登录
        重新登录 = Template(r"tpl1702610976931.png", record_pos=(0.0, 0.033), resolution=(540, 960))
        if self.Tool.existsTHENtouch(重新登录, self.prefix+"重新登录"):
            self.Tool.touchfile(self.prefix+"重新登录体验服.txt")
            return
        奖励页面 = Template(r"tpl1704522893096.png", record_pos=(0.239, 0.317), resolution=(540, 960))
        pos = False
        # 这里是等待刷新的过程,不用sleep那么久
        for i in range(10):
            sleep(5)
            pos = exists(奖励页面)
            if pos:
                break
            else:
                TimeECHO(self.prefix+f"寻找奖励兑换页面中{i}")

        if not pos:
            TimeECHO(self.prefix+"没进入奖励兑换页面")
            return self.体验服礼物(times)
        #
        swipe(pos, vector=[0.0, -0.5])
        碎片奖励 = Template(r"tpl1699874679212.png", record_pos=(-0.233, 0.172), resolution=(540, 960), threshold=0.9)
        奖励位置 = False
        for i in range(10):
            sleep(1)
            奖励位置 = exists(碎片奖励)
            if 奖励位置:
                break
            else:
                TimeECHO(self.prefix+f"寻找碎片奖励中{i}")
            swipe(pos, vector=[0.0, -0.5])
        if not 奖励位置:
            TimeECHO(self.prefix+"没找到体验币")
            return self.体验服礼物(times)
        #
        touch(奖励位置)
        成功领取 = Template(r"tpl1699874950410.png", record_pos=(-0.002, -0.006), resolution=(540, 960))
        if exists(成功领取):
            TimeECHO(self.prefix+"成功领取")
        else:
            TimeECHO(self.prefix+"领取过了/体验币不够")
        return
        #

    def 每日签到任务(self, times=1):
        TimeECHO(self.prefix+f"营地每日签到{times}")
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=False):
                TimeECHO(self.prefix+f"营地每日签到{times}超时退出")
                return False
        #
        if times > 0:
            sleep(5)
        times = times+1
        if times > 5:
            return False
        if times > 0:
            sleep(5)
        # 每日签到
        if not stop_app(self.APPID):
            return
        start_app(self.APPID)
        sleep(10)
        self.Tool.existsTHENtouch(self.个人界面图标, self.prefix+"王者营地个人界面", savepos=True)
        sleep(5)
        if not self.Tool.existsTHENtouch(self.每日福利图标, self.prefix+"王者营地每日福利", savepos=False):
            return self.每日签到任务(times)
        sleep(5)
        self.Tool.existsTHENtouch(self.一键领取按钮, "一键领取按钮")
        # 新款签到入口
        #
        签到入口 = Template(r"tpl1706339365291.png", target_pos=6, record_pos=(-0.011, -0.185), resolution=(540, 960))
        签到按钮 = Template(r"tpl1706339420536.png", record_pos=(0.106, -0.128), resolution=(540, 960))
        if self.Tool.existsTHENtouch(签到入口, "营地签到入口"):
            sleep(10)
            if self.Tool.existsTHENtouch(签到按钮, "营地签到按钮"):
                return self.每日签到任务(times)
            # 签到后也有礼物,在后面的营地币兑换碎片可以领到
        #
        return True

    def 营地币兑换碎片(self, times=1):
        TimeECHO(self.prefix+f"营地币兑换碎片{times}")
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=False):
                TimeECHO(self.prefix+f"营地币兑换碎片{times}超时退出")
                return False
        #
        if times > 0:
            sleep(5)
        times = times+1
        if times > 10:
            return False
        if not stop_app(self.APPID):
            return
        start_app(self.APPID)
        sleep(10)
        self.Tool.existsTHENtouch(self.个人界面图标, self.prefix+"个人界面")
        sleep(5)
        self.Tool.existsTHENtouch(self.每日福利图标, self.prefix+"每日福利")
        sleep(5)
        self.Tool.existsTHENtouch(self.一键领取按钮, "一键领取按钮")
        # 老款营地币兑换
        # if not self.Tool.existsTHENtouch(Template(r"tpl1699872561488.png", record_pos=(-0.317, 0.331), resolution=(540, 960)), self.prefix+"营地币兑换"):
        if not self.Tool.existsTHENtouch(Template(r"tpl1706338003287.png", record_pos=(0.389, 0.524), resolution=(540, 960)), self.prefix+"营地币兑换"):
            return self.营地币兑换碎片(times)
        兑换页面 = Template(r"tpl1699873075417.png", record_pos=(0.437, 0.167), resolution=(540, 960))
        pos = False
        for i in range(10):
            sleep(5)
            pos = exists(兑换页面)
            if pos:
                break
            else:
                TimeECHO(self.prefix+f"寻找兑换页面中{i}")
        if not pos:
            TimeECHO(self.prefix+"没进入营地币兑换页面")
            return self.营地币兑换碎片(times)
        swipe(pos, vector=[0.0, -0.5])
        碎片奖励 = Template(r"tpl1699873407201.png", record_pos=(0.009, 0.667), resolution=(540, 960))
        奖励位置 = False
        for i in range(5):
            sleep(1)
            奖励位置 = exists(碎片奖励)
            if 奖励位置:
                break
            else:
                TimeECHO(self.prefix+f"寻找营地币换碎片中{i}")
            swipe(pos, vector=[0.0, -0.5])
        if not 奖励位置:
            TimeECHO(self.prefix+"没找到营地币")
            return self.营地币兑换碎片(times)
        touch(奖励位置)
        self.Tool.existsTHENtouch(Template(r"tpl1699873472386.png", record_pos=(0.163, 0.107), resolution=(540, 960)))
        self.Tool.existsTHENtouch(Template(r"tpl1699873480797.png", record_pos=(0.163, 0.104), resolution=(540, 960)))


class wzry_task:
    # 备注
    # 新账户,第一次打开各种模块,如万向天宫,会有动画等展示,脚本不做处理,手动点几下，之后就不会出现了
    # 需要传递中文时,由于精简后无法输入中文,在shell中建
    # redroid_arm64:/mnt/sdcard/Download # touch 诗语江南s4tpxWGu.txt

    def __init__(self, 移动端="android", 对战模式="5v5匹配", shiftnode=0, debug=False, 限时组队时间=7):
        self.移动端 = 移动端
        self.mynode = self.移动端.mynode
        self.totalnode = self.移动端.totalnode
        self.组队模式 = self.totalnode > 1
        self.房主 = self.mynode == 0 or self.totalnode == 1
        self.prefix = f"({self.mynode})"
        #
        self.对战模式 = 对战模式  # "5v5匹配" or "王者模拟战"
        self.debug = debug  # 本地调试模式,加速,测试所有功能
        TimeECHO(self.prefix+f"对战模式:{self.对战模式}")
        #
        self.对战时间 = [5.1, 23]  # 单位hour,对战时间取N.m是为了让程序在N点时启动领取昨日没领完的礼包
        # 当hour小于此数字时才是组队模式
        self.限时组队时间 = 限时组队时间
        self.totalnode_bak = self.totalnode

        # <难度3蓝色,4紫色,5红色
        self.选择英雄 = True
        #
        self.Tool = DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.mynode}.txt",
                            mynode=self.mynode, totalnode=self.totalnode, 容器优化=self.移动端.容器优化)
        # 如果所有节点都清理文件会影响下面的同步等待的执行
        if self.房主:
            self.Tool.init_clean()
        # ------------------------------------------------------------------------------
        # 先确定每个节点是否都可以正常连接,这里不要退出,仅生成需要退出的信息和创建同步文件
        # 然后多节点进行同步后
        # 再统一退出
        if not connect_status():
            self.移动端.连接设备()
            if not self.移动端.device:
                TimeErr(self.prefix+"连接不上设备. 待同步后退出")
                if self.totalnode_bak > 1:  # 让其他节点抓紧结束
                    self.Tool.touchstopfile(f"{self.mynode}连接不上设备")
        # ------------------------------------------------------------------------------
        # 强制同步
        if self.totalnode_bak > 1:
            self.Tool.touch同步文件()
            self.Tool.必须同步等待成功(self.mynode, self.totalnode, sleeptime=10)
        # 检查连接状态以及退出
        if self.totalnode_bak > 1:
            if self.Tool.readstopfile():  # 这个只在多节点运行时会创建
                self.Tool.stoptask()
                return  # 就是结束
        else:
            if not connect_status():
                TimeErr(self.prefix+"连接不上设备. 退出")
                return

        self.Tool.barriernode(self.mynode, self.totalnode, "WZRYinit")
        #
        self.runstep = 0
        self.jinristep = 0

        # 控制参数
        self.选择人机模式 = True
        self.青铜段位 = False
        self.标准模式 = False
        self.触摸对战 = False
        self.标准触摸对战 = False
        self.赛季 = "2024"
        self.对战结束返回房间 = True
        self.无法进行组队 = False
        # 对应的控制文件
        self.结束游戏FILE = "WZRY.ENDGAME.txt"
        self.SLEEPFILE = "WZRY.SLEEP.txt"
        self.触摸对战FILE = "WZRY.TOUCH.txt"  # 在5v5的对战过程中,频繁触摸,提高金币数量
        self.标准模式触摸对战FILE = "WZRY.标准模式TOUCH.txt"  # 检测到该文件后该次对战使用5v5标准对战模式
        self.青铜段位FILE = f"WZRY.{self.mynode}.青铜段位.txt"  # 检测到该文件后该次对战使用5v5标准对战模式
        self.标准模式FILE = f"WZRY.{self.mynode}.标准模式.txt"  # 检测到该文件后该次对战使用5v5标准对战模式
        self.临时组队FILE = "WZRY.组队.txt"
        self.重新设置英雄FILE = f"WZRY.{self.mynode}.重新设置英雄.txt"
        self.临时初始化FILE = f"WZRY.{self.mynode}.临时初始化.txt"
        self.对战前插入FILE = f"WZRY.{self.mynode}.对战前插入.txt"
        self.重新登录FILE = f"WZRY.{self.mynode}.重新登录FILE.txt"
        self.无法进行组队FILE = f"WZRY.无法进行组队FILE.txt"
        self.免费商城礼包FILE = f"WZRY.{self.mynode}.免费商城礼包.txt"  # 检测到该文件后领每日商城礼包
        self.Tool.removefile(self.结束游戏FILE)
        self.Tool.removefile(self.SLEEPFILE)
        self.Tool.removefile(self.免费商城礼包FILE)
        # self.Tool.removefile(self.触摸对战FILE)
        # self.Tool.removefile(self.临时组队FILE)

        #
        self.王者营地礼包 = False
        if ":5555" in self.移动端.LINK:
            self.王者营地礼包 = True
        if "ios" in self.移动端.LINK:
            self.王者营地礼包 = True
        TimeECHO(self.prefix+f"本节点领取营地礼包:{self.王者营地礼包}")
        self.玉镖夺魁签到 = False
        #
        self.runinfo = {}
        self.runinfo["runstep"] = 0
        # 一些图库, 后期使用图片更新
        self.登录界面开始游戏图标 = Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540), threshold=0.9)
        self.大厅对战图标 = Template(r"tpl1689666004542.png", record_pos=(-0.102, 0.145), resolution=(960, 540))
        self.大厅万象天工 = Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540))
        self.房间中的开始按钮图标 = []
        self.房间中的开始按钮图标.append(Template(r"tpl1689666117573.png", record_pos=(0.096, 0.232), resolution=(960, 540)))
        self.房间中的开始按钮图标.append(Template(r"tpl1704331759027.png", record_pos=(0.105, 0.235), resolution=(960, 540)))
        # 新年活动结束时,替换一个常规的取消准备按钮
        self.房间中的取消按钮图标 = []
        self.房间中的取消按钮图标.append(Template(r"tpl1707180405239.png", record_pos=(0.104, 0.235), resolution=(960, 540)))
        self.房间中的取消按钮图标.append(Template(r"tpl1699179402893.png", record_pos=(0.098, 0.233), resolution=(960, 540), threshold=0.9))
        self.大厅元素 = []
        self.大厅元素.append(self.大厅对战图标)
        self.大厅元素.append(self.大厅万象天工)
        self.房间元素 = []
        self.房间元素.extend(self.房间中的开始按钮图标)
        self.房间元素.extend(self.房间中的取消按钮图标)
        self.房间元素.append(Template(r"tpl1690442701046.png", record_pos=(0.135, -0.029), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1700304317380.png", record_pos=(-0.38, -0.252), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1691463676972.png", record_pos=(0.356, -0.258), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1700304304172.png", record_pos=(0.39, -0.259), resolution=(960, 540)))
        # 登录关闭按钮
        self.王者登录关闭按钮 = []
        self.王者登录关闭按钮.append(Template(r"tpl1692947351223.png", record_pos=(0.428, -0.205), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1699616162254.png", record_pos=(0.38, -0.237), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540)))
        self.王者登录关闭按钮.append(Template(r"tpl1693271987720.png", record_pos=(0.428, -0.205), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1700294024287.png", record_pos=(0.465, -0.214), resolution=(1136, 640)))
        self.王者登录关闭按钮.append(Template(r"tpl1700918628072.png", record_pos=(-0.059, 0.211), resolution=(960, 540)))
        self.王者登录关闭按钮.append(Template(r"tpl1707232517229.png", record_pos=(0.394, -0.237), resolution=(960, 540)))
        #
        self.战绩页面元素 = []
        self.战绩页面元素.append(Template(r"tpl1699677816333.png", record_pos=(0.408, 0.226), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1699677826933.png", record_pos=(-0.011, -0.257), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1699766285319.png", record_pos=(-0.009, -0.257), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1699677835926.png", record_pos=(0.011, -0.134), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1699677870739.png", record_pos=(-0.369, 0.085), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1689727624208.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1689667038979.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
        self.战绩页面元素.append(Template(r"tpl1689669071283.png", record_pos=(-0.001, -0.036), resolution=(960, 540)))
        #
        # 头像数据
        英雄_诸葛 = Template(r"tpl1701436812155.png", record_pos=(-0.454, 0.134), resolution=(1136, 640))
        英雄_妲己 = Template(r"tpl1691818492021.png", record_pos=(-0.278, 0.029), resolution=(960, 540))
        英雄_海诺 = Template(r"tpl1701750143194.png", record_pos=(-0.36, 0.135), resolution=(960, 540))
        英雄_牙 = Template(r"tpl1701436836229.png", record_pos=(0.107, -0.085), resolution=(1136, 640))
        英雄_孙尚香 = Template(r"tpl1690442530784.png", record_pos=(0.11, -0.083), resolution=(960, 540))
        英雄_烈 = Template(r"tpl1701436844556.png", record_pos=(0.203, 0.025), resolution=(1136, 640))
        英雄_桑启 = Template(r"tpl1701750374410.png", record_pos=(0.202, 0.024), resolution=(1136, 640))
        英雄_太乙 = Template(r"tpl1690442560069.png", record_pos=(0.11, 0.025), resolution=(960, 540))
        英雄_鬼谷子 = Template(r"tpl1701759712161.png", record_pos=(0.203, 0.026), resolution=(1136, 640))
        英雄_云中 = Template(r"tpl1701750390892.png", record_pos=(-0.172, 0.24), resolution=(1136, 640))
        英雄_凯 = Template(r"tpl1689665521942.png", record_pos=(0.108, -0.086), resolution=(960, 540))
        英雄_八戒 = Template(r"tpl1701573854122.png", record_pos=(0.297, 0.135), resolution=(1136, 640))
        英雄_亚瑟 = Template(r"tpl1685515357752.png", record_pos=(-0.359, 0.129), resolution=(960, 540))
        # 一些数据
        参战英雄线路_dict = {}
        参战英雄头像_dict = {}
        参战英雄线路_dict[(shiftnode+0) % 6] = Template(r"tpl1689665490071.png", record_pos=(-0.315, -0.257), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+0) % 6] = 英雄_八戒
        参战英雄线路_dict[(shiftnode+1) % 6] = Template(r"tpl1689665455905.png", record_pos=(-0.066, -0.256), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+1) % 6] = 英雄_海诺
        参战英雄线路_dict[(shiftnode+2) % 6] = Template(r"tpl1689665540773.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+2) % 6] = 英雄_牙
        参战英雄线路_dict[(shiftnode+3) % 6] = Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+3) % 6] = 英雄_鬼谷子
        参战英雄线路_dict[(shiftnode+4) % 6] = Template(r"tpl1686048521443.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+4) % 6] = 英雄_云中
        参战英雄线路_dict[(shiftnode+5) % 6] = Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+5) % 6] = 英雄_太乙
        self.参战英雄线路 = 参战英雄线路_dict[self.mynode % 6]
        self.参战英雄头像 = 参战英雄头像_dict[self.mynode % 6]
        self.备战英雄线路 = 参战英雄线路_dict[(self.mynode+3) % 6]
        self.备战英雄头像 = 参战英雄头像_dict[(self.mynode+3) % 6]
        #
        # 刷新礼包的领取计时
        self.每日礼包()
        self.武道大会()
        self.六国远征()
        self.进行六国远征 = os.path.exists(self.prefix+"六国远征.txt")
        self.进行武道大会 = os.path.exists(self.prefix+"武道大会.txt")
        # 设置为0,可以保证下次必刷礼包
        self.Tool.timedict["领游戏礼包"] = 0
        self.Tool.timedict["领营地礼包"] = 0
        self.Tool.timedict["六国远征战"] = 0
        self.Tool.timedict["武道大会"] = 0
        self.Tool.touchfile(self.免费商城礼包FILE)
        # self.每日礼包()
        # self.每日礼包_每日任务()
        # self.每日礼包_邮件礼包()
        # self.每日礼包_妲己礼物()
        # self.每日礼包_王者营地()
        # self.六国远征()

    # 网络优化提示
    def 网络优化(self):
        if exists(Template(r"tpl1693669091002.png", record_pos=(-0.003, -0.015), resolution=(960, 540))):
            TimeECHO(self.prefix+"网络优化提示")
            self.Tool.existsTHENtouch(Template(r"tpl1693669117249.png", record_pos=(-0.102, 0.116), resolution=(960, 540)), "下次吧")

    def 确定按钮(self):
        确定按钮 = []
        确定按钮.append(Template(r"tpl1693194657793.png", record_pos=(0.001, 0.164), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1693886962076.png", record_pos=(0.097, 0.115), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1693660628972.png", record_pos=(-0.003, 0.118), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1689666290543.png", record_pos=(-0.001, 0.152), resolution=(960, 540), threshold=0.8))
        for i in 确定按钮:
            self.Tool.existsTHENtouch(i, f"确定{i}", savepos=False)

    def 关闭按钮(self):
        # 这个循环仅作为识别关闭按钮位置的循环
        # 主要用于: self.进入大厅时遇到的复杂的关闭按钮()
        self.王者登录关闭按钮 = uniq_array_order(self.王者登录关闭按钮)
        for i in self.王者登录关闭按钮:
            keyindex = f"王者登陆关闭按钮{i}"
            # if keyindex in self.Tool.var_dict.keys(): continue
            pos = exists(i)
            if pos:
                self.Tool.var_dict[keyindex] = pos
                self.Tool.existsTHENtouch(i, keyindex, savepos=True)
            else:
                TimeECHO(self.prefix+"未识别到"+keyindex)
        for i in self.王者登录关闭按钮:
            self.Tool.LoopTouch(i, f"关闭按钮{i}", loop=3, savepos=False)
    #

    def 进入大厅时遇到的复杂的关闭按钮(self):
        self.关闭按钮()
        if self.判断大厅中():
            return True
        TimeECHO(self.prefix+": 未能进入大厅,有可能有新的关闭按钮,继续尝试关闭中")
        for key, value in self.Tool.var_dict.items():
            if "王者登陆关闭按钮" not in key:
                continue
            TimeECHO(self.prefix+":尝试touch:"+key)
            touch(value)
            if self.判断大厅中():
                return True
        return False
        #

    def 判断战绩页面(self):
        存在, self.战绩页面元素 = self.Tool.存在任一张图(self.战绩页面元素, "战绩页面元素")
        return 存在

    def 进入大厅(self, times=1):
        TimeECHO(self.prefix+f"尝试进入大厅{times}")
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        if "ios" in self.移动端.LINK:
            配件不支持 = Template(r"tpl1701523669097.png", record_pos=(-0.001, 0.002), resolution=(1136, 640))
            关闭配件不支持 = Template(r"tpl1701523677678.png", record_pos=(-0.004, 0.051), resolution=(1136, 640))
            if exists(配件不支持):
                self.Tool.existsTHENtouch(关闭配件不支持, "关闭配件不支持")
        if self.判断大厅中():
            return True
        if self.判断对战中():
            self.Tool.timelimit(timekey="结束对战", limit=60*15)
            处理对战 = "模拟战" in self.对战模式
            if self.debug:
                处理对战 = True
            if self.标准触摸对战:
                处理对战 = True
            if self.触摸对战:
                处理对战 = True
            while self.判断对战中(处理对战):
                if self.debug:
                    TimeECHO(self.prefix+"尝试进入大厅:对战中,直接重启APP")
                    self.移动端.重启APP(30)
                    self.登录游戏()  # cndaqiang: debug专用
                TimeECHO(self.prefix+"尝试进入大厅:对战sleep")
                sleep(15)  # sleep太久容易死
                if self.Tool.timelimit(timekey="结束对战", limit=60*15, init=False):
                    break
            self.结束人机匹配()
        if self.判断战绩页面():
            self.结束人机匹配()
        #
        if exists(self.登录界面开始游戏图标):
            self.登录游戏()
        self.网络优化()
        # 各种异常，异常图标,比如网速不佳、画面设置、
        self.Tool.existsTHENtouch(Template(r"tpl1692951507865.png", record_pos=(-0.106, 0.12), resolution=(960, 540), threshold=0.9), "关闭画面设置")
        # 更新资源
        WIFI更新资源 = Template(r"tpl1694357134235.png", record_pos=(-0.004, -0.019), resolution=(960, 540))
        if exists(WIFI更新资源):
            self.Tool.existsTHENtouch(Template(r"tpl1694357142735.png", record_pos=(-0.097, 0.116), resolution=(960, 540)))
        if self.判断大厅中():
            return True
        # 更新图形显示设置
        显示设置 = Template(r"tpl1694359268612.png", record_pos=(-0.002, 0.12), resolution=(960, 540))
        if exists(显示设置):
            self.Tool.existsTHENtouch(Template(r"tpl1694359275922.png", record_pos=(-0.113, 0.124), resolution=(960, 540)))
        if self.判断大厅中():
            return True
        #
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        # 返回图标
        返回图标 = Template(r"tpl1692949580380.png", record_pos=(-0.458, -0.25), resolution=(960, 540), threshold=0.9)
        self.Tool.LoopTouch(返回图标, "返回图标", loop=5, savepos=False)
        if self.判断大厅中():
            return True
        self.确定按钮()
        if exists(Template(r"tpl1693886922690.png", record_pos=(-0.005, 0.114), resolution=(960, 540))):
            self.Tool.existsTHENtouch(Template(r"tpl1693886962076.png", record_pos=(0.097, 0.115), resolution=(960, 540)), "确定按钮")
        if self.判断大厅中():
            return True
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        # 邀请
        if exists(Template(r"tpl1692951548745.png", record_pos=(0.005, 0.084), resolution=(960, 540))):
            关闭邀请 = Template(r"tpl1692951558377.png", record_pos=(0.253, -0.147), resolution=(960, 540), threshold=0.9)
            self.Tool.LoopTouch(关闭邀请, "关闭邀请", loop=5, savepos=False)
        if self.判断大厅中():
            return True
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        self.移动端.重启APP()
        self.登录游戏()
        times = times+1
        #
        if self.健康系统_常用命令():
            if self.组队模式:
                return True
            return self.进入大厅(times)

        # 次数上限
        if times < 15 and times % 4 == 0:
            self.移动端.重启APP(10)
            self.登录游戏()
        if times > 15:
            if self.组队模式:
                TimeErr(self.prefix+"进入大厅times太多,创建同步文件")
                self.Tool.touch同步文件()
                return True
            else:
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                self.移动端.关闭APP()
                return False

    def 登录游戏(self, times=1):
        if times == 1:
            self.Tool.timelimit(timekey="登录游戏", limit=60*5, init=True)
        times = times+1
        if times > 5:
            TimeErr(self.prefix+"登录游戏次数太多,返回")
            return False
        TimeECHO(self.prefix+f"登录游戏{times}")
        if self.Tool.timelimit(timekey="登录游戏", limit=60*5, init=False):
            TimeErr(self.prefix+"登录游戏超时,返回")
        取消 = Template(r"tpl1697785803856.png", record_pos=(-0.099, 0.115), resolution=(960, 540))
        # 更新公告
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        更新公告 = Template(r"tpl1692946575591.png", record_pos=(0.103, -0.235), resolution=(960, 540), threshold=0.9)
        if exists(更新公告):
            for igengxin in np.arange(30):
                TimeECHO(self.prefix+"更新中%d" % (igengxin))
                关闭更新 = Template(r"tpl1693446444598.png", record_pos=(0.428, -0.205), resolution=(960, 540), threshold=0.9)
                if self.Tool.existsTHENtouch(关闭更新, "关闭更新", savepos=False):
                    sleep(10)
                    break
                if exists(Template(r"tpl1692946702006.png", record_pos=(-0.009, -0.014), resolution=(960, 540), threshold=0.9)):
                    TimeECHO(self.prefix+"更新完成")
                    touch(Template(r"tpl1692946738054.png", record_pos=(-0.002, 0.116), resolution=(960, 540), threshold=0.9))
                    sleep(60)
                    break
                elif not exists(更新公告):
                    TimeECHO(self.prefix+"找不到更新公告.break")
                    break
                if exists(Template(r"tpl1692952266315.png", record_pos=(-0.411, 0.266), resolution=(960, 540), threshold=0.9)):
                    TimeECHO(self.prefix+"正在下载资源包")
                sleep(60)
        if self.判断大厅中():
            return True
        if exists(Template(r"tpl1692946837840.png", record_pos=(-0.092, -0.166), resolution=(960, 540), threshold=0.9)):
            TimeECHO(self.prefix+"同意游戏")
            touch(Template(r"tpl1692946883784.png", record_pos=(0.092, 0.145), resolution=(960, 540), threshold=0.9))
        if self.判断大厅中():
            return True
        # 这里需要重新登录了
        if exists(Template(r"tpl1692946938717.png", record_pos=(-0.108, 0.159), resolution=(960, 540), threshold=0.9)):
            TimeECHO(self.prefix+"需要重新登录")
            if self.组队模式:
                TimeErr(self.prefix+"需要重新登录:创建同步文件")
                self.Tool.touch同步文件()
            else:
                TimeECHO(self.prefix+"需要重新登录:创建单节点同步")
                self.Tool.touchfile(self.重新登录FILE)
                if self.totalnode_bak > 1:
                    self.Tool.touchfile(self.无法进行组队FILE)
                self.移动端.重启APP(10*60)
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return True
        #
        #
        if exists(Template(r"tpl1692951324205.png", record_pos=(0.005, -0.145), resolution=(960, 540))):
            TimeECHO(self.prefix+"关闭家长莫模式")
            touch(Template(r"tpl1692951358456.png", record_pos=(0.351, -0.175), resolution=(960, 540)))
            sleep(5)
        # 现在打开可能会放一段视频，怎么跳过呢？使用0.1的精度测试一下.利用历史记录了
        随意点击 = self.登录界面开始游戏图标
        self.Tool.existsTHENtouch(随意点击, "随意点击k", savepos=True)
        self.Tool.existsTHENtouch(取消, "取消按钮")
        self.关闭按钮()
        self.Tool.existsTHENtouch(取消, "取消按钮")
        if self.判断大厅中():
            return True
        #
        if self.Tool.existsTHENtouch(self.登录界面开始游戏图标, "登录界面.开始游戏", savepos=False):
            sleep(10)
        #
        用户协议同意 = Template(r"tpl1692952132065.png", record_pos=(0.062, 0.099), resolution=(960, 540), threshold=0.9)
        self.Tool.existsTHENtouch(用户协议同意, "用户协议同意")
        #
        if self.健康系统_常用命令():
            if self.组队模式:
                return True
            return self.进入大厅()
        # 动态下载资源提示

        回归礼物 = Template(r"tpl1699607355777.png", resolution=(1136, 640))
        if exists(回归礼物):
            self.Tool.existsTHENtouch(Template(r"tpl1699607371836.png", resolution=(1136, 640)))
        回归挑战 = Template(r"tpl1699680234401.png", record_pos=(0.314, 0.12), resolution=(1136, 640))
        self.Tool.existsTHENtouch(回归挑战, "不进行回归挑战")
        if self.判断大厅中():
            return True
        #
        self.网络优化()
        # 各种异常，异常图标,比如网速不佳、画面设置、
        self.Tool.existsTHENtouch(Template(r"tpl1692951507865.png", record_pos=(-0.106, 0.12), resolution=(960, 540), threshold=0.9), "关闭画面设置")
        # 更新资源
        WIFI更新资源 = Template(r"tpl1694357134235.png", record_pos=(-0.004, -0.019), resolution=(960, 540))
        if exists(WIFI更新资源):
            self.Tool.existsTHENtouch(Template(r"tpl1694357142735.png", record_pos=(-0.097, 0.116), resolution=(960, 540)), "取消更新")
        #
        动态下载资源 = Template(r"tpl1697785792245.png", record_pos=(-0.004, -0.009), resolution=(960, 540))
        if exists(动态下载资源):
            self.Tool.existsTHENtouch(取消, "取消按钮")
        if self.判断大厅中():
            return True
        self.Tool.existsTHENtouch(取消, "取消按钮")
        # 活动界面
        self.进入大厅时遇到的复杂的关闭按钮()
        self.Tool.existsTHENtouch(取消, "取消按钮")
        if self.判断大厅中():
            return True
        #
        今日不再弹出 = Template(r"tpl1693272038809.png", record_pos=(0.38, 0.215), resolution=(960, 540), threshold=0.9)
        if exists(今日不再弹出):  # 当活动海报太大时，容易识别关闭图标错误，此时采用历史的关闭图标位置
            TimeECHO(self.prefix+"今日不再弹出仍在")
            self.Tool.existsTHENtouch(取消, "取消按钮")
            self.进入大厅时遇到的复杂的关闭按钮()
            self.网络优化()
            self.Tool.existsTHENtouch(self.登录界面开始游戏图标, "登录界面.开始游戏", savepos=False)
            if self.判断大厅中():
                return True
            else:
                sleep(10)
        #
        if self.判断大厅中():
            return True
        return self.登录游戏(times)

    def 单人进入人机匹配房间(self, times=1):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        if "ios" in self.移动端.LINK:
            配件不支持 = Template(r"tpl1701523669097.png", record_pos=(-0.001, 0.002), resolution=(1136, 640))
            关闭配件不支持 = Template(r"tpl1701523677678.png", record_pos=(-0.004, 0.051), resolution=(1136, 640))
            if exists(配件不支持):
                self.Tool.existsTHENtouch(关闭配件不支持, "关闭配件不支持")
        if "模拟战" in self.对战模式:
            TimeECHO(self.prefix+f"首先进入人机匹配房间_模拟战{times}")
            return self.单人进入人机匹配房间_模拟战(times)
        #
        TimeECHO(self.prefix+f"首先进入人机匹配房间{times}")
        if self.判断对战中():
            self.结束人机匹配()
        if self.标准触摸对战:
            TimeECHO(self.prefix+f"标准触摸对战:先进入大厅再重新进入房间")
            self.进入大厅()
        else:
            if self.判断房间中():
                return True
        self.进入大厅()
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        TimeECHO(self.prefix+"进入大厅,开始进入匹配房间")
        if times == 1:
            self.Tool.timelimit(timekey="单人进入人机匹配房间", limit=60*10, init=True)
        #
        times = times+1
        if not self.Tool.existsTHENtouch(self.大厅对战图标, "大厅对战", savepos=False):
            TimeErr(self.prefix+"找不到大厅对战图标")
            return self.单人进入人机匹配房间(times)
        #
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666019941.png", record_pos=(-0.401, 0.098), resolution=(960, 540)), "5v5王者峡谷", savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666034409.png", record_pos=(0.056, 0.087), resolution=(960, 540)), "人机", savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        # 暂时不修改 self.选择人机模式=False
        # 不在这里根据青铜段位文件判断,而是在上层调用之前设置self.青铜段位
        段位key = "青铜段位" if self.青铜段位 else "星耀段位"
        if self.选择人机模式:
            TimeECHO(self.prefix+"选择对战模式")
            匹配模式 = {}
            匹配模式["标准模式"] = Template(r"tpl1702268393125.png", record_pos=(-0.35, -0.148), resolution=(960, 540))
            匹配模式["快速模式"] = Template(r"tpl1689666057241.png", record_pos=(-0.308, -0.024), resolution=(960, 540))
            key = "快速模式"
            if self.标准模式:
                key = "标准模式"
            if self.标准触摸对战:
                key = "标准模式"
            if not self.Tool.existsTHENtouch(匹配模式[key], key):
                return self.单人进入人机匹配房间(times)
            # 选择难度
            段位图标 = {}
            段位图标["青铜段位"] = Template(r"tpl1689666083204.png", record_pos=(0.014, -0.148), resolution=(960, 540))
            段位图标["星耀段位"] = Template(r"tpl1689666092009.png", record_pos=(0.0, 0.111), resolution=(960, 540))
            self.Tool.existsTHENtouch(段位图标[段位key], "选择"+段位key, savepos=False)
        # 开始练习
        开始练习 = Template(r"tpl1689666102973.png", record_pos=(0.323, 0.161), resolution=(960, 540), threshold=0.9)
        开始练习 = Template(r"tpl1700298996343.png", record_pos=(0.326, 0.197), resolution=(1136, 640), threshold=0.9, target_pos=2)

        # 开始练习和下页的开始匹配太像了,修改一下
        if not self.Tool.existsTHENtouch(开始练习, "开始练习"):
            return self.单人进入人机匹配房间(times)
        #
        sleep(10)
        禁赛提示 = Template(r"tpl1700128026288.png", record_pos=(-0.002, 0.115), resolution=(960, 540))
        if exists(禁赛提示):
            TimeECHO(self.prefix+"禁赛提示无法进行匹配")
            self.移动端.重启APP(10)
            if self.组队模式:
                self.Tool.touch同步文件()
                return True
            else:
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return True
        #
        # 段位限制
        if not self.青铜段位:  # 其他段位有次数限制
            if self.Tool.LoopTouch(开始练习, "开始练习", loop=3):
                TimeECHO(self.prefix+":高阶段位已达上限,采用青铜模式")
                self.青铜段位 = True
                self.选择人机模式 = True
                段位key = "青铜段位"
                self.Tool.existsTHENtouch(段位图标[段位key], "选择"+段位key, savepos=False)
                self.Tool.existsTHENtouch(开始练习, "开始练习")
                self.Tool.touchfile(self.青铜段位FILE)
                if self.组队模式:
                    TimeErr(self.prefix+"段位不合适,创建同步文件")
                    self.Tool.touch同步文件()
                    return
                else:
                    return self.单人进入人机匹配房间(times)
        #
        if not self.判断房间中():
            # 有时候长时间不进去被禁赛了
            确定按钮 = Template(r"tpl1689667950453.png", record_pos=(-0.001, 0.111), resolution=(960, 540))
            while self.Tool.existsTHENtouch(确定按钮, "不匹配被禁赛的确定按钮"):
                sleep(20)
                if self.Tool.existsTHENtouch(开始练习, "开始练习"):
                    sleep(10)
                if self.Tool.timelimit(timekey="单人进入人机匹配房间", limit=60*10, init=False):
                    TimeErr(self.prefix+":单人进入人机匹配房间超时,touch同步文件")
                    if not self.组队模式:
                        self.Tool.touch同步文件(self.Tool.独立同步文件)
                    if self.组队模式:
                        self.Tool.touch同步文件()
                    return True
            return self.单人进入人机匹配房间(times)
        return True

    def 进入人机匹配房间(self):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        TimeECHO(self.prefix+"进入人机匹配房间")
        self.单人进入人机匹配房间()
        if not self.组队模式:
            return
        TimeECHO(self.prefix+"进入组队匹配房间")
        # 组队时,使用青铜模式进行, 前面应该已经配置好了青铜段位,这里进一步加强青铜段位确定
        if not "模拟战" in self.对战模式 and not self.青铜段位 and self.房主:
            TimeECHO(self.prefix+":组队模式只在青铜段位进行,房主应该使用青铜段位建房间,重建房间中")
            self.青铜段位 = True
            self.进入大厅()
            self.单人进入人机匹配房间()
        # ...............................................................
        # 当多人组队模式时，这里要暂时保证是房间中，因为邀请系统还没写好
        self.Tool.barriernode(self.mynode, self.totalnode, "组队进房间")
        if not self.房主:
            sleep(self.mynode*10)
        self.Tool.timelimit(timekey=f"组队模式进房间{self.mynode}", limit=60*5, init=True)
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        if not self.房主:
            找到取消按钮, self.房间中的取消按钮图标 = self.Tool.存在任一张图(self.房间中的取消按钮图标, "房间中的取消准备按钮")
            self.Tool.timelimit(timekey=f"辅助进房{self.mynode}", limit=60*5, init=True)
            while not 找到取消按钮:
                if self.Tool.timelimit(timekey=f"辅助进房{self.mynode}", limit=60*5, init=False):
                    TimeErr(self.prefix+"辅助进房超时退出")
                    self.Tool.touch同步文件()
                    break
                self.check_connect_status()
                if self.Tool.存在同步文件():
                    TimeErr(self.prefix+"辅助进房检测到同步文件")
                    return True
                #
                # 需要小号和主号建立亲密关系，并在主号中设置亲密关系自动进入房间
                TimeECHO(self.prefix+"不在组队的房间中")
                if not self.判断房间中():
                    self.单人进入人机匹配房间()
                # 这里给的是特殊账户的头像
                进房 = Template(r"tpl1700284839745.png", record_pos=(0.357, -0.17), resolution=(1136, 640), target_pos=9)
                if not exists(进房):
                    进房 = Template(r"tpl1699181922986.png", record_pos=(0.46, -0.15), resolution=(960, 540), threshold=0.9)
                if self.Tool.existsTHENtouch(进房):
                    取消确定 = Template(r"tpl1699712554213.png", record_pos=(0.003, 0.113), resolution=(960, 540))
                    取消 = Template(r"tpl1699712559021.png", record_pos=(-0.096, 0.115), resolution=(960, 540))
                    if exists(取消确定):
                        TimeECHO(self.prefix+"点击房间错误,返回")
                        self.Tool.existsTHENtouch(取消, "取消错误房间")
                        continue
                    self.Tool.existsTHENtouch(取消, "取消错误房间")
                    TimeECHO(self.prefix+"找到房间")
                    # 这里给的是特殊账户的头像
                    进房间 = Template(r"tpl1700284856473.png", record_pos=(0.312, -0.17), resolution=(1136, 640), target_pos=2)
                    if not exists(进房间):
                        进房间 = Template(r"tpl1699181937521.png", record_pos=(0.348, -0.194), resolution=(960, 540), threshold=0.9)
                    if self.Tool.existsTHENtouch(进房间):
                        TimeECHO(self.prefix+"尝试进入房间中")
                        sleep(10)
                        找到取消按钮, self.房间中的取消按钮图标 = self.Tool.存在任一张图(self.房间中的取消按钮图标, "房间中的取消准备按钮")
                        if not 找到取消按钮:
                            TimeECHO(self.prefix+"进入房间失败,可能是今日更新太频繁,版本不一致无法进房,需要重新登录更新")
                else:
                    TimeECHO(self.prefix+"未找到组队房间,检测主节点登录状态")

        self.Tool.barriernode(self.mynode, self.totalnode, "结束组队进房间")
        return

    def 单人进入人机匹配房间_模拟战(self, times=1):
        if self.判断对战中():
            self.结束人机匹配()
        if self.判断房间中():
            return True
        self.进入大厅()
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        TimeECHO(self.prefix+"大厅中.开始进入模拟战房间")
        if self.Tool.LoopTouch(self.大厅万象天工, "万象天工", loop=3, savepos=False):
            sleep(30)
            if self.判断大厅中():
                TimeECHO(self.prefix+"模拟战: 进入万象天工失败, 重启设备")
                self.移动端.重启APP()
                self.登录游戏()
                return self.单人进入人机匹配房间_模拟战(times)
        #
        王者模拟战图标 = Template(r"tpl1693660105012.png", record_pos=(-0.435, -0.134), resolution=(960, 540))
        任意位置继续 = Template(r"tpl1693660122898.png", record_pos=(0.001, 0.252), resolution=(960, 540))  # 多次
        任意位置继续2 = Template(r"tpl1693660165029.png", record_pos=(-0.001, 0.244), resolution=(960, 540))
        任意位置继续3 = Template(r"tpl1693660182958.png", record_pos=(-0.004, 0.25), resolution=(960, 540))
        if not self.Tool.existsTHENtouch(王者模拟战图标, "王者模拟战图标"):
            return self.单人进入人机匹配房间_模拟战(times)
        while self.Tool.existsTHENtouch(任意位置继续, "任意位置继续"):
            sleep(5)
        while self.Tool.existsTHENtouch(任意位置继续2, "任意位置继续"):
            sleep(5)
        while self.Tool.existsTHENtouch(任意位置继续3, "任意位置继续"):
            sleep(5)
    # 新手要跳过教学局,自己先跳过
        #
        进入队列失败 = Template(r"tpl1693660615126.png", record_pos=(-0.19, -0.141), resolution=(960, 540))
        确定失败 = Template(r"tpl1693660628972.png", record_pos=(-0.003, 0.118), resolution=(960, 540))
        邀请好友 = Template(r"tpl1693660666527.png", record_pos=(0.408, 0.166), resolution=(960, 540))  # 就是进入房间
        self.Tool.LoopTouch(邀请好友, "邀请好友", loop=10)
        for loop in range(30):
            if not exists(进入队列失败):
                break
            self.Tool.existsTHENtouch(确定失败)
            sleep(20)
            self.Tool.existsTHENtouch(邀请好友, "邀请好友")
        #
        if self.判断房间中():
            return True
        else:
            return self.单人进入人机匹配房间(times)

    def 进行人机匹配(self, times=1):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        if times == 1:
            self.Tool.timelimit(timekey="进行人机匹配", limit=60*10, init=True)
        times = times+1
        # 这里需要barrier一下,不然下面主节点如果提前点击领匹配,这里可能无法判断
        self.Tool.barriernode(self.mynode, self.totalnode, "人机匹配预判断房间")
        #
        self.Tool.timelimit(timekey="确认匹配", limit=60*1, init=True)
        self.Tool.timelimit(timekey="超时确认匹配", limit=60*5, init=True)
        #
        自己确定匹配 = False
        loop = 0
        自己曾经确定过匹配 = False
        找到开始按钮 = False
        找到取消按钮 = False
        # 不同活动中,开始按钮的图标不同,这里进行排序寻找
        if self.房主:
            找到开始按钮, self.房间中的开始按钮图标 = self.Tool.存在任一张图(self.房间中的开始按钮图标, "开始匹配")
            房间中的开始按钮 = self.房间中的开始按钮图标[0]
            # 记录历史上有的匹配按钮位置,历史上就执行一次
            if "房间中的开始匹配按钮" not in self.Tool.var_dict.keys():
                pos = exists(房间中的开始按钮)
                if pos:
                    self.Tool.var_dict["房间中的开始匹配按钮"] = pos
            if not 找到开始按钮:
                TimeECHO(self.prefix+f":没找到开始按钮,使用历史位置")
            self.Tool.existsTHENtouch(房间中的开始按钮, "房间中的开始匹配按钮", savepos=not 找到开始按钮)
        else:
            找到取消按钮, self.房间中的取消按钮图标 = self.Tool.存在任一张图(self.房间中的取消按钮图标, "房间中的取消准备按钮")
            房间中的取消按钮 = self.房间中的取消按钮图标[0]

        while True:
            # 如果没找到就再找一次
            if self.房主 and not 找到开始按钮:
                找到开始按钮, self.房间中的开始按钮图标 = self.Tool.存在任一张图(self.房间中的开始按钮图标, "开始匹配")
                房间中的开始按钮 = self.房间中的开始按钮图标[0]
                self.Tool.existsTHENtouch(房间中的开始按钮, "房间中的开始匹配按钮", savepos=False)
            #
            if self.Tool.timelimit(timekey="确认匹配", limit=60*1, init=False):
                TimeErr(self.prefix+"超时,队友未确认匹配或大概率程序卡死")
            if self.Tool.timelimit(timekey="超时确认匹配", limit=60*5, init=False):
                TimeErr(self.prefix+"超时太久,退出匹配")
                return False
            自己确定匹配 = self.Tool.existsTHENtouch(Template(r"tpl1689666290543.png", record_pos=(-0.001, 0.152), resolution=(960, 540), threshold=0.8), "确定匹配按钮")
            自己曾经确定过匹配 = 自己曾经确定过匹配 or 自己确定匹配
            # if 自己确定匹配: sleep(15) #自己确定匹配后给流出时间
            队友确认5v5匹配 = False
            if 自己曾经确定过匹配:
                队友确认5v5匹配 = self.Tool.existsTHENtouch(Template(r"tpl1689666324375.png", record_pos=(-0.297, -0.022), resolution=(960, 540)), "展开英雄", savepos=False)
            # exists(Template(r"tpl1689666311144.png", record_pos=(-0.394, -0.257), resolution=(960, 540), threshold=0.9))
            #
            if "模拟战" in self.对战模式:
                if 队友确认5v5匹配:
                    TimeErr(self.prefix+":模拟战误入5v5?")
                    if self.组队模式:
                        self.Tool.touch同步文件()
                    return
                队友确认匹配 = False
                if 自己曾经确定过匹配:
                    队友确认匹配 = self.判断对战中()
                if 队友确认匹配:
                    TimeECHO(self.prefix+":队友确认匹配")
                    return True  # 模拟战确定匹配后就结束了
                else:
                    TimeECHO(self.prefix+":队友未确认匹配")
                    continue
            else:
                队友确认匹配 = 队友确认5v5匹配
            if 队友确认匹配:
                break
        #
        # 选择英雄
        if self.选择英雄:
            if os.path.exists(self.重新设置英雄FILE):
                TimeECHO(self.prefix+":重新设置英雄")
                exec_insert = self.Tool.readfile(self.重新设置英雄FILE)
                for i_insert in exec_insert:
                    trim_insert = i_insert.strip()
                    if len(trim_insert) < 1:
                        continue
                    if '#' == trim_insert[0]:
                        continue
                    try:
                        exec(i_insert)
                        if "TimeE" not in i_insert:
                            TimeECHO(self.prefix+".重新设置英雄.run: "+i_insert[:-1])
                    except:
                        TimeErr(self.prefix+".重新设置英雄.Error run: "+i_insert[:-1])
            else:
                sleep(1)
                self.Tool.existsTHENtouch(self.参战英雄线路, "参战英雄线路", savepos=True)
                sleep(5)
                self.Tool.existsTHENtouch(self.参战英雄头像, "参战英雄头像", savepos=True)
                sleep(1)
            # 分路重复.png
            if exists(Template(r"tpl1689668119154.png", record_pos=(0.0, -0.156), resolution=(960, 540))):
                TimeECHO(self.prefix+"分路冲突，切换英雄")
                # 分路重复取消按钮.png
                if self.Tool.existsTHENtouch(Template(r"tpl1689668138416.png", record_pos=(-0.095, 0.191), resolution=(960, 540)), "冲突取消英雄", savepos=False):
                    # 选择备选英雄
                    self.Tool.existsTHENtouch(self.备战英雄线路, "备战英雄线路", savepos=True)
                    self.Tool.existsTHENtouch(self.备战英雄头像, "备战英雄", savepos=True)
            # 确定英雄后一般要等待队友确定，这需要时间
            sleep(5)
            #   确定
            self.Tool.existsTHENtouch(Template(r"tpl1689666339749.png", record_pos=(0.421, 0.237), resolution=(960, 540)), "确定英雄", savepos=True)  # 这里是用savepos的好处就是那个英雄的熟练度低点哪个英雄
            sleep(5)
            # 万一是房主
            self.Tool.existsTHENtouch(Template(r"tpl1689666339749.png", record_pos=(0.421, 0.237), resolution=(960, 540)), "确定阵容", savepos=True)
            sleep(5)
        # 加载游戏界面
        加载游戏界面 = Template(r"tpl1693143323624.png", record_pos=(0.003, -0.004), resolution=(960, 540))
        self.Tool.timelimit(timekey="加载游戏", limit=60*5, init=True)
        加载中 = exists(加载游戏界面)
        while True:
            加载中 = exists(加载游戏界面)
            if 加载中:
                TimeECHO(self.prefix+"加载游戏中.....")
                if self.Tool.existsTHENtouch(Template(r"tpl1689666367752.png", record_pos=(0.42, -0.001), resolution=(960, 540)), "加油按钮", savepos=False):
                    sleep(2)
            else:
                break
            if self.Tool.timelimit(timekey="加载游戏", limit=60*10, init=False):
                if self.Tool.容器优化:
                    break
                TimeECHO(self.prefix+"加载时间过长.....重启APP")
                self.移动端.重启APP(10)
                return False
        #
        关闭技能介绍1 = Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540))
        关闭技能介绍2 = Template(r"tpl1700918628072.png", record_pos=(-0.059, 0.211), resolution=(960, 540))
        self.Tool.existsTHENtouch(关闭技能介绍1, "关闭技能介绍1", savepos=False)
        self.Tool.existsTHENtouch(关闭技能介绍2, "关闭技能介绍2", savepos=False)
        #

    def 结束人机匹配(self):
        TimeECHO(self.prefix+f"开始结束人机匹配:{self.对战模式}")
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        if "模拟战" in self.对战模式:
            return self.结束人机匹配_模拟战()
        self.Tool.timelimit(timekey="结束人机匹配", limit=60*15, init=True)
        jixu = False
        返回房间按钮 = Template(r"tpl1689667226045.png", record_pos=(0.079, 0.226), resolution=(960, 540), threshold=0.9)
        while True:
            self.check_connect_status()
            if self.Tool.存在同步文件():
                return True
            if self.Tool.timelimit(timekey="结束人机匹配", limit=60*15, init=False):
                TimeErr(self.prefix+"结束人机匹配时间超时")
                if self.组队模式:
                    TimeErr(self.prefix+"结束人机匹配时间超时 and 组队touch同步文件")
                    self.Tool.touch同步文件()
                    return
                else:
                    self.Tool.touch同步文件(self.Tool.独立同步文件)
                    return
                return self.进入大厅()
            加速对战 = False
            if self.标准触摸对战:
                加速对战 = True
            if self.触摸对战:
                加速对战 = True
            if self.判断对战中(加速对战):
                jixu = False
                sleep(30)
                continue
            if self.判断房间中():
                return
            if 加速对战:
                self.判断对战中(加速对战)
            if self.判断大厅中():
                return
            if 加速对战:
                self.判断对战中(加速对战)
            每日任务进展 = Template(r"tpl1703772723321.png", record_pos=(0.004, -0.174), resolution=(960, 540))
            self.Tool.existsTHENtouch(每日任务进展, "新号每日任务进展", savepos=False)
            if 加速对战:
                self.判断对战中(加速对战)
            确定按钮 = Template(r"tpl1689667950453.png", record_pos=(-0.001, 0.111), resolution=(960, 540))
            self.Tool.existsTHENtouch(确定按钮, "回归对战的奖励确定按钮|新赛季奖励按钮", savepos=False)
            if 加速对战:
                self.判断对战中(加速对战)
            if exists(返回房间按钮):
                jixu = True
            #
            if self.健康系统_常用命令():
                if self.组队模式:
                    return True
                return self.进入大厅()
            #
            游戏结束了 = Template(r"tpl1694360304332.png", record_pos=(-0.011, -0.011), resolution=(960, 540))
            if exists(游戏结束了):
                self.Tool.existsTHENtouch(Template(r"tpl1694360310806.png", record_pos=(-0.001, 0.117), resolution=(960, 540)))
            self.check_connect_status()

            if 加速对战:
                self.判断对战中(加速对战)
            # 有时候会莫名进入分享界面
            if exists(Template(r"tpl1689667038979.png", record_pos=(0.235, -0.125), resolution=(960, 540))):
                TimeECHO(self.prefix+"分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540)))
                jixu = True
                sleep(2)
                self.确定按钮()

            # 有时候会莫名进入MVP分享界面
            pos = exists(Template(r"tpl1689727624208.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
            if pos:
                TimeECHO(self.prefix+"mvp分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540)))
                jixu = True
                sleep(2)
            #
            # 都尝试一次返回
            if self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540))):
                sleep(2)
                self.确定按钮()

            if self.Tool.existsTHENtouch(Template(r"tpl1689667161679.png", record_pos=(-0.001, 0.226), resolution=(960, 540))):
                TimeECHO(self.prefix+"MVP继续")
                jixu = True
                sleep(2)

            # 胜利页面继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689668968217.png", record_pos=(0.002, 0.226), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续1/3")
                jixu = True
                sleep(2)
            # 显示mvp继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689669015851.png", record_pos=(-0.002, 0.225), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续2/3")
                jixu = True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1689669071283.png", record_pos=(-0.001, -0.036), resolution=(960, 540))):
                TimeECHO(self.prefix+"友情积分继续2/3")
                jixu = True
                self.Tool.existsTHENtouch(Template(r"tpl1689669113076.png", record_pos=(-0.002, 0.179), resolution=(960, 540)))
                sleep(2)
            if 加速对战:
                self.判断对战中(加速对战)

            # todo, 暂时为空
            if self.Tool.existsTHENtouch(Template(r"tpl1689670032299.png", record_pos=(-0.098, 0.217), resolution=(960, 540))):
                TimeECHO(self.prefix+"超神继续3/3")
                jixu = True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1692955597109.png", record_pos=(-0.095, 0.113), resolution=(960, 540))):
                TimeECHO(self.prefix+"网络卡顿提示")
                jixu = True
                sleep(2)
            #
            self.check_connect_status()
            if self.Tool.存在同步文件():
                return True
            if 加速对战:
                self.判断对战中(加速对战)
            sleep(10)
            if not jixu:
                if self.Tool.timelimit(timekey="结束人机匹配", limit=60*2, init=False):
                    jixu = True
                TimeECHO(self.prefix+"未监测到继续,sleep...")
                sleep(20)
                continue
            # 返回大厅
            # 因为不能保证返回辅助账户返回房间，所以返回大厅更稳妥
            if self.对战结束返回房间 and not self.标准触摸对战:
                if self.Tool.existsTHENtouch(返回房间按钮, "返回房间"):
                    sleep(10)
                self.网络优化()
                if self.判断房间中():
                    return
            else:
                if self.Tool.existsTHENtouch(Template(r"tpl1689667243845.png", record_pos=(-0.082, 0.221), resolution=(960, 540), threshold=0.9), "返回大厅"):
                    sleep(10)
                    if self.Tool.existsTHENtouch(Template(r"tpl1689667256973.png", record_pos=(0.094, 0.115), resolution=(960, 540)), "确定返回大厅"):
                        sleep(10)
                if self.判断大厅中():
                    return
    #

    def 结束人机匹配_模拟战(self):
        TimeECHO(self.prefix+"准备结束本局模拟战")
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        self.Tool.timelimit(timekey="结束人机匹配", limit=60*20, init=True)
        while True:
            if self.Tool.timelimit(timekey="结束人机匹配", limit=60*30, init=False) or self.健康系统() or self.判断大厅中():
                TimeErr(self.prefix+"结束游戏时间过长 OR 健康系统 OR 大厅中")
                return self.进入大厅()
            if self.判断房间中():
                return
            点击屏幕继续 = Template(r"tpl1701229138066.png", record_pos=(-0.002, 0.226), resolution=(960, 540))
            self.Tool.existsTHENtouch(点击屏幕继续, self.prefix+"点击屏幕继续")
            if self.判断对战中(False):
                sleeploop = 0
                while self.判断对战中(True):  # 开始处理准备结束
                    sleep(10)
                    sleeploop = sleeploop+1
                    self.check_connect_status()
                    if self.Tool.存在同步文件():
                        return True
                    if sleeploop > 20:
                        break  # 虚拟机王者程序卡住了
                # ++++++滴哦
                for loop in range(30):  # 等待时间太长
                    TimeECHO(self.prefix+"等待模拟战对战结束")
                    if exists(Template(r"tpl1690545494867.png", record_pos=(0.0, 0.179), resolution=(960, 540))):
                        TimeECHO(self.prefix+"正在退出")
                        if self.Tool.existsTHENtouch(Template(r"tpl1690545545580.png", record_pos=(-0.101, 0.182), resolution=(960, 540)), "选择退出对战"):
                            TimeECHO(self.prefix+"点击退出")
                            break
                    sleep(30)
            if exists(Template(r"tpl1690545494867.png", record_pos=(0.0, 0.179), resolution=(960, 540))):
                TimeECHO(self.prefix+"检测到:[退出+观战]界面")
                self.Tool.existsTHENtouch(Template(r"tpl1690545545580.png", record_pos=(-0.101, 0.182), resolution=(960, 540)), "选择退出对战")
            if self.判断房间中():
                return
            if self.判断大厅中():
                return

            if self.Tool.existsTHENtouch(Template(r"tpl1690545762580.png", record_pos=(-0.001, 0.233), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续1")
                jixu = True
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1690545802859.png", record_pos=(0.047, 0.124), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续2")
                jixu = True
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1690545854354.png", record_pos=(0.002, 0.227), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续3")
                jixu = True
                sleep(5)
            #
            # 因为不能保证返回辅助账户返回房间，所以返回大厅更稳妥
            if exists(Template(r"tpl1690545925867.png", record_pos=(-0.001, 0.241), resolution=(960, 540))):
                if self.对战结束返回房间:
                    if self.Tool.existsTHENtouch(Template(r"tpl1690545951270.png", record_pos=(0.075, 0.239), resolution=(960, 540)), "返回房间", savepos=True):
                        sleep(10)
    # @todo ,添加barrier
                        if self.判断房间中():
                            break
            if self.判断房间中():
                return
            if self.判断大厅中():
                return
    #

    def 每日礼包(self):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
            #
        if os.path.exists(self.免费商城礼包FILE):
            if self.商城免费礼包():
                self.Tool.removefile(self.免费商城礼包FILE)
        #
        if self.Tool.timelimit("领游戏礼包", limit=60*60*3, init=False):
            self.移动端.打开APP()
            #
            self.每日礼包_每日任务()
            self.玉镖夺魁签到 = os.path.exists("玉镖夺魁签到.txt")
            if self.玉镖夺魁签到:
                self.玉镖夺魁()
            else:
                TimeECHO(self.prefix+"暂时不进行玉镖夺魁")
            # 友情礼包、邮件礼包、战队礼包不领取不会丢失,影响不大,最后领取
            self.每日礼包_邮件礼包()
            self.每日礼包_妲己礼物()
            self.友情礼包()
            self.战队礼包()
            TimeECHO(self.prefix+"钻石夺宝、战令(动画多,很卡)没有代码需求,攒够了一起转")
            if self.Tool.存在同步文件():
                return True
            self.进入大厅()
        else:
            TimeECHO(self.prefix+"时间太短,暂时不领取游戏礼包")
        if self.王者营地礼包 and not self.组队模式:  # 组队时不打开王者营地,不同的节点进度不同
            self.每日礼包_王者营地()

        self.Tool.timelimit("领游戏礼包", limit=60*60*3, init=False)

    def 战队礼包(self):
        self.进入大厅()
        #
        # 战队礼包
        TimeECHO(self.prefix+f":战队礼包")
        self.Tool.existsTHENtouch(Template(r"tpl1700403158264.png", record_pos=(0.067, 0.241), resolution=(960, 540)), "战队")
        sleep(10)
        self.Tool.existsTHENtouch(Template(r"tpl1700403166845.png", record_pos=(0.306, 0.228), resolution=(960, 540)), "展开战队")
        sleep(10)
        if not self.Tool.existsTHENtouch(Template(r"tpl1700403174640.png", record_pos=(0.079, 0.236), resolution=(960, 540)), "战队商店"):
            TimeECHO(self.prefix+"找不到战队商店, 可能没有加战队, 返回")
        sleep(10)
        self.Tool.existsTHENtouch(Template(r"tpl1700403186636.png", record_pos=(0.158, -0.075), resolution=(960, 540), target_pos=8), "英雄碎片")
        sleep(10)
        self.Tool.existsTHENtouch(Template(r"tpl1700403207652.png", record_pos=(0.092, 0.142), resolution=(960, 540)), "领取")
        sleep(10)
        self.Tool.existsTHENtouch(Template(r"tpl1700403218837.png", record_pos=(0.098, 0.117), resolution=(960, 540)), "确定")
        sleep(10)
        return
    # @todo,其他活动一键领取

    def 商城免费礼包(self, times=1):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        if times > 10:
            return False
        #
        self.进入大厅()
        if times == 1:
            self.Tool.timelimit(timekey="领商城免费礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领商城免费礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领商城免费礼包超时")
                return False
        #
        times = times+1
        #
        # 商城免费礼包
        TimeECHO(self.prefix+f"领任务礼包:每日任务{times}")
        if self.健康系统():
            return False
        #
        TimeECHO(self.prefix+f":商城免费礼包")
        # 做活动时，商城入口会变
        商城入口 = []
        商城入口.append(Template(r"tpl1705069544018.png", record_pos=(0.465, -0.173), resolution=(960, 540)))
        商城入口.append(Template(r"tpl1705718545013.png", target_pos=2, record_pos=(0.461, -0.115), resolution=(960, 540)))
        特惠入口 = Template(r"tpl1705069563125.png", record_pos=(-0.43, 0.14), resolution=(960, 540))
        免费图标 = Template(r"tpl1705069610816.png", record_pos=(0.165, -0.159), resolution=(960, 540))
        免费购买 = Template(r"tpl1705069621203.png", record_pos=(0.244, 0.244), resolution=(960, 540), threshold=0.95)
        免费点券 = Template(r"tpl1705069633600.png", record_pos=(-0.004, 0.142), resolution=(960, 540))
        确定购买 = Template(r"tpl1705069645193.png", record_pos=(-0.105, 0.165), resolution=(960, 540))
        商城界面 = []
        商城界面.append(免费图标)
        商城界面.append(免费购买)
        商城界面.append(Template(r"tpl1705070445445.png", record_pos=(0.464, -0.04), resolution=(960, 540)))
        商城界面.append(Template(r"tpl1705070628028.png", record_pos=(0.15, -0.003), resolution=(960, 540)))
        返回 = Template(r"tpl1694442171115.png", record_pos=(-0.441, -0.252), resolution=(960, 540))
        #
        找到商城入口 = False
        for i in range(len(商城入口)):
            TimeECHO(self.prefix+f"寻找商城入口{i}")
            找到商城入口 = self.Tool.existsTHENtouch(商城入口[i], "商城入口", savepos=True)
            if 找到商城入口:
                break
        if not 找到商城入口:
            TimeECHO(self.prefix+f"无法找到商城入口")
            return self.商城免费礼包(times=times)
        sleep(30)
        进入商城界面 = False
        for i in range(len(商城界面)):
            self.Tool.existsTHENtouch(特惠入口, f"点击特惠入口", savepos=True)
            sleep(20)
            TimeECHO(self.prefix+f"检测商城界面中...{i}")
            if exists(商城界面[i]):
                进入商城界面 = True
                break
        if self.健康系统():
            return False
        if not 进入商城界面:
            TimeECHO(self.prefix+f"未检测到商城界面, 重新进入商城")
            self.Tool.LoopTouch(返回, "返回")
            if "商城入口" in self.Tool.var_dict.keys():
                del self.Tool.var_dict["商城入口"]
            if "特惠入口" in self.Tool.var_dict.keys():
                del self.Tool.var_dict["特惠入口"]
            return self.商城免费礼包(times=times)
        #
        if not self.Tool.existsTHENtouch(免费图标, "免费礼包的图标"):
            TimeECHO(self.prefix+f"没检测到免费图标,可能领取过了")
            self.Tool.LoopTouch(返回, "返回")
            return True

        领取成功 = False
        if self.Tool.existsTHENtouch(免费购买, "免费购买", savepos=False):
            sleep(5)
            领取成功 = self.Tool.existsTHENtouch(免费点券, "免费点券", savepos=False)
            sleep(10)
            self.Tool.LoopTouch(确定购买, "确定购买")
            self.关闭按钮()
            self.Tool.LoopTouch(返回, "返回")
            self.确定按钮()
        if not 领取成功:
            TimeECHO(self.prefix+f"领取每日礼包失败")
        return True

    def 玉镖夺魁(self, times=1):
        self.进入大厅()
        #
        # 玉镖夺魁
        TimeECHO(self.prefix+f":玉镖夺魁{times}")
        #
        if times > 10:
            return False
        #
        if times == 1:
            self.Tool.timelimit(timekey="玉镖夺魁", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="玉镖夺魁", limit=60*5, init=False):
                TimeECHO(self.prefix+f"玉镖夺魁{times}超时退出")
                return False
        #
        times = times+1
        #
        # 开始寻找入口
        图标 = Template(r"tpl1700803051511.png", record_pos=(0.379, -0.172), resolution=(960, 540))
        if self.Tool.existsTHENtouch(图标, "玉镖夺魁"):
            TimeECHO(self.prefix+"从大厅进入玉镖夺魁")
        else:
            TimeECHO("找不到玉镖夺魁图标:尝试切换入口")
            活动图标 = Template(r"tpl1701428211463.png", record_pos=(0.463, -0.089), resolution=(960, 540))
            礼包图标 = Template(r"tpl1701428223494.png", record_pos=(-0.442, -0.101), resolution=(960, 540))
            夺镖活动 = Template(r"tpl1701428233468.png", record_pos=(-0.354, 0.16), resolution=(960, 540))
            参与按钮 = Template(r"tpl1701428241862.png", record_pos=(0.08, 0.216), resolution=(960, 540))
            if not self.Tool.existsTHENtouch(活动图标, "夺魁_活动图标"):
                TimeECHO("找不到活动图标:重新夺魁")
                return self.玉镖夺魁(times)
            sleep(5)
            if not self.Tool.existsTHENtouch(礼包图标, "夺魁_礼包图标"):
                TimeECHO("找不到礼包图标:重新夺魁")
                return self.玉镖夺魁(times)
            sleep(5)
            #
            夺镖位置 = []
            夺镖位置.append(Template(r"tpl1704087360602.png", record_pos=(-0.403, 0.116), resolution=(960, 540), target_pos=6))
            夺镖位置.append(Template(r"tpl1704087510800.png", record_pos=(-0.4, -0.099), resolution=(960, 540), target_pos=6))
            夺镖位置.append(Template(r"tpl1704087522398.png", record_pos=(-0.397, -0.024), resolution=(960, 540), target_pos=6))
            pos = False
            for 夺镖位置_i in range(len(夺镖位置)):
                pos = exists(夺镖位置[夺镖位置_i])
                if pos:
                    TimeECHO(self.prefix+f"找到活动滑动按钮{夺镖位置_i}")
                    break
                else:
                    TimeECHO(self.prefix+f"寻找活动滑动按钮中{夺镖位置_i}")
            if not pos:
                return self.玉镖夺魁(times)
            参与位置 = False
            for i in range(10):
                sleep(1)
                TimeECHO(self.prefix+f"寻找参与投镖按钮中{i}")
                trypos = exists(参与按钮)
                if self.Tool.existsTHENtouch(夺镖活动, "夺镖活动入口"):
                    TimeECHO(self.prefix+f"找到夺镖活动页面,寻找投镖入口")
                    参与位置 = exists(参与按钮)
                if trypos:
                    参与位置 = trypos
                if 参与位置:
                    break
                TimeECHO(self.prefix+f"滑动页面寻找......")
                swipe(pos, vector=[0.0, -0.5])
            #
            if not 参与位置:
                TimeECHO(self.prefix+"没找到夺镖活动入口")
                return self.玉镖夺魁(times)
            else:
                touch(参与位置)
        TimeECHO(self.prefix+"开始签到夺标")
        #
        领取加号 = []
        领取加号.append(Template(r"tpl1700803174309.png", record_pos=(0.227, -0.21), resolution=(960, 540), target_pos=2))
        领取加号.append(Template(r"tpl1700803136907.png", record_pos=(0.24, -0.243), resolution=(960, 540), target_pos=4))
        for i in 领取加号:
            if self.Tool.existsTHENtouch(i, f"领取加号{i}"):
                break
        领取按钮 = Template(r"tpl1700803185294.png", record_pos=(0.172, -0.067), resolution=(960, 540))
        self.Tool.existsTHENtouch(领取按钮, "领取按钮")
        self.Tool.existsTHENtouch(Template(r"tpl1700803983736.png", record_pos=(0.015, 0.101), resolution=(960, 540)), "确定")
        self.Tool.existsTHENtouch(领取按钮, "领取按钮")
        self.Tool.existsTHENtouch(Template(r"tpl1700803983736.png", record_pos=(0.015, 0.101), resolution=(960, 540)), "确定")
        self.Tool.existsTHENtouch(Template(r"tpl1700803191090.png", record_pos=(0.372, -0.184), resolution=(960, 540)))
        return

    def 友情礼包(self):
        self.进入大厅()
        #
        # 友情礼包,虽然每次只领取了一个,但是每周/日领取了多次,一周内是可以领完上限的
        TimeECHO(self.prefix+f":友情礼包")
        TimeECHO(self.prefix+f":对战友情币")
        if not self.Tool.existsTHENtouch(Template(r"tpl1700454802287.png", record_pos=(0.242, -0.251), resolution=(960, 540)), "友情双人入口"):
            return
            sleep(5)
        if not self.Tool.existsTHENtouch(Template(r"tpl1700454817255.png", record_pos=(-0.447, 0.166), resolution=(960, 540)), "友情文字入口"):
            return
            sleep(5)
        self.Tool.existsTHENtouch(Template(r"tpl1700454833319.png", record_pos=(0.416, 0.011), resolution=(960, 540)), "多次任务领取")
        self.Tool.existsTHENtouch(Template(r"tpl1700454842665.png", record_pos=(0.001, 0.163), resolution=(960, 540)), "确定领取友情币")
        # 奖励兑换
        if not self.Tool.existsTHENtouch(Template(r"tpl1700454852769.png", record_pos=(-0.332, 0.191), resolution=(960, 540)), "奖励兑换按钮"):
            return
            sleep(5)
        # 积分
        if self.Tool.existsTHENtouch(Template(r"tpl1700454863912.png", record_pos=(-0.124, -0.004), resolution=(960, 540)), "积分夺宝券"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454872767.png", record_pos=(0.32, 0.228), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454883635.png", record_pos=(0.098, 0.118), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454897119.png", record_pos=(0.0, 0.164), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
        # 碎片
        if self.Tool.existsTHENtouch(Template(r"tpl1700454908937.png", record_pos=(0.039, 0.004), resolution=(960, 540)), "皮肤碎片兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454916324.png", record_pos=(0.317, 0.226), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454883635.png", record_pos=(0.098, 0.118), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454897119.png", record_pos=(0.0, 0.164), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
        # 碎片
        if self.Tool.existsTHENtouch(Template(r"tpl1700454935340.png", record_pos=(-0.28, 0.153), resolution=(960, 540)), "英雄碎片兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454947514.png", record_pos=(0.321, 0.227), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454883635.png", record_pos=(0.098, 0.118), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454897119.png", record_pos=(0.0, 0.164), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
        # 铭文
        if self.Tool.existsTHENtouch(Template(r"tpl1700455034567.png", record_pos=(-0.123, 0.155), resolution=(960, 540)), "铭文碎片兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700455039770.png", record_pos=(0.321, 0.226), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454883635.png", record_pos=(0.098, 0.118), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454897119.png", record_pos=(0.0, 0.164), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
        # 包箱
        if self.Tool.existsTHENtouch(Template(r"tpl1700454970340.png", record_pos=(-0.12, -0.154), resolution=(960, 540)), "友情皮肤礼包兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454978914.png", record_pos=(0.32, 0.228), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454987098.png", record_pos=(0.1, 0.117), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454996867.png", record_pos=(-0.099, 0.166), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)

    def 每日礼包_王者营地(self):
        TimeECHO(self.prefix+"王者营地礼包开始")
        if not self.check_connect_status():
            TimeErr(self.prefix+"无法连接设备.暂时不领取营地礼包")
            return
        if not self.Tool.timelimit("领营地礼包", limit=60*60*3, init=False):
            TimeECHO(self.prefix+"时间太短,暂时不领取营地礼包")
            return
        self.移动端.关闭APP()
        if "ios" in self.移动端.设备类型:
            APPID = "com.tencent.smobagamehelper"
        elif "android" in self.移动端.设备类型:
            APPID = "com.tencent.gamehelper.smoba"
        else:
            TimeErr(self.prefix+":无法判断设备类型")
            return
        王者营地 = wzyd_libao(prefix=str(self.mynode), APPID=APPID)
        try:
            王者营地.RUN()
            TimeECHO(self.prefix+"王者营地礼包领取成功")
        except:
            TimeErr(self.prefix+"王者营地礼包领取失败")
        stop_app(APPID)  # 杀掉后台,提高王者、WDA活性
        self.移动端.打开APP()
        self.Tool.timelimit("领营地礼包", limit=60*60*3, init=False)

    def 每日礼包_每日任务(self, times=1, 战令领取=True):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10:
            return False
        #
        times = times+1
        #
        # 每日任务
        TimeECHO(self.prefix+f"领任务礼包:每日任务{times}")
        # @todo, 用抢先服确定这里没有问题
        战令入口 = Template(r"tpl1703756544792.png", record_pos=(0.461, -0.017), resolution=(960, 540))
        赛季任务界面 = []
        赛季任务界面.append(Template(r"tpl1703756264588.png", record_pos=(-0.407, -0.255), resolution=(960, 540)))
        赛季任务界面.append(Template(r"tpl1703756272809.png", record_pos=(0.373, 0.11), resolution=(960, 540)))
        赛季任务界面.append(Template(r"tpl1703755615130.png", record_pos=(-0.453, -0.058), resolution=(960, 540)))
        赛季任务界面.append(Template(r"tpl1706543181534.png", record_pos=(0.373, 0.173), resolution=(960, 540)))
        赛季任务界面.append(Template(r"tpl1706543217077.png", record_pos=(-0.255, 0.174), resolution=(960, 540)))
        赛季任务界面.append(Template(r"tpl1706543240746.png", record_pos=(0.352, 0.183), resolution=(960, 540)))
        任务 = Template(r"tpl1703755622899.png", record_pos=(-0.448, -0.027), resolution=(960, 540))
        任务列表 = Template(r"tpl1703757152809.png", record_pos=(-0.173, -0.18), resolution=(960, 540))
        确定按钮 = Template(r"tpl1693194657793.png", record_pos=(0.001, 0.164), resolution=(960, 540))
        self.进入大厅()
        self.Tool.existsTHENtouch(战令入口, "战令入口", savepos=True)
        sleep(10)
        进入战令界面 = False
        for i in range(len(赛季任务界面)):
            if exists(赛季任务界面[i]):
                TimeECHO(self.prefix+f"检测到战令界面")
                进入战令界面 = True
                break
            sleep(4)
        if not 进入战令界面 and times > 2:
            进入战令界面 = not self.判断大厅中()

        if not 进入战令界面:
            TimeECHO(self.prefix+f"未检测到战令界面, 重新进入领任务礼包")
            if "战令入口" in self.Tool.var_dict.keys():
                del self.Tool.var_dict["战令入口"]
            return self.每日礼包_每日任务(times=times, 战令领取=战令领取)
        #
        if 战令领取:
            TimeECHO(self.prefix+f"领取战令奖励测试中")
            战令一键领取 = Template(r"tpl1703765448167.png", record_pos=(0.293, 0.11), resolution=(960, 540), target_pos=6)
            if self.Tool.existsTHENtouch(战令一键领取, "战令一键领取", savepos=False):
                self.Tool.LoopTouch(确定按钮, "确定按钮")
                self.关闭按钮()
                self.确定按钮()
        # 正常每日礼包
        一键领取 = Template(r"tpl1693193500142.png", record_pos=(0.391, 0.224), resolution=(960, 540))
        # 新图标
        今日活跃 = Template(r"tpl1703758748236.png", record_pos=(-0.239, 0.233), resolution=(960, 540))
        本周活跃1 = Template(r"tpl1703758755430.png", record_pos=(-0.075, 0.232), resolution=(960, 540))
        本周活跃2 = Template(r"tpl1703758760425.png", record_pos=(-0.015, 0.232), resolution=(960, 540))
        #
        返回 = Template(r"tpl1694442171115.png", record_pos=(-0.441, -0.252), resolution=(960, 540))
        # 开始切换到任务界面,但是可能比较卡,要等
        进入任务界面 = False
        for i in range(60):
            self.Tool.existsTHENtouch(任务, "战令的每日任务", savepos=True)
            if exists(任务列表):
                进入任务界面 = True
                break
            if exists(一键领取):
                进入任务界面 = True
                break
            sleep(5)
            if self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if not 进入任务界面:
            TimeECHO(self.prefix+f"未检测到任务界面, 重新进入领任务礼包")
            if "战令的每日任务" in self.Tool.var_dict.keys():
                del self.Tool.var_dict["战令的每日任务"]
            return self.每日礼包_每日任务(times=times-1, 战令领取=战令领取)
        #
        # 开始正式领取
        if self.Tool.existsTHENtouch(一键领取, "一键领取 "):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        # 这几个活跃，暂时没有找到位置，不确定是没发光的原因，还是图标变化
        if self.Tool.existsTHENtouch(今日活跃, "今日活跃 "):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        if self.Tool.existsTHENtouch(本周活跃1, "本周活跃1"):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        if self.Tool.existsTHENtouch(本周活跃2, "本周活跃2"):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        #
        self.Tool.LoopTouch(确定按钮, "确定按钮")
        self.关闭按钮()
        self.确定按钮()
        #
        # 新赛季增加的领取入口
        本周任务 = Template(r"tpl1703755716888.png", record_pos=(-0.175, -0.192), resolution=(960, 540))
        本周签到 = Template(r"tpl1703755733895.png", record_pos=(0.244, 0.228), resolution=(960, 540))
        确定签到 = Template(r"tpl1703755744366.png", record_pos=(-0.001, 0.165), resolution=(960, 540))
        if self.Tool.existsTHENtouch(本周任务, "本周任务礼包", savepos=True):
            sleep(5)
            if self.Tool.existsTHENtouch(本周签到, "本周战令签到", savepos=False):
                self.Tool.LoopTouch(确定签到, "确定签到战令")
            if self.Tool.existsTHENtouch(一键领取, "一键领取 "):
                self.Tool.existsTHENtouch(确定按钮, "确定")
                sleep(5)
            self.Tool.LoopTouch(确定按钮, "确定按钮")
            self.关闭按钮()
            self.确定按钮()
        本期任务 = Template(r"tpl1703755722682.png", record_pos=(-0.068, -0.192), resolution=(960, 540))
        if self.Tool.existsTHENtouch(本期任务, "本期任务礼包", savepos=True):
            sleep(5)
            if self.Tool.existsTHENtouch(一键领取, "一键领取 "):
                self.Tool.existsTHENtouch(确定按钮, "确定")
                sleep(5)
            self.Tool.LoopTouch(确定按钮, "确定按钮")
            self.关闭按钮()
            self.确定按钮()
        #
        self.Tool.LoopTouch(返回, "返回")
        self.确定按钮()
        return True

    def 每日礼包_邮件礼包(self, times=1):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领邮件礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领邮件礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10:
            return False
        #
        times = times+1
        self.进入大厅()
        TimeECHO(self.prefix+f"领任务礼包:领邮件礼包{times}")
        邮件图标 = Template(r"tpl1694441018032.png", record_pos=(0.35, -0.251), resolution=(960, 540))
        好友邮件 = Template(r"tpl1694441042380.png", record_pos=(-0.453, -0.188), resolution=(960, 540))
        收到邮件 = Template(r"tpl1694441057562.png", record_pos=(-0.31, -0.199), resolution=(960, 540))
        快速领取 = Template(r"tpl1694441070767.png", record_pos=(0.385, 0.23), resolution=(960, 540))
        下次吧 = Template(r"tpl1694443587766.png", record_pos=(-0.097, 0.118), resolution=(960, 540))
        金币确定 = Template(r"tpl1694443607846.png", record_pos=(0.002, 0.167), resolution=(960, 540))
        点击屏幕继续 = Template(r"tpl1694487484286.png", record_pos=(-0.006, 0.237), resolution=(960, 540))
        友情确定 = Template(r"tpl1694487498294.png", record_pos=(-0.097, 0.24), resolution=(960, 540))
        系统邮件 = Template(r"tpl1694441115819.png", record_pos=(-0.446, -0.127), resolution=(960, 540))
        系统快速领取 = Template(r"tpl1694451260084.png", record_pos=(0.415, 0.236), resolution=(960, 540))
        解锁语音界面 = Template(r"tpl1694441160296.png", record_pos=(-0.01, -0.015), resolution=(960, 540))
        我知道了 = Template(r"tpl1694441175302.png", record_pos=(-0.1, 0.116), resolution=(960, 540))
        系统礼物确定 = Template(r"tpl1694441190629.png", record_pos=(0.0, 0.165), resolution=(960, 540))
        黄色礼物确定 = Template(r"tpl1694441373245.png", record_pos=(-0.002, 0.116), resolution=(960, 540))
        系统礼物关闭 = Template(r"tpl1699626801240.png", record_pos=(0.34, -0.205), resolution=(960, 540))
        下次再选 = Template(r"tpl1704542576626.png", record_pos=(-0.099, 0.182), resolution=(960, 540))

        返回 = Template(r"tpl1694442171115.png", record_pos=(-0.441, -0.252), resolution=(960, 540))
        self.Tool.existsTHENtouch(邮件图标)
        if not exists(好友邮件):
            if not self.判断大厅中():
                self.进入大厅()
            if self.Tool.existsTHENtouch(邮件图标, "邮件图标"):
                sleep(10)
            if not exists(好友邮件):
                return self.每日礼包_邮件礼包(times)
        #
        if self.Tool.existsTHENtouch(好友邮件):
            self.Tool.existsTHENtouch(收到邮件, "收到邮件", savepos=False)
            self.Tool.existsTHENtouch(快速领取, "快速领取", savepos=False)
            # 缺少确定
            self.Tool.LoopTouch(下次吧, "下次吧", loop=10)
            self.Tool.existsTHENtouch(金币确定, "金币确定")
            self.Tool.existsTHENtouch(点击屏幕继续, "点击屏幕继续")
            self.Tool.existsTHENtouch(友情确定, "友情确定")
            #
        if self.Tool.existsTHENtouch(系统邮件):
            sleep(5)
            self.Tool.LoopTouch(系统礼物关闭, "系统礼物关闭", loop=5)
            self.Tool.existsTHENtouch(系统快速领取, "系统快速领取", savepos=False)
            self.Tool.LoopTouch(系统礼物关闭, "系统礼物关闭", loop=5)
            self.Tool.LoopTouch(黄色礼物确定, "黄色礼物确定", loop=10)
            self.Tool.existsTHENtouch(下次再选, "下次再选礼物")
            self.Tool.LoopTouch(系统礼物关闭, "系统礼物关闭", loop=5)
            while self.Tool.existsTHENtouch(系统礼物确定, "系统礼物确定"):
                if exists(解锁语音界面):
                    self.Tool.existsTHENtouch(我知道了, "我知道了")
                self.Tool.LoopTouch(系统礼物关闭, "系统礼物关闭", loop=5)
                self.Tool.LoopTouch(黄色礼物确定, "黄色礼物确定", loop=10)
                self.Tool.existsTHENtouch(下次再选, "下次再选礼物")
                self.Tool.existsTHENtouch(系统礼物关闭, "系统礼物关闭", savepos=False)
                if self.Tool.timelimit(timekey="领邮件礼包", limit=60*5, init=False):
                    TimeECHO(self.prefix+"领邮件礼包超时.....")
                    return self.每日礼包_邮件礼包(times)
            self.Tool.LoopTouch(系统礼物确定, "系统礼物确定", loop=10)

        self.Tool.LoopTouch(返回, "返回")
        return True

        # 妲己礼物
    def 每日礼包_妲己礼物(self, times=1):
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10:
            return False
        #
        times = times+1
        self.进入大厅()
        TimeECHO(self.prefix+f"领任务礼包:小妲己礼物{times}")
        # 小妲己的图标会变化
        妲己图标 = []
        妲己图标.append(Template(r"tpl1694441259292.png", record_pos=(0.458, 0.21), resolution=(960, 540)))
        妲己图标.append(Template(r"tpl1703297029482.png", record_pos=(0.451, 0.207), resolution=(960, 540)))
        一键领奖 = Template(r"tpl1694442066106.png", record_pos=(-0.134, 0.033), resolution=(960, 540))
        去领取 = Template(r"tpl1694442088041.png", record_pos=(-0.135, 0.107), resolution=(960, 540))
        收下 = Template(r"tpl1694442103573.png", record_pos=(-0.006, 0.181), resolution=(960, 540))
        确定 = Template(r"tpl1694442122665.png", record_pos=(-0.003, 0.165), resolution=(960, 540))
        返回 = Template(r"tpl1694442136196.png", record_pos=(-0.445, -0.251), resolution=(960, 540))
        能力测试关闭 = Template(r"tpl1699626801240.png", record_pos=(0.34, -0.205), resolution=(960, 540))
        #
        进入成功 = False
        for i in range(len(妲己图标)):
            if not self.判断大厅中():
                self.进入大厅()
            进入成功 = self.Tool.existsTHENtouch(妲己图标[i], f"妲己图标{i}")
            if 进入成功:
                break
        if not 进入成功:
            return self.每日礼包_妲己礼物(times)
        #
        if exists(一键领奖):
            self.Tool.existsTHENtouch(去领取, "去领取")
            self.Tool.LoopTouch(收下, "收下", loop=10)
            self.Tool.LoopTouch(确定, "确定", loop=10)
            self.Tool.LoopTouch(收下, "收下", loop=10)
        self.Tool.existsTHENtouch(能力测试关闭, "能力测试关闭")
        self.Tool.LoopTouch(返回, "返回")
        self.确定按钮()
        return True
    #

    def 六国远征_界面判断(self):
        六国界面图 = Template(r"tpl1703206627245.png", record_pos=(-0.379, -0.255), resolution=(960, 540))
        六国商店入口 = Template(r"tpl1703207698623.png", record_pos=(-0.287, 0.219), resolution=(960, 540))
        平台1 = Template(r"tpl1703206581622.png", record_pos=(-0.298, -0.131), resolution=(960, 540))
        if exists(六国界面图):
            return True
        if exists(六国商店入口):
            return True
        if exists(平台1):
            return True
        return False

    def 六国远征_进入界面(self, times=1):
        # 成功返回True,各种失败返回False
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return False
        if self.六国远征_界面判断():
            return True
        TimeECHO(self.prefix+":六国远征_进入界面")
        #
        if times == 1:
            self.Tool.timelimit(timekey="六国远征_进入界面", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="六国远征_进入界面", limit=60*5, init=False):
                TimeErr(self.prefix+"六国远征_进入界面超时")
                return False
        if times > 10:
            return False
        #
        times = times+1
        TimeECHO(self.prefix+":六国远征_准备从大厅重新进入六国界面")
        self.进入大厅()
        万象天工 = Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540))
        if not self.Tool.existsTHENtouch(万象天工, "万象天工"):
            TimeErr(self.prefix+":六国:找不到万象天工")
            self.六国远征_进入界面(times)
        sleep(2)
        冒险玩法 = Template(r"tpl1703206553221.png", record_pos=(-0.433, -0.132), resolution=(960, 540))
        六国远征入口 = Template(r"tpl1703206565024.png", record_pos=(0.152, -0.027), resolution=(960, 540))
        if not self.Tool.existsTHENtouch(冒险玩法, "冒险玩法"):
            TimeErr(self.prefix+":六国:找不到冒险玩法")
            self.六国远征_进入界面(times)
        sleep(2)
        if not self.Tool.existsTHENtouch(六国远征入口, "六国远征入口"):
            TimeErr(self.prefix+":六国:找不到六国远征界面")
            self.六国远征_进入界面(times)
        sleep(2)
        if not self.六国远征_界面判断():
            return self.六国远征_进入界面(times)
        return True

    def 六国远征_重置次数(self):  # 成功返回True,各种失败返回False
        if self.Tool.存在同步文件():
            return False
        if not self.六国远征_进入界面():
            TimeECHO(self.prefix+":无法进行六国远征模式,重置次数失败")
            return False
        #
        重置次数 = Template(r"tpl1703207708968.png", record_pos=(0.001, 0.22), resolution=(960, 540))
        黄色确定 = Template(r"tpl1703207718965.png", record_pos=(0.095, 0.117), resolution=(960, 540))
        关卡 = []
        关卡.append(Template(r"tpl1703208015389.png", record_pos=(0.191, -0.163), resolution=(960, 540), threshold=0.9))
        #
        TimeECHO(self.prefix+":六国远征.准备重置次数")
        if self.Tool.existsTHENtouch(重置次数, "重置次数", savepos=False):
            sleep(5)
            self.Tool.existsTHENtouch(黄色确定, "确定重置", savepos=False)
            sleep(5)
            if not exists(关卡[-1]):
                TimeECHO(self.prefix+":重置成功")
                return True
            else:
                TimeECHO(self.prefix+f":找到{关卡[-1]},重置失败")
                return False
        else:
            TimeECHO(self.prefix+":找不到重置按钮")
            return False

    # 进入界面后再Call,这里默认已经进入界面了,不再进行重复检测
    def 六国远征_自动探索(self, times=1):
        if self.Tool.存在同步文件():
            return False
        自动探索 = Template(r"tpl1703206610423.png", record_pos=(0.284, 0.22), resolution=(960, 540), threshold=0.9)
        任务完成 = Template(r"tpl1703207598362.png", record_pos=(0.083, -0.176), resolution=(960, 540), threshold=0.9)
        任务完成0 = Template(r"tpl1703207566167.png", record_pos=(-0.014, -0.156), resolution=(960, 540))
        蓝色确定 = Template(r"tpl1703207573159.png", record_pos=(-0.002, 0.163), resolution=(960, 540))
        黄色确定 = Template(r"tpl1703207718965.png", record_pos=(0.095, 0.117), resolution=(960, 540))
        挑战按钮 = Template(r"tpl1703343022624.png", record_pos=(0.221, 0.201), resolution=(960, 540))
        # 每日首通的图标,只显示一次
        关卡 = []
        关卡.append(Template(r"tpl1703206581622.png", record_pos=(-0.298, -0.131), resolution=(960, 540), threshold=0.9))
        关卡.append(Template(r"tpl1703206592623.png", record_pos=(-0.056, -0.212), resolution=(960, 540), threshold=0.9))
        关卡.append(Template(r"tpl1703207999598.png", record_pos=(-0.111, 0.027), resolution=(960, 540), threshold=0.9))
        关卡.append(Template(r"tpl1703208004794.png", record_pos=(0.077, -0.032), resolution=(960, 540), threshold=0.9))
        关卡.append(Template(r"tpl1703208010005.png", record_pos=(0.306, 0.032), resolution=(960, 540), threshold=0.9))
        关卡.append(Template(r"tpl1703208015389.png", record_pos=(0.191, -0.163), resolution=(960, 540), threshold=0.9))
        #
        if not self.六国远征_界面判断():
            TimeErr(self.prefix+":六国_自动探索:找不到六国远征界面")
            return False
        #
        #
        # 正式开始探索,基本上10分钟才能完成一轮，所以这个时间就取50
        if times == 1:
            self.Tool.timelimit(timekey="六国远征_闯关计时", limit=60*50, init=True)
        # 是因为容易卡住,所以设置这个上限,在一段时间内必须能检测到界面
        self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
        times = times+1
        if times > 2:
            TimeErr(self.prefix+":六国_自动探索:次数太多,放弃")
            return False
        while True:
            self.Tool.timelimit("六国远征战", limit=60*60, init=True)
            if self.健康系统():
                return False
            if self.Tool.存在同步文件():
                return False
            if self.Tool.timelimit(timekey="六国远征_闯关计时", limit=60*50, init=False):
                TimeECHO(self.prefix+":六国远征探索时间达到上限")
                # 这里其实还在探索关卡,直接return不行,程序还在探索
                self.移动端.重启APP(10)
                return False
            # 探索过程中检测界面
            if self.六国远征_界面判断():
                TimeECHO(self.prefix+":检测到远征界面")
                for i in range(len(关卡)):
                    if exists(关卡[i]):
                        TimeECHO(self.prefix+f":存在关卡{i+1}")
                    else:
                        break
                sleep(30)
                if not self.六国远征_界面判断():
                    self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
            else:
                self.Tool.existsTHENtouch(蓝色确定, "成就确定", savepos=False)
                if self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=False):
                    TimeECHO(self.prefix+":10分钟内未检测到远征界面")
                    TimeECHO(self.prefix+":有概率界面卡住,重启APP")
                    self.移动端.重启APP(10)
                    return self.六国远征_自动探索(times)
            # 对战中判断,这句话没有什么用,就是单纯跑一下
            # windows的虚拟机,容易对战结束后卡在对战界面，如果联系60s都是对战界面,建议点击右上角退出游戏
            if self.判断对战中():
                还在对战 = True
                for i in range(30):
                    还在对战 = self.判断对战中()
                    if not 还在对战:
                        self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
                        break
                    sleep(5)
                if 还在对战:
                    TimeECHO(self.prefix+"还在对战,可能卡住,手动退出")
                    设置按钮 = Template(r"tpl1703433283847.png", record_pos=(0.47, -0.258), resolution=(960, 540))
                    退出本局 = Template(r"tpl1703433372804.png", record_pos=(-0.01, 0.218), resolution=(960, 540))
                    继续 = Template(r"tpl1703433396250.png", record_pos=(0.0, 0.241), resolution=(960, 540))
                    self.Tool.existsTHENtouch(设置按钮, "设置按钮", savepos=True)
                    sleep(5)
                    self.Tool.existsTHENtouch(退出本局, "退出本局", savepos=True)
                    sleep(5)
                    # 退出两次时怕有点击屏幕继续
                    self.Tool.existsTHENtouch(退出本局, "退出本局", savepos=True)
                    sleep(5)
                    self.Tool.existsTHENtouch(继续, "继续", savepos=False)
                    break
            #
            self.Tool.existsTHENtouch(自动探索, "自动探索", savepos=False)
            # 有时候会卡住,需要手动点击一下,而且容易卡多次
            if exists(挑战按钮):
                TimeECHO(self.prefix+"检测到挑战按钮")
                sleep(10)
                if self.Tool.existsTHENtouch(挑战按钮, "挑战按钮", savepos=False):
                    TimeECHO(self.prefix+":卡在挑战按钮,点击跳过")
                    sleep(10)
                    self.Tool.LoopTouch(挑战按钮, "挑战按钮", loop=10, savepos=False)
                    if exists(挑战按钮):
                        TimeErr(self.prefix+":仍有挑战按钮,大概率英雄已经死完了,准备重置次数")
                        if self.六国远征_重置次数():
                            TimeECHO(self.prefix+"成功重置,继续今日挑战")
                            self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
                            continue
                        else:
                            TimeECHO(self.prefix+"重置失败,开始检测原因")
                            if self.Tool.存在同步文件():
                                return False
                            # 唯一return True表示成功的入口
                            if exists(关卡[-1]):
                                TimeECHO(self.prefix+"存在关卡-1,远征完成,结束今日挑战")
                                return True
                    else:
                        TimeECHO(self.prefix+":挑战按钮消失,跳过成功")
                        self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
                        continue
            #
            # 达成六国的各种成就

            if exists(任务完成0):  # 也可能是普通的一局结束
                TimeECHO(self.prefix+":领取本局/轮奖励")
                self.Tool.existsTHENtouch(蓝色确定, "蓝色确定", savepos=False)
                if not exists(任务完成0):
                    self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
            #
            if exists(任务完成):
                TimeECHO(self.prefix+":自动探索一轮完成.回到界面.准备重置")
                # 多加几个判断
                if not exists(关卡[0]):
                    TimeECHO(self.prefix+":不存在关卡1,不该重置,返回")
                    continue
                else:
                    TimeECHO(self.prefix+":存在关卡1")
                    if not exists(关卡[-1]):
                        TimeECHO(self.prefix+":不存在关卡-1,不该重置,返回")
                        continue
                #
                if self.六国远征_重置次数():
                    self.Tool.timelimit(timekey="六国远征_卡顿计时", limit=60*20, init=True)
                    continue
                else:
                    TimeECHO(self.prefix+"无法重置,远征完成,不再继续探索")
                    return True
            sleep(30)
    # 六国远征获取的金币不受欢迎5v5对战上限限制,可以额外获得金币
    # 当英雄太少,铭文不够时,进行六国模式,容易发生英雄死完了,一轮没通关

    def 六国远征(self):
        if "2023" not in self.赛季:
            TimeECHO(self.prefix+"S34赛季彻底关闭远征商店与武道商店入口,暂时保留代码避免又增加该功能")
            return True
        if not self.Tool.timelimit("六国远征战", limit=60*60, init=False):
            TimeECHO(self.prefix+"时间太短,暂时不六国远征战")
            return False
        TimeECHO(self.prefix+":开始进行六国远征模式")
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return False
        if not self.六国远征_进入界面():
            TimeECHO(self.prefix+":无法进行六国远征模式")
            return False
        return self.六国远征_自动探索()
    #
    # 懒得分写成好几个了

    def 武道大会(self):
        if "2023" not in self.赛季:
            TimeECHO(self.prefix+"S34赛季彻底关闭远征商店与武道商店入口,暂时保留代码避免又增加该功能")
            return True
        if not self.Tool.timelimit("武道大会", limit=60*60, init=False):
            TimeECHO(self.prefix+"时间太短,暂时不武道大会")
            return False
        TimeECHO(self.prefix+":开始进行武道大会")
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return False
        # 进入对战
        武道界面 = Template(r"tpl1703483575207.png", record_pos=(-0.357, -0.25), resolution=(960, 540))
        if not exists(武道界面):
            self.进入大厅()
            万象天工 = Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540))
            if not self.Tool.existsTHENtouch(万象天工, "万象天工"):
                TimeErr(self.prefix+":找不到万象天工")
                self.进入大厅()
                if not self.Tool.existsTHENtouch(万象天工, "万象天工"):
                    TimeErr(self.prefix+":第二次无法找不到万象天工,武道大会失败")
                    return False
            sleep(2)
            #
            冒险玩法 = Template(r"tpl1703206553221.png", record_pos=(-0.433, -0.132), resolution=(960, 540))
            武道大会入口 = Template(r"tpl1703482944918.png", record_pos=(-0.158, -0.028), resolution=(960, 540))
            if not self.Tool.existsTHENtouch(冒险玩法, "冒险玩法"):
                TimeErr(self.prefix+":武道:找不到冒险玩法")
            sleep(2)
            if not self.Tool.existsTHENtouch(武道大会入口, "武道大会入口"):
                TimeErr(self.prefix+":找不到武道大会入口")
            sleep(2)
        #
        if not exists(武道界面):
            TimeErr(self.prefix+":最后也没有找到武道大会")
            return False
        #
        self.Tool.timelimit(timekey="武道大会_计时", limit=60*50, init=True)
        while True:
            self.Tool.timelimit("武道大会", limit=60*60, init=True)
            # .............................................
            if not exists(武道界面):
                TimeErr(self.prefix+":不在武道大会初始界面")
                return False
            # .............................................
            if self.健康系统():
                return False
            if self.Tool.存在同步文件():
                return False
            if self.Tool.timelimit(timekey="武道大会_计时", limit=60*50, init=False):
                TimeECHO(self.prefix+":武道大会达到时间上限")
                # 这里其实还在探索关卡,直接return不行,程序还在探索
                self.移动端.重启APP(10)
                return False
            #
            挑战按钮1 = Template(r"tpl1703482958121.png", record_pos=(0.307, 0.106), resolution=(960, 540))
            self.Tool.existsTHENtouch(挑战按钮1, "主挑战按钮", savepos=True)
            sleep(5)
            # 这里等待判断是不是对战次数达到上限
            挑战界面 = Template(r"tpl1703482977909.png", record_pos=(-0.002, -0.116), resolution=(960, 540))
            if not exists(挑战界面):
                TimeECHO(self.prefix+":武道大会今日达标")
                return True
            挑战按钮2 = Template(r"tpl1703482967110.png", record_pos=(0.122, -0.046), resolution=(960, 540))
            self.Tool.existsTHENtouch(挑战按钮2, "次挑战按钮", savepos=True)
            sleep(5)
            没选择英雄时 = Template(r"tpl1703483013544.png", record_pos=(0.427, -0.011), resolution=(960, 540))
            if exists(没选择英雄时):
                TimeErr(self.prefix+":需要手动选择英雄")
                return False
            确定挑战 = Template(r"tpl1703483092932.png", record_pos=(0.427, 0.239), resolution=(960, 540))
            self.Tool.existsTHENtouch(确定挑战, "确定挑战", savepos=True)
            # sleep至对战阶段,这个要判断勤点,不然直接循环的就太久了
            for i in range(60):
                if self.判断对战中():
                    break  # 流程正常
                TimeECHO(self.prefix+":sleep等待对战检测")
                sleep(2)
                if self.Tool.existsTHENtouch(挑战按钮2, "loop次挑战按钮", savepos=False):
                    sleep(1)
                if self.Tool.existsTHENtouch(确定挑战, "loop确定挑战", savepos=False):
                    sleep(1)  # 玩意没有确定成功
            # 等待对战结束
            for i in range(10):
                if self.判断对战中():
                    TimeECHO(self.prefix+":sleep等待对战结束")
                    sleep(90)  # 等待长一点时间
                else:
                    sleep(30)  # 避免刚结束对战，程序有点小卡
                    break
            #
            任意点击继续 = Template(r"tpl1703483189920.png", record_pos=(0.003, 0.228), resolution=(960, 540))
            self.Tool.existsTHENtouch(任意点击继续, "任意点击继续", savepos=True)
            sleep(10)
            确定继续 = Template(r"tpl1703483203726.png", record_pos=(0.302, 0.23), resolution=(960, 540))
            self.Tool.existsTHENtouch(确定继续, "确定继续")
            sleep(10)
            任意继续 = Template(r"tpl1703483241120.png", record_pos=(-0.006, -0.255), resolution=(960, 540))
            self.Tool.existsTHENtouch(任意继续, "任意继续")
            sleep(10)
            黄色确定 = Template(r"tpl1703207718965.png", record_pos=(-0.004, 0.164), resolution=(960, 540))
            if self.Tool.existsTHENtouch(黄色确定, "段位提升黄色确定"):
                sleep(10)
            继续按钮 = Template(r"tpl1703483264138.png", record_pos=(-0.002, 0.24), resolution=(960, 540))
            self.Tool.existsTHENtouch(继续按钮, "继续按钮")
            sleep(10)
            if self.健康系统():
                return False
            if not exists(武道界面):
                TimeECHO(self.prefix+"找不到武道界面了,重新进入界面")
                sleep(30)
                self.移动端.重启APP()
                self.登录游戏()
                self.进入大厅()
                self.Tool.existsTHENtouch(万象天工, "万象天工")
                self.Tool.existsTHENtouch(冒险玩法, "冒险玩法")
                self.Tool.existsTHENtouch(武道大会入口, "武道大会入口")
# 状态判断

    def 判断大厅中(self):
        存在, self.大厅元素 = self.Tool.存在任一张图(self.大厅元素, "大厅元素")
        return 存在

    def 判断房间中(self):
        存在, self.房间元素 = self.Tool.存在任一张图(self.房间元素, "房间元素")
        return 存在

    def 判断对战中(self, 处理=False):
        if "模拟战" in self.对战模式:
            return self.判断对战中_模拟战(处理)
        对战 = Template(r"tpl1689666416575.png", record_pos=(0.362, 0.2), resolution=(960, 540), threshold=0.9)
        移动 = Template(r"tpl1702267006237.png", record_pos=(-0.327, 0.16), resolution=(960, 540))
        TimeECHO(self.prefix+"判断对战中")
        if exists(对战):
            TimeECHO(self.prefix+"正在对战中")
            if 处理:
                TimeECHO(self.prefix+"加速对战中:建议把自动买装备和自动技能加点打开,更真实一些")
                self.Tool.timelimit(timekey="endgame", limit=60*30, init=True)
                移动pos = False
                self.Tool.timelimit(timekey="check_connect_status", limit=60, init=True)
                while self.Tool.existsTHENtouch(对战):
                    TimeECHO(self.prefix+"加速对战中:对战按钮")
                    if self.Tool.timelimit(timekey="check_connect_status", limit=60, init=False):
                        self.check_connect_status()
                    if self.Tool.存在同步文件():
                        return True
                    if not 移动pos:
                        self.Tool.existsTHENtouch(移动, "移动按钮", savepos=True)
                        移动pos = exists(移动)
                        if not 移动pos and "移动按钮" in self.Tool.var_dict.keys():
                            移动pos = self.Tool.var_dict["移动按钮"]
                    else:
                        TimeECHO(self.prefix+"加速对战中:移动按钮")
                        for i in range(random.randint(1, 5)):
                            x = 0.2+random.random()/5
                            y = -0.2+random.random()/5
                            swipe(移动pos, vector=[x, y])
                            self.Tool.existsTHENtouch(对战, "对战按钮", savepos=True)
                    #
                    if self.Tool.timelimit(timekey="endgame", limit=60*30, init=False):
                        TimeErr(self.prefix+"对战中游戏时间过长,重启游戏")  # 存在对战的时间超过20min,大概率卡死了
                        self.移动端.重启APP(10)
                        self.登录游戏()
                        self.进入大厅()
                        return False
            return True
        TimeECHO(self.prefix+"判断对战中:没有对战")

        return False

    def 判断对战中_模拟战(self, 处理=False):
        正在对战 = False
        if exists(Template(r"tpl1690546926096.png", record_pos=(-0.416, -0.076), resolution=(960, 540))):
            TimeECHO(self.prefix+"开始中")
            if not 处理:
                return True
            sleep(5)
            正在对战 = True
        # 立信界面

        if exists(Template(r"tpl1690547491681.png", record_pos=(0.471, 0.165), resolution=(960, 540))):
            TimeECHO(self.prefix+"战斗界面")
            if not 处理:
                return True
            sleep(5)
            正在对战 = True

        if exists(Template(r"tpl1690552290188.png", record_pos=(0.158, 0.089), resolution=(960, 540))):
            TimeECHO(self.prefix+"方案界面")
            if not 处理:
                return True
            sleep(5)
            正在对战 = True
        钱袋子 = Template(r"tpl1690546610171.png", record_pos=(0.391, 0.216), resolution=(960, 540))
        刷新金币 = Template(r"tpl1690547053276.png", record_pos=(0.458, -0.045), resolution=(960, 540))
        关闭钱袋子 = Template(r"tpl1690547457483.png", record_pos=(0.392, 0.216), resolution=(960, 540))
        if exists(钱袋子):
            TimeECHO(self.prefix+"钱袋子")
            if not 处理:
                return True
        if exists(刷新金币):
            TimeECHO(self.prefix+"刷新金币")
            if not 处理:
                return True
        #
        if not 处理:
            return 正在对战
        if not 正在对战:
            return 正在对战
        #
        #
        # 下面开始处理对战
        self.Tool.LoopTouch(钱袋子, "初次钱袋子", loop=10)
        self.Tool.LoopTouch(刷新金币, "初次刷新金币", loop=10)
        self.Tool.timelimit(timekey="endgame", limit=60*20, init=True)
        while self.判断对战中_模拟战(False):
            TimeECHO(self.prefix+"处理对战中")
            self.Tool.LoopTouch(钱袋子, "LOOP钱袋子", loop=10)  # 点击结束后,应该变成X号
            self.Tool.LoopTouch(刷新金币, "LOOP刷新金币", loop=10)
            if not exists(关闭钱袋子) and not exists(钱袋子):
                return False
            if self.Tool.timelimit(timekey="endgame", limit=60*20, init=False):
                break
            sleep(10)
            self.check_connect_status()
            if self.Tool.存在同步文件():
                return True
        return 正在对战

    def 健康系统(self):
        if exists(Template(r"tpl1689666921933.png", record_pos=(0.122, -0.104), resolution=(960, 540))):
            TimeECHO(self.prefix+"您已禁赛")
            确定 = Template(r"tpl1701171103293.png", record_pos=(-0.004, 0.081), resolution=(1136, 640))
            self.Tool.existsTHENtouch(确定, self.prefix+"确定禁赛")
            return True
        return False

    def 健康系统_常用命令(self):
        if self.健康系统():
            if self.组队模式:
                TimeErr(self.prefix+"组队情况检测到健康系统,所以touch同步文件")
                self.Tool.touch同步文件()
                sleep(30)
            else:
                TimeErr(self.prefix+"独立模式检测到健康系统,领取营地礼包等操作")
                if self.王者营地礼包:
                    self.Tool.timedict["领营地礼包"] = 0
                    self.每日礼包_王者营地()
                    sleeptime = 6.0
                else:
                    sleeptime = 60*5.0
                TimeErr(self.prefix+f"独立模式检测到健康系统,sleep {sleeptime/60} min")
                self.移动端.重启APP(sleeptime)
                self.登录游戏()
            return True
        else:
            return False

    def check_connect_status(self):
        #
        if self.Tool.存在同步文件(self.Tool.独立同步文件):
            if self.组队模式:
                self.Tool.touch同步文件()
            return False
        #
        if not connect_status():
            # 尝试连接一下,还不行就同步吧
            self.移动端.连接设备(times=1, timesMax=2)
            if connect_status():
                return True
            else:
                self.Tool.touch同步文件(self.Tool.独立同步文件)

            # 单人模式创建同步文件后等待,组队模式则让全体返回
            self.Tool.touch同步文件(self.Tool.独立同步文件)
            if self.组队模式:
                self.Tool.touch同步文件()
            return False
        else:
            return True

# 开始运行
    def 进行人机匹配对战循环(self):
        # .
        self.check_connect_status()
        # 初始化
        if self.房主:
            TimeECHO(self.prefix+"人机匹配对战循环:"+"->"*10)
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        # 进入房间
        self.进入人机匹配房间()
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        # 进行对战
        self.进行人机匹配()
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        加速对战 = False
        if self.debug:
            加速对战 = True
        if "模拟战" in self.对战模式:
            加速对战 = True
        if self.标准触摸对战:
            加速对战 = True
        if self.判断对战中(加速对战):
            sleep(30)
        # 测试发现,对战过程中退出后台,没有获得到奖励,关闭此功能
        # 结束对战
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        self.结束人机匹配()
        #
        self.check_connect_status()
        if self.Tool.存在同步文件():
            return True
        #
        if self.mynode == 0:
            self.Tool.clean文件()
        if self.房主:
            TimeECHO(self.prefix+"<-"*10)
        #

    def RUN(self):  # 程序入口
        while True:
            # ------------------------------------------------------------------------------
            if os.path.exists(self.临时初始化FILE):
                TimeECHO(self.prefix+f":注入临时初始化代码({self.临时初始化FILE})")
                exec_insert = self.Tool.readfile(self.临时初始化FILE)
                for i_insert in exec_insert:
                    trim_insert = i_insert.strip()
                    if len(trim_insert) < 1:
                        continue
                    if '#' == trim_insert[0]:
                        continue
                    try:
                        exec(i_insert)
                        if "TimeE" not in i_insert:
                            TimeECHO(self.prefix+".临时初始.run: "+i_insert[:-1])
                    except:
                        TimeErr(self.prefix+".临时初始.Error run: "+i_insert[:-1])
            # ------------------------------------------------------------------------------
            # 先确定每个节点是否都可以正常连接,这里不要退出,仅生成需要退出的信息和创建同步文件
            # 然后多节点进行同步后
            # 再统一退出
            if not connect_status() or self.Tool.存在同步文件(self.Tool.独立同步文件):
                self.移动端.连接设备()
                if connect_status():
                    self.Tool.removefile(self.Tool.独立同步文件)
                else:
                    TimeErr(self.prefix+"连接不上设备. 待同步后退出")
                    if self.totalnode_bak > 1:  # 让其他节点抓紧结束
                        self.Tool.touchstopfile(f"{self.mynode}连接不上设备")
                        self.Tool.touch同步文件()
            # ------------------------------------------------------------------------------
            # 强制同步
            # 这里是能正常点击,但是可能进入了异常的界面/禁赛等原因导致的重置部分
            # 这里的同步是只有本程序的并行,不依赖于airtest等库,因此一定可以执行的
            if self.totalnode_bak > 1 and self.Tool.存在同步文件(self.Tool.辅助同步文件):  # 单进程各种原因出错时,多进程无法同步时
                TimeECHO(self.prefix+"存在同步文件,需要同步程序")
                self.移动端.关闭APP()
                if self.王者营地礼包 and not connect_status():
                    self.每日礼包_王者营地()
                self.Tool.必须同步等待成功(mynode=self.mynode, totalnode=self.totalnode,
                                   同步文件=self.Tool.辅助同步文件, sleeptime=60*5)
                self.移动端.重启APP(sleeptime=self.mynode*10+60)
            # ------------------------------------------------------------------------------
            # 现在所有进程都在这里了,开始判断单个节点的问题,以及是否退出
            # 检查本节点是否需要独立同步(重置连接)
            # 是否有节点存在物理故障
            if self.totalnode_bak > 1:
                if self.Tool.readstopfile():  # 这个只在多节点运行时会创建
                    self.Tool.stoptask()
                    return  # 就是结束
            else:
                if not connect_status():
                    TimeErr(self.prefix+"连接不上设备. 退出")
                    return
            self.Tool.removefile(self.Tool.独立同步文件)
            #
            # ------------------------------------------------------------------------------
            if os.path.exists(self.结束游戏FILE):
                TimeECHO(self.prefix+f"检测到{self.结束游戏FILE}, stop")
                self.移动端.关闭APP()
                return
            #
            while os.path.exists(self.SLEEPFILE):
                TimeECHO(self.prefix+f"检测到{self.SLEEPFILE}, sleep(5min)")
                sleep(60*5)
            # ------------------------------------------------------------------------------
            # 下面就是正常的循环流程了
            #
            # ------------------------------------------------------------------------------
            # 设定运行时间和运行模式
            # 运行时间检测
            startclock = self.对战时间[0]
            endclock = self.对战时间[1]  # 服务器5点刷新礼包和信誉积分等
            # if self.移动端.实体终端 and self.totalnode_bak == 1: endclock=19
            if self.runstep == 0:
                startclock = -1
                endclock = 25
            hour, minu = self.Tool.time_getHM()
            #
            新的一天 = False
            while hour >= endclock or hour < startclock:
                # 这里仅领礼包,不要插入六国远征等不稳定的任务
                TimeECHO(self.prefix+"夜间停止刷游戏")
                self.Tool.touchfile(self.免费商城礼包FILE)
                if os.path.exists(self.重新登录FILE):
                    TimeECHO(self.prefix+"存在重新登录文件,无法每日礼包")
                else:
                    self.每日礼包()
                self.移动端.关闭APP()
                # 计算休息时间
                hour, minu = self.Tool.time_getHM()
                leftmin = max(((startclock+24-hour) % 24)*60-minu, 1)
                if leftmin > 60:  # 考虑startclock=N.m sleep的时间容易变成22.9h, 这里直接用20判断
                    if abs(hour-startclock) < 2:
                        TimeECHO(self.prefix+"hour距离startclock过短,不该大于60min,set leftmin=2")
                        leftmin = 2
                if self.移动端.容器优化:
                    leftmin = leftmin+self.mynode*1  # 这里的单位是分钟,每个node别差别太大
                TimeECHO(self.prefix+"预计等待%d min ~ %3.2f h" % (leftmin, leftmin/60.0))
                if self.debug:
                    leftmin = 0.5
                if leftmin > 60:
                    self.移动端.重启APP(leftmin*60)
                else:
                    sleep(leftmin*60)
                if not self.check_connect_status():
                    self.移动端.连接设备()
                    self.移动端.重启APP(30)
                #
                if self.王者营地礼包:
                    self.每日礼包_王者营地()
                #
                if self.debug:
                    break
                hour, minu = self.Tool.time_getHM()
                新的一天 = True
            if 新的一天:
                self.移动端.重启APP(10)
                self.登录游戏()
                self.jinristep = 0
                self.赛季 = "2024"
                self.进行六国远征 = False
                self.进行武道大会 = False
                if "2023" in self.赛季:
                    # 存在该文件则进行六国远征
                    self.Tool.touchfile(self.prefix+"六国远征.txt")
                    self.Tool.touchfile(self.prefix+"武道大会.txt")
                self.选择人机模式 = True
                self.青铜段位 = False
                self.Tool.removefile(self.青铜段位FILE)
                self.Tool.touchfile(self.免费商城礼包FILE)
                if self.totalnode_bak > 1:
                    self.Tool.touch同步文件()
                continue
            #
            if os.path.exists(self.重新登录FILE):
                TimeECHO(self.prefix+"存在重新登录文件,登录后删除")
                sleep(60*10)
                continue
            #
            hour, minu = self.Tool.time_getHM()
            # 当hour小于此数字时才是组队模式
            # 这里的同步文件是怕有的进程跑的太快了，刚好错过这个时间点
            # 去掉条件and self.runstep > 0, 以后的第一次不再进行组队模拟,程序出问题的概率不大,真测试可以touch组队文件
            if hour >= self.限时组队时间 and not self.Tool.存在同步文件() and self.totalnode > 1:
                TimeECHO(self.prefix+"限时进入单人模式")
                self.totalnode = 1
                self.进入大厅()
            if hour < self.限时组队时间:
                self.totalnode = self.totalnode_bak
            else:
                if self.totalnode_bak > 1 and self.totalnode == 1:
                    if os.path.exists(self.临时组队FILE):
                        TimeECHO(self.prefix+f"检测到{self.临时组队FILE}, 使用组队模式对战")
                        self.totalnode = self.totalnode_bak
            self.组队模式 = self.totalnode > 1
            # 各种原因无法组队判定
            self.无法进行组队 = os.path.exists(self.无法进行组队FILE)
            if self.组队模式 and self.无法进行组队:
                TimeECHO(self.prefix+f"检测到{self.无法进行组队FILE}, 无法进行组队,关闭组队功能")
                self.组队模式 = False
                self.totalnode = 1
            #
            if self.组队模式:
                TimeECHO(self.prefix+"组队模式")
            self.房主 = self.mynode == 0 or self.totalnode == 1
            #
            # 仅在单人模式时进行六国远征
            self.进行六国远征 = not self.组队模式 and os.path.exists(self.prefix+"六国远征.txt")
            self.进行武道大会 = not self.组队模式 and os.path.exists(self.prefix+"武道大会.txt")
            if self.进行六国远征:
                self.进行六国远征 = not self.六国远征()
                self.进入大厅()
                if self.进行六国远征:
                    TimeECHO(self.prefix+"六国远征探索未结束,需要重复进行探索")
                else:
                    TimeECHO(self.prefix+"今日六国远征探索完成")
                    self.Tool.removefile(self.prefix+"六国远征.txt")
            if self.Tool.存在同步文件():
                continue
            if self.进行武道大会:
                self.进行武道大会 = not self.武道大会()
                self.进入大厅()
                if self.进行武道大会:
                    TimeECHO(self.prefix+"武道大会探索未结束,需要重复进行探索")
                else:
                    TimeECHO(self.prefix+"今日武道大会探索完成")
                    self.Tool.removefile(self.prefix+"武道大会.txt")
            #
            if self.Tool.存在同步文件():
                continue
            self.Tool.barriernode(self.mynode, self.totalnode, "准备进入战斗循环")
            #
            if self.Tool.存在同步文件():
                continue
            #
            # ------------------------------------------------------------------------------
            self.runstep = self.runstep+1
            self.jinristep = self.jinristep+1
            #
            # ------------------------------------------------------------------------------
            # 增加对战模式
            self.青铜段位 = os.path.exists(self.青铜段位FILE)
            self.标准模式 = os.path.exists(self.标准模式FILE)
            self.触摸对战 = os.path.exists(self.触摸对战FILE)
            self.标准触摸对战 = os.path.exists(self.标准模式触摸对战FILE)
            if self.组队模式 and not self.青铜段位:
                TimeECHO(self.prefix+f"组队时采用青铜段位")
                self.青铜段位 = True
            # 默认标准模式的触摸对战每天只启动一次,其余时间用户通过手动建文件启动
            # 经过对比发现,触摸对战,系统会判定没有挂机,给的金币更多, 所以这里提高5v5对战过程中触摸的几率
            # 每日的任务也需要击杀足够数量,获得金牌等,此时不触摸才能完成任务. 所以这里对半分挂机与否
            # 触摸标准对战持续29min胜利,获得了170+金币. 触摸快速对战记录最大值35金币
            if self.jinristep % 2 == 0 and not self.组队模式:
                self.触摸对战 = True
            # 在特定步数进行标准对战,频率很低
            if self.jinristep % 10 == 0 and not self.组队模式:
                self.标准触摸对战 = True
            # 希望在青铜局时进行触摸对战,而不是占据星耀刷熟练度的机会
            if not self.青铜段位:
                if self.触摸对战:
                    TimeECHO(self.prefix+f"非青铜局不模拟人手触摸")
                    self.触摸对战 = False
                if self.标准触摸对战:
                    TimeECHO(self.prefix+f"非青铜局不进行标准模式的人手触摸")
                    self.标准触摸对战 = False
            if self.触摸对战:
                TimeECHO(self.prefix+f"本局对战,模拟人手触摸")
            if self.标准触摸对战:
                self.标准模式 = True
                TimeECHO(self.prefix+f"使用标准模式对战,并且模拟人手触摸")
            # ------------------------------------------------------------------------------
            # 运行前统一变量
            self.runinfo["runstep"] = self.runstep
            self.runinfo = self.Tool.bcastvar(self.mynode, self.totalnode, var=self.runinfo, name="bcastruninfo")
            self.runstep = self.runinfo["runstep"]
            TimeECHO(self.prefix+f"运行次数{self.runstep}|今日步数{self.jinristep}")
            #
            # ------------------------------------------------------------------------------
            if os.path.exists(self.对战前插入FILE):
                TimeECHO(self.prefix+f":对战前注入代码({self.对战前插入FILE})")
                exec_insert = self.Tool.readfile(self.对战前插入FILE)
                for i_insert in exec_insert:
                    trim_insert = i_insert.strip()
                    if len(trim_insert) < 1:
                        continue
                    if '#' == trim_insert[0]:
                        continue
                    try:
                        exec(i_insert)
                        if "TimeE" not in i_insert:
                            TimeECHO(self.prefix+".对战前注入.run: "+i_insert[:-1])
                    except:
                        TimeErr(self.prefix+".对战前注入.Error run: "+i_insert[:-1])
            # ------------------------------------------------------------------------------
            # 开始辅助同步,然后开始游戏
            self.进行人机匹配对战循环()
            if self.Tool.存在同步文件():
                continue
            if not connect_status():
                continue
            # 礼包
            if self.runstep % 5 == 0:  # 实际礼包还有1h间隔限制,这里取的self.runstep小没事
                if not connect_status():
                    continue
                self.每日礼包()
            #
            if self.移动端.实体终端 and self.Tool.timelimit("休息手机", limit=60*60, init=False):
                TimeECHO(self.prefix+":实体终端,休息设备")
                # self.移动端.关闭APP()
                sleep(60*2)


class auto_airtest:
    def __init__(self, mynode=0, totalnode=1, 设备类型="android", LINK_dict={}):
        self.mynode = mynode
        self.totalnode = totalnode
        self.设备类型 = 设备类型.lower()
        self.prefix = f"({self.mynode}/{self.totalnode})"
        self.debug = "darwin" in sys.platform.lower()
        # 设备信息
        if len(LINK_dict) == 0:
            LINK_dict = {}
            if "android" in self.设备类型:
                LINK_dict[0] = "Android:///"+"127.0.0.1:"+str(5555)
                LINK_dict[1] = "Android:///"+"127.0.0.1:"+str(5565)
                LINK_dict[2] = "Android:///"+"127.0.0.1:"+str(5575)
                LINK_dict[3] = "Android:///"+"127.0.0.1:"+str(5585)
                LINK_dict[4] = "Android:///"+"127.0.0.1:"+str(5595)
            else:
                LINK_dict[0] = "ios:///http://"+"192.168.12.130:8100"
                LINK_dict[1] = "ios:///http://"+"192.168.12.130:8101"
                LINK_dict[2] = "ios:///http://"+"192.168.12.130:8102"
                LINK_dict[3] = "ios:///http://"+"192.168.12.130:8103"
                LINK_dict[4] = "ios:///http://"+"192.168.12.130:8104"
            if self.debug:
                # 当在这里手动指定Link时,自动进行修正
                LINK_dict[0] = "Android:///"+"192.168.192.10:5555"
                LINK_dict[1] = "Android:///"+"192.168.192.10:5565"
                LINK_dict[2] = "Android:///"+"192.168.192.10:5575"
                LINK_dict[3] = "Android:///"+"192.168.192.10:5585"
                # 以后不再以IOS平台进行测试,这里暂时关闭IOS入口
                # LINK_dict[2] = "ios:///http://127.0.0.1:8200"
                # LINK_dict[totalnode-1]="ios:///http://127.0.0.1:8200"
                # LINK_dict[totalnode-1]="ios:///http://169.254.83.56:8100"
                # LINK_dict[2]="ios:///http://169.254.83.56:8100"
                self.debug = False  # 仅用于设置ios连接,程序还是正常运行
        # 使用端口映射成8200后, usb接口老频繁失灵，怀疑与这个有关,还是采用默认的方式
        # if "ios" in LINK_dict[0]: os.system("tidevice wdaproxy -B com.facebook.WebDriverAgentRunner.cndaqiang.xctrunner > tidevice.result.txt 2>&1 &")
        #
        #
        self.LINK = LINK_dict[mynode]
        self.设备类型 = self.LINK.split(":")[0].lower()
        self.APPID = "com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.printINFO()
        self.移动端 = deviceOB(设备类型=self.设备类型, mynode=self.mynode, totalnode=self.totalnode, LINK=self.LINK, APPID=self.APPID)
        if not self.移动端.device:
            TimeErr(self.prefix+f"{self.prefix}:连接设备失败,退出")
        #
        对战模式 = "模拟战" if "moni" in __file__ else "5v5匹配"
        TASK = wzry_task(self.移动端, 对战模式, shiftnode=-4, debug=self.debug)
        # 以后的测试脚本写在WZRY.0.临时初始化.txt中,不再插入到object.py中
        TASK.RUN()
        self.移动端.关闭APP()
        #

    def printINFO(self):
        TimeECHO(self.prefix+f"{self.prefix}:LINK={self.LINK}")
        TimeECHO(self.prefix+f"{self.prefix}:设备类型={self.设备类型}")
        TimeECHO(self.prefix+f"{self.prefix}:mynode={self.mynode}")
        TimeECHO(self.prefix+f"{self.prefix}:totalnode={self.totalnode}")
        TimeECHO(self.prefix+f"{self.prefix}:APPID={self.APPID}")


# @todo
# 给ios设备添加休息冷却的时间
#
# 如果文件被直接执行，则执行以下代码块
if __name__ == "__main__":
    multi_run = False
    设备类型 = "android"
    # 设备类型="ios"
    if len(sys.argv) <= 1:  # 直接跑
        mynode = 0
        totalnode = 1
    elif len(sys.argv) <= 2:  # 直接跑,或者指定node跑
        try:
            para2 = int(sys.argv[1])
        except:
            para2 = 0
        if para2 >= 0:
            mynode = para2
            totalnode = 1
        else:
            mynode = 0
            totalnode = abs(para2)
            multi_run = True
    else:  # 组队模式,但是自己单进程跑
        mynode = int(sys.argv[1])
        totalnode = int(sys.argv[2])
    if not multi_run:
        auto_airtest(mynode, totalnode, 设备类型)
    else:
        def multi_start(i):
            auto_airtest(i, totalnode, 设备类型)
        from pathos import multiprocessing
        m_process = totalnode
        # barrier=multiprocessing.Barrier(totalnode)
        m_cpu = [i for i in range(0, m_process)]
        if __name__ == '__main__':
            p = multiprocessing.Pool(m_process)
            out = p.map_async(multi_start, m_cpu).get()
            p.close()
            p.join()
