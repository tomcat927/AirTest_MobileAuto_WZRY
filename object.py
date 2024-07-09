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
import airtest
from airtest.core.settings import Settings as ST
import logging
import sys
import os
import numpy as np
import random
import traceback
import subprocess
# 重写函数#
from airtest.core.api import connect_device, sleep
from airtest.core.api import exists as exists_o
from airtest.core.api import touch as touch_o
from airtest.core.api import swipe as swipe_o
from airtest.core.api import start_app as start_app_o
from airtest.core.api import stop_app as stop_app_o
from airtest.core.api import Template as Template_o

# ........................
# python -m pip install --upgrade --no-deps --force-reinstall airtest
# vscode设置image preview的解析目录为assets,就可以预览了
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
# ? 设置,虚拟机,android docker, iphone, etc,主要进行设备的连接和重启
BlueStackdir="C:\Program Files\BlueStacks_nxt"
LDPlayerdir="D:\GreenSoft\LDPlayer"

# 获取当前的运行信息, 有的客户端有bug
AirtestIDE = "AirtestIDE" in sys.executable


# 控制屏幕输出
# 这个设置可以极低的降低airtest输出到屏幕的信息
logger = logging.getLogger("airtest")
logger.setLevel(logging.WARNING)

# 替代基础的print函数


def TimeECHO(info="None", end=""):
    # 由于AirTest客户端的解释器不会输出print的命令
    if AirtestIDE:
        logger.warning(info)
        return
    # 获取当前日期和时间
    current_datetime = datetime.now(eastern_eight_tz)
    # 格式化为字符串（月、日、小时、分钟、秒）
    formatted_string = current_datetime.strftime("[%m-%d %H:%M:%S]")
    modified_args = formatted_string+info
    if len(end) > 0:
        print(modified_args, end=end)
    else:
        print(modified_args)


def TimeErr(info="None"):
    TimeECHO("NNNN:"+info)


def fun_name(level=1):
    import inspect
    fun = inspect.currentframe()
    ilevel = 0
    for i in range(level):
        try:
            fun = fun.f_back
            ilevel = ilevel+1
        except:
            break
    try:
        return str(fun.f_code.co_name)
    except:
        return f"not found fun_name({ilevel})"

# 如果命令需要等待打开的程序关闭, 这个命令很容易卡住


def getstatusoutput(*args, **kwargs):
    try:
        return subprocess.getstatusoutput(*args, **kwargs)
    except:
        return [1, traceback.format_exc()]


def run_command(command=[], sleeptime=20,  prefix="", quiet=False, must_ok=False):
    """
     执行命令
    """
    exit_code_o = 0
    command_step = 0
    # 获得运行的结果
    for i_command in command:
        # 去掉所有的空白符号看是否还有剩余命令
        trim_insert = i_command.strip()
        if len(trim_insert) < 1:
            continue
        if not quiet:
            TimeECHO(prefix+"sysrun:"+i_command)
        try:
            #result = [os.system(i_command), f"run_command({i_command})"]
            #os.system的容易卡，各种命令兼容性也不好，subprocess.Popen可以直接填windows快捷方式里的内容
            process = subprocess.Popen(i_command)
            result = [0, str(process)]
            # 运行成功的结果会直接输出的
        except:
            result = [1, traceback.format_exc()]
        command_step = command_step + 1
        exit_code = result[0]
        if not quiet:
            if exit_code != 0:
                TimeECHO(prefix+"result:"+">"*20)
                TimeECHO(result[1])
                TimeECHO(prefix+"result:"+"<"*20)
        exit_code_o += exit_code
        if must_ok and exit_code_o != 0:
            break
        sleep(sleeptime)
    # 没有执行任何命令
    if command_step == 0:
        exit_code_o = -100
    return exit_code_o


def run_class_command(self=None, command=[], prefix="", quiet=False, must_ok=False):
    """
 # 执行模块内的文件
 # 以为文件中的命令可能包含self,所以把self作为输入参数
    """
    # 获得运行的结果
    exit_code_o = 0
    command_step = 0
    for i_command in command:
        # 去掉所有的空白符号看是否还有剩余命令
        trim_insert = i_command.strip()
        if len(trim_insert) < 1:
            continue
        if '#' == trim_insert[0]:
            continue
        if not quiet:
            TimeECHO(prefix+'python: '+i_command.rstrip())
        try:
            exec(i_command)
            exit_code = 0
            command_step = command_step + 1
        except:
            traceback.print_exc()
            exit_code = 1
        exit_code_o += exit_code
        if must_ok and exit_code_o != 0:
            break
    # 没有执行任何命令
    if command_step == 0:
        exit_code_o = -100
    return exit_code_o


def getpid_win(IMAGENAME="HD-Player.exe", key="BlueStacks App Player 0"):
    if sys.platform.lower() != "win32":
        return 0
    try:
        tasklist = os.popen(f'tasklist -FI "IMAGENAME eq {IMAGENAME}" /V')
    except:
        TimeECHO(f"getpid_win({IMAGENAME}) error"+"-"*10)
        traceback.print_exc()
        TimeECHO(f"getpid_win({IMAGENAME}) error"+"-"*10)
    cont = tasklist.readlines()
    PID = 0
    for task in cont:
        taskterm = task.split()
        if len(taskterm) < 3:
            continue
        #IMAGENAME如果太长了会显示不全，因此不能直接IMAGENAME in task
        lenname=len(taskterm[0])
        if lenname == 0:
            continue
        if lenname < len(IMAGENAME):
            if not taskterm[0] == IMAGENAME[:lenname]:
                continue
        #key还是可以显示全的
        if key in task:
            PID = task.split()[1]
            try:
                TimeECHO(f"getpid_win:{task}")
                PID = int(PID)
            except:
                TimeECHO(f"getpid_win({IMAGENAME},{key}) error"+"-"*10)
                traceback.print_exc()
                TimeECHO(f"getpid_win({IMAGENAME},{key}) error"+"-"*10)
                PID = 0
            break
    return PID


def connect_status(times=10, prefix=""):
    # png = Template_o(r"assets/tpl_target_pos.png", record_pos=(-0.28, 0.153), resolution=(960, 540), target_pos=6)
    # 同一个py文件, 只要在调用之前定义过了就可以
    png = Template(r"tpl_target_pos.png", record_pos=(-0.28, 0.153), resolution=(960, 540), target_pos=6)
    prefix = f"{prefix} [{fun_name(2)}][{fun_name(1)}]"
    #
    for i in np.arange(times):
        try:
            exists_o(png)
            return True
        except:
            if i == times - 1:
                traceback.print_exc()
            TimeECHO(f"{prefix}无法连接设备,重试中{i}")
            sleep(1)
            continue
    TimeECHO(f"{prefix}设备失去联系")
    return False
# ........................


def exists(*args, **kwargs):
    prefix = ""
    if "prefix" in kwargs:
        prefix = kwargs["prefix"]
        del kwargs["prefix"]
    try:
        result = exists_o(*args, **kwargs)
    except:
        result = False
        TimeECHO(f"{prefix}  {fun_name(1)}  失败")
        if not connect_status(prefix=prefix):
            TimeErr(f"{prefix} {fun_name(1)}连接不上设备")
            return result
        sleep(1)
        try:
            result = exists_o(*args, **kwargs)
        except:
            traceback.print_exc()
            TimeECHO(f"{prefix} 再次尝试{fun_name(1)}仍失败")
            result = False
    return result


def touch(*args, **kwargs):
    prefix = ""
    if "prefix" in kwargs:
        prefix = kwargs["prefix"]
        del kwargs["prefix"]
    try:
        result = touch_o(*args, **kwargs)
    except:
        result = False
        TimeECHO(f"{prefix}  {fun_name(1)}  失败")
        if not connect_status(prefix=prefix):
            TimeErr(f"{prefix} {fun_name(1)}连接不上设备")
            return result
        sleep(1)
        try:
            result = touch_o(*args, **kwargs)
        except:
            traceback.print_exc()
            TimeECHO(f"{prefix} 再次尝试{fun_name(1)}仍失败")
            result = False
    return result


def swipe(*args, **kwargs):
    prefix = ""
    if "prefix" in kwargs:
        prefix = kwargs["prefix"]
        del kwargs["prefix"]
    result = False
    try:
        result = swipe_o(*args, **kwargs)
    except:
        result = False
        TimeECHO(f"{prefix}  {fun_name(1)}  失败")
        if not connect_status(prefix=prefix):
            TimeErr(f"{prefix} {fun_name(1)}连接不上设备")
            return result
        sleep(1)
        try:
            result = swipe_o(*args, **kwargs)
        except:
            traceback.print_exc()
            TimeECHO(f"{prefix} 再次尝试{fun_name(1)}仍失败")
            result = False
    return result


def start_app(*args, **kwargs):
    prefix = ""
    if "prefix" in kwargs:
        prefix = kwargs["prefix"]
        del kwargs["prefix"]
    try:
        result = True
        start_app_o(*args, **kwargs)
    except:
        result = False
        TimeECHO(f"{prefix} {fun_name(1)} 失败")
        if not connect_status(prefix=prefix):
            TimeErr(f"{prefix} {fun_name(1)}连接不上设备")
            return result
        sleep(1)
        # ......
        # 安卓系统的报错, 尝试进行修复
        errormessgae = traceback.format_exc()
        if "AdbError" in errormessgae or True:
            """
            使用start_app启动安卓软件的各种坑（有的安卓系统使用monkey需要添加参数，否则报错）
            方式1(monkey). start_app(package_name), 需要修改Airtest的代码添加`--pct-syskeys 0`(https://cndaqiang.github.io/2023/11/10/MobileAuto/)
            adb -s 127.0.0.1:5555 shell monkey -p com.tencent.tmgp.sgame
            方式2(am start). start_app(package_name, activity)
            获得Activity的方法`adb -s 127.0.0.1:5565 shell dumpsys package com.tencent.tmgp.sgame`有一个Activity Resolver Table
            Airtest代码中是 adb -s 127.0.0.1:5565  shell am start -n package_name/package_name.activity
            可并不是所有的app的启动都遵循这一原则,如
            "com.tencent.tmgp.sgame/SGameActivity",
            "com.tencent.gamehelper.smoba/com.tencent.gamehelper.biz.launcher.ui.SplashActivit
            所以如果相同方式2，还是要修改Airtest的代码，变为package_name/activity
            综合上述原因，还是采取方式1, 添加`--pct-syskeys 0`
            虽然start_app(self.APPID)也能启动, 但是要修改代码airtest/core/android/adb.py,
            即使用start_app(self.APPID,Activity)就不用修改代码了
            """
            args_list = list(args)
            if args_list and "SYS_KEYS has no physical keys but with factor" in errormessgae:
                args_list = list(args)
                args_list[0] = str(args_list[0])+" --pct-syskeys 0"
                args = args_list
                TimeECHO(prefix+f"{fun_name(1)} with {args_list[0]}")
            if "device offline" in errormessgae:
                TimeECHO(prefix+"ADB device offline")
                return result
        # ......
        try:
            result = True
            start_app_o(*args, **kwargs)
        except:
            traceback.print_exc()
            TimeECHO(f"{prefix} 再次尝试{fun_name(1)}仍失败，检测是否没有开启ADB,或者重新启动ADB")
            result = False
    return result


def stop_app(*args, **kwargs):
    prefix = ""
    if "prefix" in kwargs:
        prefix = kwargs["prefix"]
        del kwargs["prefix"]
    try:
        result = True
        stop_app_o(*args, **kwargs)
    except:
        result = False
        TimeECHO(f"{prefix} {fun_name(1)} 失败")
        if not connect_status(prefix=prefix):
            TimeErr(f"{prefix} {fun_name(1)}连接不上设备")
            return result
        sleep(1)
        # 下面仍会输出信息，所以这里少报错，让屏幕更干净
        # traceback.print_exc()
        #
        try:
            result = True
            stop_app_o(*args, **kwargs)
        except:
            traceback.print_exc()
            TimeECHO(f"{prefix} 再次尝试{fun_name(1)}仍失败")
            result = False
    return result


def Template(*args, **kwargs):
    # 在这里修改args和kwargs，例如针对kwargs中的key进行添加内容
    dirname = "assets"
    if "dirname" in kwargs:
        dirname = kwargs["dirname"]
        del kwargs["dirname"]
    # 将args转换为列表以进行修改
    args_list = list(args)
    if args_list and "png" in args_list[0]:
        filename = os.path.join(dirname, args_list[0].lstrip('/'))
        if os.path.exists(filename):
            args_list[0] = os.path.join(dirname, args_list[0].lstrip('/'))
        else:
            TimeErr(f"不存在{filename}")
            filename = args_list[0]
            if not os.path.exists(filename):
                TimeErr(f"不存在{filename}")
        args = args_list
    # 调用Template_o函数，传入修改后的参数
    return Template_o(*args, **kwargs)


class DQWheel:
    def __init__(self, var_dict_file='var_dict_file.txt', prefix="", mynode=-10, totalnode=-10, 容器优化=False):
        self.timedict = {}
        self.容器优化 = 容器优化
        self.辅助同步文件 = "NeedRebarrier.txt"
        self.mynode = mynode
        self.totalnode = totalnode
        self.totalnode_bak = totalnode
        self.prefix = (f"({mynode})" if mynode >= 0 else "")+prefix
        #
        self.barrierlimit = 60*20  # 同步最大时长
        self.filelist = []  # 建立的所有文件，用于后期clear
        self.var_dict_file = var_dict_file
        self.var_dict = self.read_dict(self.var_dict_file)
        self.savepos = True
        # 子程序运行次数
        self.calltimes_dict = {}
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
        if len(timekey) == 0:
            timekey = "none"
        if not timekey in self.timedict.keys():
            init = True
        if init:
            self.timedict[timekey] = time.time()
            return False
        else:
            if time.time()-self.timedict[timekey] > limit:
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
        f = open(filename, 'w', encoding='utf-8')
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
        if not os.path.exists(filename):
            TimeECHO(self.prefix+"不存在["+filename+"]")
            return [""]
        try:
            f = open(filename, 'r', encoding='utf-8')
            content = f.readlines()
            f.close()
            TimeECHO(self.prefix+"Read["+filename+"]成功")
            return content
        except:
            traceback.print_exc()
            TimeECHO(self.prefix+"Read["+filename+"]失败")
            return [""]

    #
    def touch同步文件(self, 同步文件=""):
        if len(同步文件) > 1:
            同步文件 = 同步文件
        else:
            同步文件 = self.辅助同步文件 if self.totalnode_bak > 1 else self.独立同步文件
        if self.存在同步文件(同步文件):
            TimeECHO(f"{self.prefix}不再创建[{同步文件}]")
            return True
        TimeECHO(f">{self.prefix}"*10)
        TimeECHO(self.prefix+f"创建同步文件[{同步文件}]")
        self.touchfile(同步文件)
        TimeECHO(f"<{self.prefix}"*10)
        # 该文件不添加到列表,仅在成功同步后才删除
        # self.filelist.append(self.辅助同步文件)
        return True

    def 存在同步文件(self, 同步文件=""):
        if len(同步文件) > 1:
            if os.path.exists(同步文件):
                TimeECHO(self.prefix+f"存在同步文件[{同步文件}]")
                return True
            else:
                return False
        # 只要是总结点数大于1,无论当前是否组队都判断辅助同步文件
        if self.totalnode_bak > 1 and os.path.exists(self.辅助同步文件):
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
    # read_dict 不仅适合保存字典,而且适合任意的变量类型

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
    # save_dict 不仅适合保存字典,而且适合任意的变量类型

    def save_dict(self, var_dict, var_dict_file="position_dict.txt"):
        global 辅助
        # if 辅助: return True
        import pickle
        f = open(var_dict_file, "wb")
        pickle.dump(var_dict, f)
        f.close()
    # bcastvar 不仅适合保存字典,而且适合任意的变量类型

    def bcastvar(self, mynode, totalnode, var, name="bcastvar"):
        if totalnode < 2:
            return var
        dict_file = ".tmp."+name+".txt"
        if mynode == 0:
            self.save_dict(var, dict_file)
        self.barriernode(mynode, totalnode, "bcastvar."+name)
        if self.存在同步文件():
            return var
        #
        var_new = self.read_dict(dict_file)
        #
        return var_new

    def uniq_Template_array(self, arr):
        if not arr:  # 如果输入的列表为空
            return []
        #
        seen = set()
        unique_elements = []
        for item in arr:
            if item.filepath not in seen:
                unique_elements.append(item)
                seen.add(item.filepath)
        return unique_elements

    def 存在任一张图(self, array, strinfo=""):
        array = self.uniq_Template_array(array)
        判断元素集合 = array
        strinfo = strinfo if len(strinfo) > 0 else "图片"
        if strinfo in self.calltimes_dict.keys():
            self.calltimes_dict[strinfo] = self.calltimes_dict[strinfo]+1
        else:
            self.calltimes_dict[strinfo] = 1
        strinfo = f"第[{self.calltimes_dict[strinfo]}]次寻找{strinfo}"
        length = len(判断元素集合)
        for idx, i in enumerate(判断元素集合):
            TimeECHO(self.prefix+f"{strinfo}({idx+1}/{length}):{i}")
            if exists(i, prefix=self.prefix):
                TimeECHO(self.prefix+f"{strinfo}成功:{i}")
                # 交换元素位置
                判断元素集合[0], 判断元素集合[idx] = 判断元素集合[idx], 判断元素集合[0]
                return True, 判断元素集合
        return False, 判断元素集合

    def existsTHENtouch(self, png=Template(r"tpl_target_pos.png"), keystr="", savepos=False):
        savepos = savepos and len(keystr) > 0 and self.savepos
        #
        if self.connecttimes > self.connecttimesMAX:  # 大概率连接失败了,判断一下
            if connect_status(times=max(2, self.connecttimesMAX-self.connecttimes+10), prefix=self.prefix):  # 出错后降低判断的次数
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
        pos = exists(png, prefix=self.prefix)
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
    def LoopTouch(self, png=Template(r"tpl_target_pos.png"), keystr="", limit=0, loop=10, savepos=False):
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
        if exists(png, prefix=self.prefix):
            TimeErr(self.prefix+keystr+"图片仍存在")
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
        else:
            return True
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

    def time_getweek(self):
        return datetime.now(eastern_eight_tz).weekday()
    # return 0 - 6

    def hour_in_span(self, startclock=0, endclock=24, hour=None):
        if not hour:
            hour, minu, sec = self.time_getHMS()
            hour = hour + minu/60.0+sec/60.0/60.0
        startclock = (startclock+24) % 24
        endclock = (endclock+24) % 24
        
        # 不跨越午夜的情况[6,23]
        if startclock <= endclock:
            left = 0 if startclock <= hour <= endclock else self.left_hour(startclock, hour)
        # 跨越午夜的情况[23,6], 即[6,23]不对战
        else:
            left = self.left_hour(startclock, hour) if endclock < hour < startclock else 0
        return left

    def left_hour(self, endtime=24, hour=None):
        if not hour:
            hour, minu, sec = self.time_getHMS()
            hour = hour + minu/60.0+sec/60.0/60.0
        left = (endtime+24-hour) % 24
        return left

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
    def __init__(self, 设备类型=None, mynode=0, totalnode=1, LINK="Android:///"+"127.0.0.1:"+str(5555)):
        # 控制端
        self.控制端 = sys.platform.lower()
        # 避免和windows名字接近
        self.控制端 = "macos" if "darwin" in self.控制端 else self.控制端
        #
        # 客户端
        self.device = None
        self.LINK = LINK
        self.LINKport = self.LINK.split(":")[-1]  # port
        # (USB连接时"Android:///id",没有端口
        self.LINKport = "" if "/" in self.LINKport else self.LINKport
        self.LINKtype = self.LINK.split(":")[0].lower()  # android, ios
        self.LINKhead = self.LINK[:-len(self.LINKport)-1] if len(self.LINKport) > 0 else self.LINK  # ios:///ip
        self.LINKURL = self.LINK.split("/")[-1]  # ip:port
        self.设备类型 = 设备类型.lower() if 设备类型 else self.LINKtype
        #
        self.adb_path = "adb"
        if "android" in self.设备类型:
            from airtest.core.android import adb
            self.ADB = adb.ADB()
            self.adb_path = self.ADB.adb_path
        # 不同客户端对重启的适配能力不同
        if "ios" in self.设备类型:
            self.客户端 = "ios"
        elif "win" in self.控制端 and "127.0.0.1" in self.LINK:
            # 可以通过cmd控制模拟器: f"start /MIN C:\Progra~1\BlueStacks_nxt\HD-Player.exe --instance {instance}" (windows通用，不运行期间可彻底关闭模拟器，省电)
            # 也可以adb reboot控制模拟器(安卓通用，但是BlueStack模拟器不支持)
            # 通过是否运行多开管理，来判断是否使用模拟器
            # LD模拟器支持adb reboot重启模拟器
            BluePID = 0
            LdPID = 0
            # 模拟器启动后的窗口的名字
            self.win_WindowsName = []
            # 模拟器内部的名字(快捷方式中可以查看到)
            self.win_InstanceName = []
            if os.path.exists(os.path.join(BlueStackdir,"HD-MultiInstanceManager.exe")):
                BluePID=getpid_win(IMAGENAME="HD-MultiInstanceManager.exe",key="BlueStacks")
            if os.path.exists(os.path.join(LDPlayerdir,"dnmultiplayer.exe")):
                 LdPID=getpid_win(IMAGENAME="dnmultiplayer.exe",key="dnmultiplayer")
            if BluePID > 0:#
                self.客户端 = "win_BlueStacks"
                Instance = ["", "1", "2", "3", "4", "5"]
                for i in Instance:
                    if len(i) == 0:
                        self.win_WindowsName.append(f"BlueStacks App Player")
                        # 引擎, Nougat64,Nougat32,Pi64
                        self.win_InstanceName.append(f"--instance Nougat32")
                    else:
                        self.win_WindowsName.append(f"BlueStacks App Player {i}")
                        self.win_InstanceName.append(f"--instance Nougat32_{i}")
                #
            elif LdPID > 0:#
                self.客户端 = "win_LD"
                # LD多开模拟器的ID, 通过添加桌面快捷方式可以获取
                Instance = ["0", "1", "2", "3", "4", "5"]
                for i in Instance:
                    self.win_InstanceName.append(f"index={i}")
                    if i == "0":
                        self.win_WindowsName.append(f"雷电模拟器")
                    else:
                        self.win_WindowsName.append(f"雷电模拟器-{i}")
                # LDPlayer 也支持 self.客户端="FULL_ADB" 的模式
                # 但是需要提前开启模拟器
            else:
                # self.客户端="FULL_ADB
                # 利用adb reboot控制，但是在一些机器上会卡住或者直接关机
                #
                self.客户端 = "RemoteAndroid"
                # 暂时通过 adb disconnect的方式控制
        elif "linux" in self.控制端 and "127.0.0.1" in self.LINK:  # Linux + docker
            if os.path.exists("/home/cndaqiang/builddocker/redroid/8arm0"):
                self.客户端 = "lin_docker"
        elif len(self.LINKport) > 0:  # 通过网络访问的安卓设备
            self.客户端 = "RemoteAndroid"
        else:
            self.客户端 = "USBAndroid"
        #
        self.mynode = mynode
        self.prefix = f"({self.mynode})"
        self.totalnode = totalnode
        #
        self.实体终端 = False
        self.实体终端 = "mac" in self.控制端 or "ios" in self.设备类型
        self.容器优化 = "linux" in self.控制端 and "android" in self.设备类型
        #
        TimeECHO(self.prefix+f"控制端({self.控制端})")
        TimeECHO(self.prefix+f"客户端({self.客户端})")
        TimeECHO(self.prefix+f"ADB =({self.adb_path})")
        TimeECHO(self.prefix+f"LINK({self.LINK})")
        TimeECHO(self.prefix+f"LINKhead({self.LINKhead})")
        TimeECHO(self.prefix+f"LINKtype({self.LINKtype})")
        TimeECHO(self.prefix+f"LINKURL({self.LINKURL})")
        TimeECHO(self.prefix+f"LINKport({self.LINKport})")
        #
        self.连接设备()

    def 连接设备(self, times=1, timesMax=2):
        """
        # 尝试连接timesMax+1次,当前是times次
        """
        self.device = False
        TimeECHO(self.prefix+f"{self.LINK}:开始第{times}/{timesMax+1}次连接")
        try:
            self.device = connect_device(self.LINK)
            if self.device:
                TimeECHO(self.prefix+f"{self.LINK}:链接成功")
                return True
        except:
            if times == timesMax+1:
                traceback.print_exc()
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
        command = []
        TimeECHO(self.prefix+f"尝试启动设备中...")
        if self.客户端 == "ios":
            if "mac" in self.控制端:
                TimeECHO(self.prefix+f"测试本地IOS打开中")
            else:
                TimeECHO(self.prefix+f"当前模式无法打开IOS")
                return False
            # 获得运行的结果
            result = getstatusoutput("tidevice list")
            if 'ConnectionType.USB' in result[1]:
                # wdaproxy这个命令会同时调用xctest和relay，另外当wda退出时，会自动重新启动xctest
                # tidevice不支持企业签名的WDA
                self.LINKport = str(int(self.LINKport)+1)
                self.LINK = self.LINKhead+":"+self.LINKport
                command.append(f"tidevice $(cat para.txt) wdaproxy -B  com.facebook.WebDriverAgentRunner.cndaqiang.xctrunner --port {self.LINKport} > tidevice.result.txt 2 > &1 &")
                sleep(20)
            else:
                TimeErr(self.prefix+": tidevice list 无法找到IOS设备重启失败")
                return False
        # android
        elif self.客户端 == "win_BlueStacks":
            instance = self.win_InstanceName[self.mynode]
            command.append(os.path.join(BlueStackdir,"HD-Player.exe")+" "+instance)
        elif self.客户端 == "win_LD":
            instance = self.win_InstanceName[self.mynode]
            command.append(os.path.join(LDPlayerdir,"dnplayer.exe")+" "+instance)
        elif self.客户端 == "FULL_ADB":
            # 通过reboot的方式可以实现重启和解决资源的效果
            command.append(f"{self.adb_path} connect "+self.LINKURL)
            command.append(f"{self.adb_path} -s "+self.LINKURL+" reboot")
        elif self.客户端 == "lin_docker":
            虚拟机ID = f"androidcontain{self.mynode}"
            command.append(f"docker restart {虚拟机ID}")
        elif self.客户端 == "RemoteAndroid":
            command.append(f"{self.adb_path} connect "+self.LINKURL)
        elif self.客户端 == "USBAndroid":
            result = getstatusoutput("adb devices")
            if self.LINKURL in result[1]:
                command.append(f"{self.adb_path} -s "+self.LINKURL+" reboot")
            else:
                TimeECHO(self.prefix+f"没有找到USB设备{self.LINKURL}\n"+result[1])
                return False
        else:
            TimeECHO(self.prefix+f"未知设备类型")
            return False
        # 开始运行
        exit_code = run_command(command=command, prefix=self.prefix)
        if exit_code == 0:
            TimeECHO(self.prefix+f"启动成功")
            return True
        else:
            TimeErr(self.prefix+f"启动失败")
            return False

    def 关闭设备(self):
        command = []
        TimeECHO(self.prefix+f"尝试关闭设备中...")
        if self.客户端 == "ios":
            if "mac" in self.控制端:
                TimeECHO(self.prefix+f"测试本地IOS关闭中")
                command.append("tidevice reboot")
            else:
                TimeECHO(self.prefix+f"当前模式无法关闭IOS")
                return False
        # android
        elif self.客户端 == "win_BlueStacks":
            # 尝试获取PID
            PID = getpid_win(IMAGENAME="HD-Player.exe", key=self.win_WindowsName[self.mynode])
            # BlueStacks App Player 3
            if PID > 0:
                command.append(f'taskkill /F /FI "PID eq {str(PID)}"')
            else:  # 关闭所有虚拟机，暂时用不到
                command.append('taskkill /f /im HD-Player.exe')
        elif self.客户端 == "win_LD":
            # 尝试获取PID
            PID = getpid_win(IMAGENAME="dnplayer.exe", key=self.win_WindowsName[self.mynode])
            if PID > 0:
                command.append(f'taskkill /F /FI "PID eq {str(PID)}"')
            else:
                # 关闭所有虚拟机，暂时用不到
                #command.append('taskkill /f /im dnplayer.exe')
                # 通过reboot的方式可以实现重启和解决资源的效果
                # LDPlayer支持adb reboot,👍
                command.append(f"{self.adb_path} connect "+self.LINKURL)
                command.append(f"{self.adb_path} -s "+self.LINKURL+" reboot")
        elif self.客户端 == "FULL_ADB":
            # 通过reboot的方式可以实现重启和解决资源的效果
            command.append(f"{self.adb_path} connect "+self.LINKURL)
            command.append(f"{self.adb_path} -s "+self.LINKURL+" reboot")
        elif self.客户端 == "lin_docker":
            虚拟机ID = f"androidcontain{self.mynode}"
            command.append(f"docker stop {虚拟机ID}")
        elif self.客户端 == "RemoteAndroid":
            command.append(f"{self.adb_path} disconnect "+self.LINKURL)
        elif self.客户端 == "USBAndroid":
            result = getstatusoutput("adb devices")
            if self.LINKURL in result[1]:
                command.append(f"{self.adb_path} -s "+self.LINKURL+" reboot")
            else:
                TimeECHO(self.prefix+f"没有找到USB设备{self.LINKURL}\n"+result[1])
                return False
        else:
            TimeECHO(self.prefix+f"未知设备类型")
            return False
        # 开始运行
        exit_code = run_command(command=command, prefix=self.prefix, sleeptime=60)
        if exit_code == 0:
            TimeECHO(self.prefix+f"关闭成功")
            return True
        else:
            TimeECHO(self.prefix+f"关闭失败")
            return False

    def 重启设备(self, sleeptime=0):
        TimeECHO(self.prefix+f"重新启动({self.LINK})")
        self.关闭设备()
        sleeptime = max(10, sleeptime-60)
        printtime = max(30, sleeptime/10)
        TimeECHO(self.prefix+"sleep %d min" % (sleeptime/60))
        for i in np.arange(int(sleeptime/printtime)):
            TimeECHO(self.prefix+f"...taskkill_sleep: {i}", end='\r')
            sleep(printtime)
        self.启动设备()
        self.连接设备()


class appOB:
    def __init__(self, prefix="", APPID="", big=False, device=None):
        self.prefix = prefix
        self.APPID = APPID
        self.Activity = None if "/" not in self.APPID else self.APPID.split("/")[1]
        self.APPID = self.APPID.split("/")[0]
        self.device = device
        self.big = big  # 是不是大型的程序, 容易卡顿，要多等待一会
    #

    def 打开APP(self):
        if self.Activity:
            TimeECHO(self.prefix+f"打开APP[{self.APPID}/{self.Activity}]中")
            启动成功 = start_app(self.APPID, self.Activity)
        else:
            TimeECHO(self.prefix+f"打开APP[{self.APPID}]中")
            启动成功 = start_app(self.APPID, prefix=self.prefix)
        if not 启动成功:
            TimeErr(self.prefix+"打开失败,可能失联")
            return False
        else:
            sleep(20)
        return True

    def 重启APP(self, sleeptime=0):
        TimeECHO(self.prefix+f"重启APP中")
        self.关闭APP()
        sleep(10)
        sleeptime = max(10, sleeptime)  # 这里的单位是s
        printtime = max(30, sleeptime/10)
        if sleeptime > 60*60 and self.device:  # >1h
            self.device.重启设备(sleeptime)
        else:
            TimeECHO(self.prefix+"sleep %d min" % (sleeptime/60))
            nstep = int(sleeptime/printtime)
            for i in np.arange(nstep):
                TimeECHO(self.prefix+f"...taskkill_sleep: {i}/{nstep}", end='\r')
                sleep(printtime)
        TimeECHO(self.prefix+f"打开程序")
        if self.打开APP():
            if self.big:
                TimeECHO(self.prefix+f"打开程序成功,sleep60*2")
                sleep(60*2)
            return True
        else:
            TimeECHO(self.prefix+f"打开程序失败")
            return False
    #

    def 关闭APP(self):
        TimeECHO(self.prefix+f"关闭APP[{self.APPID}]中")
        if not stop_app(self.APPID, prefix=self.prefix):
            TimeErr(self.prefix+"关闭失败,可能失联")
            return False
        else:
            sleep(5)
            return True


class wzyd_libao:
    def __init__(self, prefix="0", 设备类型="android", Tool=None, 初始化检查=False):
        # 默认只创建对象, 开启初始化检查才会检查
        self.体验币成功 = False
        self.营地活动 = True
        self.设备类型 = 设备类型
        # 这里prefix+,是用于输出到屏幕
        # 输入的prefix是mynode
        self.prefix = f"({prefix})王者营地"
        self.APPID = "com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.gamehelper.smoba"
        # com.tencent.gamehelper.smoba/com.tencent.gamehelper.biz.launcher.ui.SplashActivity
        self.APPOB = appOB(prefix=self.prefix, APPID=self.APPID)
        self.IOS = "ios" in self.设备类型
        #
        self.营地初始化FILE = self.prefix+".初始化.txt"
        self.营地需要登录FILE = self.prefix+".需要登录.txt"
        # 使用输入的prefix,才可以用一套同步文件
        self.Tool = DQWheel(prefix=self.prefix, var_dict_file="."+self.prefix+"var_dict_file.txt") if Tool == None else Tool
        # 这两个图标会根据活动变化,可以用下面的注入替换
        self.个人界面图标 = Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960))
        self.游戏界面图标 = Template(r"tpl1704381547456.png", record_pos=(0.187, 0.726), resolution=(540, 960))
        self.社区界面图标 = Template(r"tpl1717046076553.png", record_pos=(-0.007, 0.759), resolution=(540, 960))
        self.每日福利图标 = Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960))
        self.一键领取按钮 = Template(r"tpl1706338731419.png", record_pos=(0.328, -0.365), resolution=(540, 960))
        self.赛事入口 = Template(r"tpl1717046009399.png", record_pos=(-0.269, -0.804), resolution=(540, 960), target_pos=6)
        self.资讯入口 = Template(r"tpl1717046009399.png", record_pos=(-0.269, -0.804), resolution=(540, 960))
        if self.IOS:
            self.每日福利图标 = Template(r"tpl1700272452555.png", record_pos=(-0.198, -0.002), resolution=(640, 1136))
        self.营地大厅元素 = []
        self.营地大厅元素.append(Template(r"tpl1708393295383.png", record_pos=(0.011, -0.8), resolution=(540, 960)))
        self.营地大厅元素.append(self.个人界面图标)
        self.营地大厅元素.append(self.游戏界面图标)
        self.营地大厅元素.append(self.每日福利图标)
        self.营地登录元素 = []
        self.营地登录元素.append(Template(r"tpl1708393355383.png", record_pos=(-0.004, 0.524), resolution=(540, 960)))
        self.营地登录元素.append(Template(r"tpl1708393749272.png", record_pos=(-0.002, 0.519), resolution=(540, 960)))
        #
        self.初始化成功 = False
        if 初始化检查:
            self.初始化成功 = self.营地初始化(初始化检查=初始化检查)
            if 初始化检查:
                self.APPOB.关闭APP()

    def 判断营地大厅中(self):
        #
        self.营地大厅元素.append(self.个人界面图标)
        self.营地大厅元素.append(self.游戏界面图标)
        self.营地大厅元素.append(self.每日福利图标)
        存在, self.营地大厅元素 = self.Tool.存在任一张图(self.营地大厅元素, "营地大厅元素")
        return 存在
    #

    def 判断营地登录中(self):
        存在, self.营地登录元素 = self.Tool.存在任一张图(self.营地登录元素, "营地登录元素")
        return 存在
    #
    #
    # 用于更新上层调用参数,是不是领取礼包

    def 营地初始化(self, 初始化检查=False):
        # 判断网络情况
        if not connect_status(prefix=self.prefix):
            TimeECHO(self.prefix+":营地暂时无法触摸,返回")
            if 初始化检查:
                return True
            return False
        # 打开APP
        if not self.APPOB.重启APP(10):
            TimeECHO(self.prefix+":营地无法打开,返回")
            self.APPOB.关闭APP()
            return False
        sleep(20)  # 等待营地打开
        run_class_command(self=self, prefix=self.prefix, command=self.Tool.readfile(self.营地初始化FILE))
        #
        # 判断营地是否登录的界面
        if self.判断营地登录中():
            TimeECHO(self.prefix+":检测到营地登录界面,不领取礼包")
            self.Tool.touchfile(self.营地需要登录FILE)
            self.APPOB.关闭APP()
            return False
        # 这里很容易出问题，主页的图标变来变去
        if not self.判断营地大厅中():
            TimeECHO(self.prefix+":营地未知原因没能进入大厅,再次尝试")
            self.APPOB.重启APP(40)
            if not self.判断营地大厅中():
                self.Tool.touchfile(self.营地需要登录FILE)
                self.APPOB.关闭APP()
                self.Tool.timedict["检测营地登录"] = 0  # 下次继续检查
                return False
        # 前面的都通过了,判断成功
        if 初始化检查:
            self.Tool.removefile(self.营地需要登录FILE)
        #
        return True

    def STOP(self):
        self.APPOB.关闭APP()
    #

    def RUN(self):
        #
        self.Tool.removefile(self.Tool.独立同步文件)
        #
        if os.path.exists(self.营地需要登录FILE):
            if self.Tool.timelimit(timekey="检测营地登录", limit=60*60*8, init=False):
                TimeECHO(self.prefix+f"存在[{self.营地需要登录FILE}],重新检测登录状态")
                self.Tool.removefile(self.营地需要登录FILE)
                self.营地初始化(初始化检查=False)
        #
        if os.path.exists(self.营地需要登录FILE):
            TimeECHO(self.prefix+f"检测到{self.营地需要登录FILE}, 不领取礼包")
            return False
        #
        self.初始化成功 = self.营地初始化(初始化检查=False)
        if not self.初始化成功:
            TimeECHO(self.prefix+":营地初始化失败")
            self.APPOB.关闭APP()
            return False
        #
        self.营地任务_浏览资讯()
        self.营地任务_观看赛事()
        self.营地任务_圈子签到()
        #
        # 体验服只有安卓客户端可以领取
        if not self.IOS:
            self.体验服礼物()
        self.每日签到任务()
        self.营地币兑换碎片()
        self.营地战令经验()
        self.APPOB.关闭APP()
        return True

    def 营地任务_观看赛事(self, times=1):
        #
        if self.Tool.存在同步文件():
            return True
        #
        keystr = "营地任务_观看赛事"
        if times == 1:
            self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(self.prefix+f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.赛事入口, self.prefix+"赛事入口", savepos=True)
        去直播间 = Template(r"tpl1717046024359.png", record_pos=(0.033, 0.119), resolution=(540, 960))
        for i in range(5):
            if self.Tool.existsTHENtouch(去直播间, self.prefix+"去直播间图标"):
                sleep(50)
                return True
        TimeECHO(self.prefix+f"没进入直播间")
        return self.营地任务_观看赛事(times)

    def 营地任务_圈子签到(self, times=1):
        #
        if self.Tool.存在同步文件():
            return True
        #
        keystr = "营地任务_圈子签到"
        if times == 1:
            self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(self.prefix+f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.社区界面图标, self.prefix+"社区界面图标", savepos=True)
        sleep(10)
        #
        圈子图标 = Template(r"tpl1717047527808.png", record_pos=(-0.254, -0.809), resolution=(540, 960))
        if not self.Tool.existsTHENtouch(圈子图标, self.prefix+"圈子图标", savepos=True):
            TimeECHO(self.prefix+f"找不到圈子图标")
            return self.营地任务_圈子签到(times)
        #
        # 需要提前自己峡谷互助小组圈子
        峡谷互助小组圈子 = Template(r"tpl1717046264179.png", record_pos=(-0.178, -0.511), resolution=(540, 960))
        进入小组 = False
        for i in range(5):
            if self.Tool.existsTHENtouch(峡谷互助小组圈子, self.prefix+"峡谷互助小组圈子"):
                sleep(6)
                进入小组 = True
        if not 进入小组:
            TimeECHO(self.prefix+f"找不到互助小组圈子")
            return self.营地任务_圈子签到(times)
        圈子签到图标 = Template(r"tpl1717046286604.png", record_pos=(0.393, -0.3), resolution=(540, 960))
        签到成功图标 = Template(r"tpl1717047898461.png", record_pos=(-0.004, 0.237), resolution=(540, 960))
        if self.Tool.existsTHENtouch(圈子签到图标, "圈子签到图标"):
            if self.Tool.existsTHENtouch(签到成功图标, "签到成功图标"):
                TimeECHO(self.prefix+f"签到成功")
        else:
            TimeECHO(self.prefix+f"可能签到过了")
        return True

    def 营地任务_浏览资讯(self, times=1):
        #
        if self.Tool.存在同步文件():
            return True
        #
        keystr = "营地任务_浏览资讯"
        if times == 1:
            self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(self.prefix+f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        #
        self.Tool.existsTHENtouch(self.资讯入口, self.prefix+"资讯入口.推荐", savepos=True)
        资讯入口图标 = Template(r"tpl1717046344191.png", record_pos=(-0.422, -0.37), resolution=(540, 960))
        if not self.Tool.existsTHENtouch(资讯入口图标, self.prefix+"资讯入口图标", savepos=True):
            TimeECHO(self.prefix+f"找不到资讯入口图标")
            return self.营地任务_浏览资讯(times)
        点赞图标 = Template(r"tpl1717046512030.png", record_pos=(0.424, 0.02), resolution=(540, 960))
        pos = self.Tool.var_dict[self.prefix+"资讯入口图标"]
        # 开始滑动点赞
        for i in range(100):
            sleep(1)
            if self.Tool.existsTHENtouch(点赞图标, self.prefix+"点赞图标", savepos=False):
                sleep(0.5)
            else:
                sleep(1)
            TimeECHO(self.prefix+f"浏览资讯中{i}")
            swipe(pos, vector=[0.0, -0.5])
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(self.prefix+f"浏览资讯时间到")
                return
        return

    def 营地战令经验(self, times=1):
        #
        # 第一次，需要手动点击一下，开启战令
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地战令经验", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地战令经验", limit=60*5, init=False):
                TimeECHO(self.prefix+f"营地战令经验{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"营地战令经验{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.游戏界面图标, self.prefix+"游戏界面图标", savepos=True)
        sleep(5)
        #
        正式服判断图标 = Template(r"tpl1715609808723.png", record_pos=(-0.217, -0.044), resolution=(540, 960))
        正式服大头图标 = Template(r"tpl1715610763289.png", record_pos=(-0.281, -0.8), resolution=(540, 960))
        正式服入口 = False
        for i in range(5):
            if exists(正式服判断图标):
                正式服入口 = True
                break
            # 不同的账号，显示的数目不一样多，没办法savepos
            self.Tool.existsTHENtouch(正式服大头图标, "正式服大头图标", savepos=False)
        if not 正式服入口:
            TimeECHO(self.prefix+f"没有找到正式服入口,有可能营地有更新")
            return self.营地战令经验(times)
        # 点开工具箱
        self.Tool.existsTHENtouch(正式服判断图标, self.prefix+"正式服工具图标", savepos=True)
        sleep(10)
        战令入口 = Template(r"tpl1715609828196.png", record_pos=(0.209, -0.004), resolution=(540, 960))
        self.Tool.existsTHENtouch(战令入口, self.prefix+"战令入口", savepos=True)
        sleep(10)
        #
        战令页面元素 = []
        战令页面元素.append(Template(r"tpl1715609862801.png", record_pos=(0.131, 0.743), resolution=(540, 960)))
        战令页面元素.append(Template(r"tpl1716804327622.png", record_pos=(0.0, 0.156), resolution=(540, 960)))
        战令页面元素.append(Template(r"tpl1716804333697.png", record_pos=(0.352, 0.739), resolution=(540, 960)))
        战令页面元素.append(Template(r"tpl1716804348346.png", record_pos=(-0.281, -0.7), resolution=(540, 960)))
        战令页面元素.append(Template(r"tpl1716804366593.png", record_pos=(-0.083, 0.543), resolution=(540, 960)))
        存在, 战令页面元素 = self.Tool.存在任一张图(战令页面元素, "营地.战令页面元素")
        if not 存在:
            sleep(20)
            存在, 战令页面元素 = self.Tool.存在任一张图(战令页面元素, "营地.战令页面元素")
            if not 存在:
                TimeECHO(self.prefix+f"没找到战令页面")
                return self.营地战令经验(times)
        战令任务 = Template(r"tpl1715609874404.png", record_pos=(-0.25, -0.706), resolution=(540, 960))
        self.Tool.existsTHENtouch(战令任务, self.prefix+"战令任务", savepos=True)
        一键领取 = Template(r"tpl1715610610922.png", record_pos=(0.337, -0.18), resolution=(540, 960))
        self.Tool.existsTHENtouch(一键领取, self.prefix+"一键领取战令经验", savepos=True)

    def 体验服礼物(self, times=1):
        #
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=False):
                TimeECHO(self.prefix+f"体验服礼物{times}超时退出")
                return False
        #
        TimeECHO(self.prefix+f"体验币{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
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
            # 不同的账号，显示的数目不一样多，没办法savepos
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
            TimeECHO(self.prefix+":没进入奖励兑换页面")
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
            TimeECHO(self.prefix+":成功领取")
        else:
            TimeECHO(self.prefix+":领取过了/体验币不够")
        return
        #

    def 每日签到任务(self, times=1):
        TimeECHO(self.prefix+f"营地每日签到{times}")
        #
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=False):
                TimeECHO(self.prefix+f"营地每日签到{times}超时退出")
                return False
        #
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 5:
            return False
        # 每日签到
        self.APPOB.重启APP(10)
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
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=False):
                TimeECHO(self.prefix+f"营地币兑换碎片{times}超时退出")
                return False
        #
        times = times+1
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        self.APPOB.重启APP(10)
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
                TimeECHO(self.prefix+f":寻找兑换页面中{i}")
        if not pos:
            TimeECHO(self.prefix+":没进入营地币兑换页面")
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
            TimeECHO(self.prefix+":没找到营地币")
            return self.营地币兑换碎片(times)
        touch(奖励位置)
        self.Tool.existsTHENtouch(Template(r"tpl1699873472386.png", record_pos=(0.163, 0.107), resolution=(540, 960)))
        self.Tool.existsTHENtouch(Template(r"tpl1699873480797.png", record_pos=(0.163, 0.104), resolution=(540, 960)))


class wzry_runinfo:
    # 备注
    # 运行参数信息
    # 主要用于保存上一步的运行信息,对本步进行调整
    def __init__(self):
        self.组队模式 = False
        self.房主 = True
        self.对战模式 = "5v5匹配"
        self.限时组队时间 = 7
        self.runstep = -1
        self.jinristep = -1
        self.青铜段位 = False
        self.标准模式 = False
        self.触摸对战 = False
        self.标准触摸对战 = False
        self.prefix = ""

    def printinfo(self):
        TimeECHO(f"{self.prefix} RUNINFO")
        TimeECHO(f"{self.prefix} 组队模式 = {str(self.组队模式)}")
        TimeECHO(f"{self.prefix} 房主 = {str(self.房主)}")
        TimeECHO(f"{self.prefix} 对战模式 = {str(self.对战模式)}")
        TimeECHO(f"{self.prefix} 限时组队时间 = {str(self.限时组队时间)}")
        TimeECHO(f"{self.prefix} runstep = {str(self.runstep)}")
        TimeECHO(f"{self.prefix} jinristep = {str(self.jinristep)}")
        TimeECHO(f"{self.prefix} 青铜段位 = {str(self.青铜段位)}")
        TimeECHO(f"{self.prefix} 标准模式 = {str(self.标准模式)}")
        TimeECHO(f"{self.prefix} 触摸对战 = {str(self.触摸对战)}")
        TimeECHO(f"{self.prefix} 标准触摸对战 = {str(self.标准触摸对战)}")

    def compare(self, other):
        if self.组队模式 != other.组队模式:
            TimeECHO(self.prefix+f"RUNINFO:组队模式变化->{str(self.组队模式)}")
            return False
        if self.对战模式 != other.对战模式:
            TimeECHO(self.prefix+f"RUNINFO:对战模式变化->{str(self.对战模式)}")
            return False
        # 对战模式没变时，模拟战不用判断了
        if "模拟战" in self.对战模式:
            return True
        if "5v5排位" in self.对战模式:
            return True
        if "5v5匹配" in self.对战模式:
            if self.青铜段位 == other.青铜段位:
                if self.标准模式 == other.标准模式:
                    return True
                else:
                    TimeECHO(self.prefix+f"RUNINFO:标准模式变化->{str(self.标准模式)}")
            else:
                TimeECHO(self.prefix+f"RUNINFO:青铜段位变化->{str(self.青铜段位)}")
                return False
        TimeECHO(self.prefix+f"RUNINFO:对战参数没有变化")
        return True


class wzry_figure:
    # 图片元素信息,
    # 方便更新,
    # 以及用于统一更新图片传递给所有进程
    def __init__(self, prefix="图片库", Tool=None):
        self.prefix = prefix
        self.Tool = DQWheel(prefix=self.prefix) if Tool == None else Tool
        # 一些图库, 后期使用图片更新
        self.网络不可用 = Template(r"tpl1720067196954.png", record_pos=(0.003, 0.045), resolution=(960, 540))
        self.登录界面开始游戏图标 = Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540), threshold=0.9)
        self.大厅对战图标 = Template(r"tpl1719454669981.png", record_pos=(-0.242, 0.145), resolution=(960, 540))
        self.大厅对战图标2 = Template(r"tpl1689666004542.png", record_pos=(-0.102, 0.145), resolution=(960, 540), threshold=0.9)
        self.大厅万象天工 = Template(r"tpl1719454683770.png", record_pos=(0.232, 0.144), resolution=(960, 540))
        self.大厅万象天工2 = Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540), threshold=0.9)
        self.大厅排位赛 = Template(r"tpl1720065349345.png", record_pos=(0.102, 0.144), resolution=(960, 540))
        self.进入排位赛 = Template(r"tpl1720065354455.png", record_pos=(0.29, 0.181), resolution=(960, 540))
        # 开始图标和登录图标等很接近, 不要用于房间判断
        self.房间中的开始按钮图标 = []
        self.房间中的开始按钮图标.append(Template(r"tpl1689666117573.png", record_pos=(0.096, 0.232), resolution=(960, 540)))
        # 新年活动结束时,替换一个常规的取消准备按钮
        self.房间中的取消按钮图标 = []
        self.房间中的取消按钮图标.append(Template(r"tpl1699179402893.png", record_pos=(0.098, 0.233), resolution=(960, 540), threshold=0.9))
        self.大厅元素 = []
        self.大厅元素.append(self.大厅对战图标)
        self.大厅元素.append(self.大厅万象天工)
        # self.大厅元素.append(self.大厅对战图标2)
        # self.大厅元素.append(self.大厅万象天工2)
        self.房间元素 = []
        self.房间元素.append(Template(r"tpl1690442701046.png", record_pos=(0.135, -0.029), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1700304317380.png", record_pos=(-0.38, -0.252), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1691463676972.png", record_pos=(0.356, -0.258), resolution=(960, 540)))
        self.房间元素.append(Template(r"tpl1700304304172.png", record_pos=(0.39, -0.259), resolution=(960, 540)))
        # 对战页面元素
        self.普攻 = Template(r"tpl1689666416575.png", record_pos=(0.362, 0.2), resolution=(960, 540), threshold=0.9)
        self.移动 = Template(r"tpl1702267006237.png", record_pos=(-0.327, 0.16), resolution=(960, 540))
        self.钱袋 = Template(r"tpl1719485696322.png", record_pos=(-0.469, -0.059), resolution=(960, 540), threshold=0.9)
        self.普攻S = [self.普攻]  # 其他特色的攻击图标
        self.移动S = [self.移动]  # 其他特色的移动图标
        self.装备S = []
        #
        self.普攻S.append(Template(r"tpl1719546715992.png", record_pos=(0.366, 0.196), resolution=(960, 540)))
        self.普攻S.append(Template(r"tpl1719546725396.png", record_pos=(0.37, 0.197), resolution=(960, 540)))
        self.普攻S.append(Template(r"tpl1719546735621.png", record_pos=(0.369, 0.199), resolution=(960, 540)))
        self.普攻S.append(Template(r"tpl1719546976757.png", record_pos=(0.368, 0.201), resolution=(960, 540)))
        self.普攻S.append(Template(r"tpl1719546988763.png", record_pos=(0.366, 0.2), resolution=(960, 540)))
        self.普攻S.append(Template(r"tpl1719547004757.png", record_pos=(0.365, 0.198), resolution=(960, 540)))
        #
        self.装备S.append(Template(r"tpl1709220117102.png", record_pos=(0.401, -0.198), resolution=(960, 540)))
        self.装备S.append(Template(r"tpl1719546874415.png", record_pos=(-0.403, -0.057), resolution=(960, 540)))
        #
        self.对战图片元素 = [self.钱袋]
        for i in self.普攻S[:1]:
            self.对战图片元素.append(i)
        for i in self.移动S:
            self.对战图片元素.append(i)
        # for i in self.装备S:
        #     self.对战图片元素.append(i)
        self.对战图片元素.append(Template(r"tpl1719546803645.png", record_pos=(-0.005, 0.223), resolution=(960, 540)))
        #
        self.友方血条 = []
        self.敌方血条 = []
        self.敌方血条.append(Template(r"tpl1720003668795.png", record_pos=(0.082, -0.195), resolution=(960, 540)))
        self.敌方血条.append(Template(r"tpl1720003679285.png", record_pos=(0.083, -0.193), resolution=(960, 540)))
        self.敌方血条.append(Template(r"tpl1720003823052.png", record_pos=(-0.128, -0.191), resolution=(960, 540)))
        self.友方血条.append(Template(r"tpl1720004138271.png", record_pos=(0.151, -0.121), resolution=(960, 540)))
        self.友方血条.append(Template(r"tpl1720004235372.png", record_pos=(-0.342, -0.051), resolution=(960, 540)))
        self.友方血条.append(Template(r"tpl1720004340139.png", record_pos=(0.007, -0.224), resolution=(960, 540)))
        #
        self.钱袋子_模拟战 = Template(r"tpl1690546610171.png", record_pos=(0.391, 0.216), resolution=(960, 540))
        self.刷新金币_模拟战 = Template(r"tpl1690547053276.png", record_pos=(0.458, -0.045), resolution=(960, 540))
        self.关闭钱袋子_模拟战 = Template(r"tpl1690547457483.png", record_pos=(0.392, 0.216), resolution=(960, 540))
        self.对战图片元素_模拟战 = [self.钱袋子_模拟战, self.刷新金币_模拟战, self.关闭钱袋子_模拟战]
        self.对战图片元素_模拟战.append(Template(r"tpl1690546926096.png", record_pos=(-0.416, -0.076), resolution=(960, 540)))
        self.对战图片元素_模拟战.append(Template(r"tpl1690547491681.png", record_pos=(0.471, 0.165), resolution=(960, 540)))
        self.对战图片元素_模拟战.append(Template(r"tpl1690552290188.png", record_pos=(0.158, 0.089), resolution=(960, 540)))
        # 登录关闭按钮
        self.王者登录关闭按钮 = []
        self.王者登录关闭按钮.append(Template(r"tpl1692947351223.png", record_pos=(0.428, -0.205), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1699616162254.png", record_pos=(0.38, -0.237), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540)))
        self.王者登录关闭按钮.append(Template(r"tpl1693271987720.png", record_pos=(0.428, -0.205), resolution=(960, 540), threshold=0.9))
        self.王者登录关闭按钮.append(Template(r"tpl1700294024287.png", record_pos=(0.465, -0.214), resolution=(1136, 640)))
        self.王者登录关闭按钮.append(Template(r"tpl1707232517229.png", record_pos=(0.394, -0.237), resolution=(960, 540)))
        self.王者登录关闭按钮.append(Template(r"tpl1719742718808.png", record_pos=(0.394, -0.241), resolution=(960, 540)))
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
        self.返回房间按钮 = Template(r"tpl1689667226045.png", record_pos=(0.079, 0.226), resolution=(960, 540), threshold=0.9)
        self.房间我知道了 = Template(r"tpl1707519287850.png", record_pos=(-0.006, 0.191), resolution=(960, 540))
        # 这些活动翻页元素一般只显示一次，新的账户每次进入房间都会提示
        self.房间翻页活动元素 = []
        self.房间翻页活动元素.append(Template(r"tpl1707519278270.png", record_pos=(0.014, -0.191), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1707784321085.png", record_pos=(-0.004, -0.219), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1707787106337.png", record_pos=(-0.001, -0.22), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1708654174076.png", record_pos=(-0.001, -0.22), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1708826597289.png", record_pos=(0.002, -0.219), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1708826597289.png", record_pos=(0.002, -0.219), resolution=(960, 540)))
        self.房间翻页活动元素.append(Template(r"tpl1708829601719.png", record_pos=(0.001, -0.22), resolution=(960, 540)))
        self.房主头像 = Template(r"tpl1716782981770.png", record_pos=(0.354, -0.164), resolution=(960, 540), target_pos=9)
        self.房主房间 = Template(r"tpl1700284856473.png", record_pos=(0.312, -0.17), resolution=(1136, 640), target_pos=2)
        #
        # 头像数据
        self.英雄_海诺 = Template(r"tpl1701750143194.png", record_pos=(-0.36, 0.135), resolution=(960, 540))
        self.英雄_牙 = Template(r"tpl1701436836229.png", record_pos=(0.107, -0.085), resolution=(1136, 640))
        self.英雄_太乙 = Template(r"tpl1690442560069.png", record_pos=(0.11, 0.025), resolution=(960, 540))
        self.英雄_鬼谷子 = Template(r"tpl1701759712161.png", record_pos=(0.203, 0.026), resolution=(1136, 640))
        self.英雄_云中 = Template(r"tpl1701750390892.png", record_pos=(-0.172, 0.24), resolution=(1136, 640))
        self.英雄_八戒 = Template(r"tpl1701573854122.png", record_pos=(0.297, 0.135), resolution=(1136, 640))
        self.参战英雄线路_dict = {}
        self.参战英雄头像_dict = {}
        self.参战英雄线路_dict[0] = Template(r"tpl1689665490071.png", record_pos=(-0.315, -0.257), resolution=(960, 540))
        self.参战英雄头像_dict[0] = self.英雄_八戒
        self.参战英雄线路_dict[1] = Template(r"tpl1689665455905.png", record_pos=(-0.066, -0.256), resolution=(960, 540))
        self.参战英雄头像_dict[1] = self.英雄_海诺
        self.参战英雄线路_dict[2] = Template(r"tpl1689665540773.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        self.参战英雄头像_dict[2] = self.英雄_牙
        self.参战英雄线路_dict[3] = Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        self.参战英雄头像_dict[3] = self.英雄_鬼谷子
        self.参战英雄线路_dict[4] = Template(r"tpl1686048521443.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        self.参战英雄头像_dict[4] = self.英雄_云中
        self.参战英雄线路_dict[5] = Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        self.参战英雄头像_dict[5] = self.英雄_太乙
        #
        # ------------------------------------------------------------------------------
        self.图片更新FILE = "WZRY.图片更新.txt"
        run_class_command(self=self, prefix=self.prefix, command=self.Tool.readfile(self.图片更新FILE))


class wzry_task:
    # 备注
    # 新账户,第一次打开各种模块,如万向天宫,会有动画等展示,脚本不做处理,手动点几下，之后就不会出现了
    # 需要传递中文时,由于精简后无法输入中文,在shell中建
    # redroid_arm64:/mnt/sdcard/Download # touch 诗语江南s4tpxWGu.txt

    def __init__(self, 移动端=None, 对战模式="5v5匹配", shiftnode=0, debug=False, 限时组队时间=7):
        self.移动端 = 移动端
        self.mynode = self.移动端.mynode
        self.totalnode = self.移动端.totalnode
        self.组队模式 = self.totalnode > 1
        self.房主 = self.mynode == 0 or self.totalnode == 1
        self.prefix = f"({self.mynode})"
        #
        self.设备类型 = self.移动端.设备类型
        self.APPID = "com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        # "com.tencent.tmgp.sgame/SGameActivity"
        self.APPOB = appOB(prefix=self.prefix, APPID=self.APPID, big=True, device=self.移动端)
        #
        self.对战模式 = 对战模式  # "5v5匹配" or "王者模拟战"
        # 对战模式 = "模拟战" if "moni" in __file__ else "5v5匹配"
        self.debug = debug  # 本地调试模式,加速,测试所有功能
        TimeECHO(self.prefix+f"对战模式:{self.对战模式}")
        #
        self.对战时间 = [5.1, 23]  # 单位hour,对战时间取N.m是为了让程序在N点时启动领取昨日没领完的礼包
        # 当hour小于此数字时才是组队模式
        self.限时组队时间 = 限时组队时间
        self.totalnode_bak = self.totalnode
        #
        self.本循环参数 = wzry_runinfo()
        self.上循环参数 = wzry_runinfo()

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
        if not connect_status(prefix=self.prefix):
            self.移动端.连接设备()
            if not self.移动端.device:
                TimeErr(self.prefix+"连接不上设备. 待同步后退出")
                if self.totalnode_bak > 1:  # 让其他节点抓紧结束
                    self.Tool.touchstopfile(f"{self.mynode}连接不上设备")
        # ------------------------------------------------------------------------------
        # 强制同步
        if self.totalnode_bak > 1:
            self.Tool.touch同步文件(self.Tool.辅助同步文件)
            self.Tool.必须同步等待成功(self.mynode, self.totalnode, sleeptime=10)
        # 检查连接状态以及退出
        if self.totalnode_bak > 1:
            if self.Tool.readstopfile():  # 这个只在多节点运行时会创建
                self.Tool.stoptask()
                return  # 就是结束
        else:
            if not connect_status(prefix=self.prefix):
                TimeErr(self.prefix+"连接不上设备. 退出")
                return
        #
        self.Tool.barriernode(self.mynode, self.totalnode, "WZRYinit")
        #
        # 统一本次运行的PID, 避免两个脚本同时运行出现控制冲突的情况
        self.WZRYPIDFILE = f".tmp.WZRY.{self.mynode}.PID.txt"
        hour, minu, sec = self.Tool.time_getHMS()
        self.myPID = f"{self.totalnode_bak}.{hour}{minu}{sec}"
        self.myPID = self.Tool.bcastvar(self.mynode, self.totalnode_bak, var=self.myPID, name="self.myPID")
        self.Tool.touchfile(self.WZRYPIDFILE, content=self.myPID)
        TimeECHO(self.prefix+f": 本次运行PID:[{self.myPID}]")
        #
        self.runstep = 0
        self.jinristep = 0
        # 如果已经判断在房间中了,短时间内执行相关函数，不再进行判断
        self.当前界面 = "未知"
        self.Tool.timelimit(timekey="当前界面", init=True)

        # 控制参数
        self.选择人机模式 = True
        self.青铜段位 = False
        self.标准模式 = False
        self.触摸对战 = False
        self.标准触摸对战 = False
        self.WZ新功能 = True
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
        self.KPL每日观赛FILE = f"WZRY.KPL每日观赛FILE.txt"
        self.Tool.removefile(self.结束游戏FILE)
        self.Tool.removefile(self.SLEEPFILE)
        # self.Tool.removefile(self.触摸对战FILE)
        # self.Tool.removefile(self.临时组队FILE)
        # 这里的图片主要是一些图片列表，例如所有的大厅元素
        # 以及一些核心，公共的图片
        self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
        分路长度 = len(self.图片.参战英雄线路_dict)
        self.参战英雄线路 = self.图片.参战英雄线路_dict[(self.mynode+0+shiftnode) % 分路长度]
        self.参战英雄头像 = self.图片.参战英雄头像_dict[(self.mynode+0+shiftnode) % 分路长度]
        self.备战英雄线路 = self.图片.参战英雄线路_dict[(self.mynode+3+shiftnode) % 分路长度]
        self.备战英雄头像 = self.图片.参战英雄头像_dict[(self.mynode+3+shiftnode) % 分路长度]
        #
        # 礼包设置
        self.强制领取礼包 = True
        self.王者营地礼包 = True
        self.玉镖夺魁签到 = False
        # 刷新礼包的领取计时
        self.王者营地 = wzyd_libao(prefix=str(self.mynode), 设备类型=self.移动端.设备类型, 初始化检查=False)
        self.每日礼包()
        self.Tool.touchfile(self.免费商城礼包FILE)

    # 保存运行信息
    def 构建循环参数(self, runinfo=None):
        if runinfo == None:
            runinfo = wzry_runinfo()
        runinfo.组队模式 = self.组队模式
        runinfo.房主 = self.房主
        runinfo.对战模式 = self.对战模式
        runinfo.限时组队时间 = self.限时组队时间
        runinfo.runstep = self.runstep
        runinfo.jinristep = self.jinristep
        runinfo.青铜段位 = self.青铜段位
        runinfo.标准模式 = self.标准模式
        runinfo.触摸对战 = self.触摸对战
        runinfo.标准触摸对战 = self.标准触摸对战
        runinfo.prefix = self.prefix
        return runinfo

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
        self.图片.王者登录关闭按钮 = self.Tool.uniq_Template_array(self.图片.王者登录关闭按钮)
        for i in self.图片.王者登录关闭按钮:
            keyindex = f"王者登陆关闭按钮{i}"
            # if keyindex in self.Tool.var_dict.keys(): continue
            pos = exists(i)
            if pos:
                self.Tool.var_dict[keyindex] = pos
                self.Tool.existsTHENtouch(i, keyindex, savepos=True)
            else:
                TimeECHO(self.prefix+"未识别到"+keyindex)
        for i in self.图片.王者登录关闭按钮:
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
        存在, self.图片.战绩页面元素 = self.Tool.存在任一张图(self.图片.战绩页面元素, "战绩页面元素")
        return 存在

    def 进入大厅(self, times=1):
        TimeECHO(self.prefix+f"尝试进入大厅{times}")
        if times == 1:
            self.Tool.timelimit(timekey="进入大厅", limit=60*30, init=True)
        else:
            if self.Tool.timelimit(timekey="进入大厅", limit=60*30, init=False):
                TimeECHO(self.prefix+f"进入大厅超时退出,更新图片资源库")
                self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
                TimeErr(self.prefix+"进入大厅超时退出,创建同步文件")
                if self.组队模式:
                    self.Tool.touch同步文件(self.Tool.辅助同步文件)
                else:
                    self.Tool.touch同步文件(self.Tool.独立同步文件)
                self.APPOB.重启APP(10)
                return False
        # 次数上限
        if times % 4 == 0:
            # 新赛季频繁提示资源损坏，次数太多进不去，就重启设备：
            if times > 4:
                self.移动端.重启设备(10)
            self.APPOB.重启APP(10)
            self.登录游戏()
        times = times+1
        #
        if not self.check_run_status():
            return True
        if "ios" in self.移动端.LINK:
            配件不支持 = Template(r"tpl1701523669097.png", record_pos=(-0.001, 0.002), resolution=(1136, 640))
            关闭配件不支持 = Template(r"tpl1701523677678.png", record_pos=(-0.004, 0.051), resolution=(1136, 640))
            if exists(配件不支持):
                self.Tool.existsTHENtouch(关闭配件不支持, "关闭配件不支持")
        if self.判断大厅中():
            return True
        if self.判断对战中():
            处理对战 = "模拟战" in self.对战模式
            if self.debug:
                处理对战 = True
            if self.触摸对战:
                处理对战 = True
            while self.判断对战中(处理对战):
                if self.debug:
                    TimeECHO(self.prefix+"尝试进入大厅:对战中,直接重启APP")
                    self.APPOB.重启APP(30)
                    self.登录游戏()  # cndaqiang: debug专用
                TimeECHO(self.prefix+"尝试进入大厅:对战sleep")
                sleep(15)  # sleep太久容易死
                if self.Tool.timelimit(timekey="结束对战", limit=60*15, init=False):
                    break
            self.结束人机匹配()
        if self.判断战绩页面():
            self.结束人机匹配()
        #
        if exists(self.图片.登录界面开始游戏图标):
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
        if not self.check_run_status():
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
        if not self.check_run_status():
            return True
        # 邀请
        if exists(Template(r"tpl1692951548745.png", record_pos=(0.005, 0.084), resolution=(960, 540))):
            关闭邀请 = Template(r"tpl1692951558377.png", record_pos=(0.253, -0.147), resolution=(960, 540), threshold=0.9)
            self.Tool.LoopTouch(关闭邀请, "关闭邀请", loop=5, savepos=False)
        # 老账号的友情提示
        if exists(Template(r"tpl1707377651759.png", record_pos=(-0.282, -0.032), resolution=(960, 540))):
            关闭邀请 = Template(r"tpl1707377671958.png", record_pos=(0.453, -0.205), resolution=(960, 540))
            self.Tool.LoopTouch(关闭邀请, "关闭友情对战推荐", loop=5, savepos=False)
        #
        if self.判断大厅中():
            return True
        if not self.check_run_status():
            return True
        #
        self.APPOB.重启APP()
        self.登录游戏()
        if not self.check_run_status():
            return True
        #
        # 健康系统直接重新同步
        if self.健康系统_常用命令():
            return True

    def 登录游戏(self, times=1, 检测到登录界面=False):
        if times == 1:
            self.Tool.timelimit(timekey="登录游戏", limit=60*5, init=True)
        times = times+1
        if not connect_status(prefix=self.prefix):
            self.Tool.touch同步文件(self.Tool.独立同步文件)
            return False
        if times > 2 and not 检测到登录界面:
            TimeErr(self.prefix+f"登录游戏:{times}次没有检测到登录界面,返回")
        if times > 5:
            TimeErr(self.prefix+f"登录游戏:{times}次登录成功,返回")
            return False
        TimeECHO(self.prefix+f"登录游戏{times}")
        if self.Tool.timelimit(timekey="登录游戏", limit=60*5, init=False):
            TimeErr(self.prefix+"登录游戏超时返回,更新图片资源库")
            self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
        #
        if exists(self.图片.网络不可用):
            TimeErr(self.prefix+"网络不可用:需要重启设备")
            self.移动端.重启设备(10)
            if self.组队模式:
                TimeErr(self.prefix+"需要重启设备:创建同步文件")
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
            else:
                TimeECHO(self.prefix+"需要重启设备:创建单节点同步")
                self.Tool.touch同步文件(self.Tool.独立同步文件)
        # 更新公告
        if not self.check_run_status():
            return True
        更新公告 = Template(r"tpl1692946575591.png", record_pos=(0.103, -0.235), resolution=(960, 540), threshold=0.9)
        if exists(更新公告):
            检测到登录界面 = True
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
        if exists(Template(r"tpl1692946837840.png", record_pos=(-0.092, -0.166), resolution=(960, 540), threshold=0.9)):
            检测到登录界面 = True
            TimeECHO(self.prefix+"同意游戏")
            touch(Template(r"tpl1692946883784.png", record_pos=(0.092, 0.145), resolution=(960, 540), threshold=0.9))
        if self.判断大厅中():
            return True
        #
        用户协议同意 = Template(r"tpl1692952132065.png", record_pos=(0.062, 0.099), resolution=(960, 540), threshold=0.9)
        if self.Tool.existsTHENtouch(用户协议同意, "用户协议同意"):
            检测到登录界面 = True
        # 这里需要重新登录了
        if exists(Template(r"tpl1692946938717.png", record_pos=(-0.108, 0.159), resolution=(960, 540), threshold=0.9)):
            检测到登录界面 = True
            TimeECHO(self.prefix+"需要重新登录")
            #
            self.Tool.touchfile(self.重新登录FILE)
            if self.totalnode_bak > 1:
                self.Tool.touchfile(self.无法进行组队FILE)
            #
            if self.组队模式:
                TimeErr(self.prefix+"需要重新登录:创建同步文件")
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
            else:
                TimeECHO(self.prefix+"需要重新登录:创建单节点同步")
                self.APPOB.重启APP(10*60)
                self.Tool.touch同步文件(self.Tool.独立同步文件)
            return True
        #
        if exists(Template(r"tpl1692951324205.png", record_pos=(0.005, -0.145), resolution=(960, 540))):
            检测到登录界面 = True
            TimeECHO(self.prefix+"关闭家长莫模式")
            touch(Template(r"tpl1692951358456.png", record_pos=(0.351, -0.175), resolution=(960, 540)))
            sleep(5)
        # 现在打开可能会放一段视频，怎么跳过呢？使用0.1的精度测试一下.利用历史记录了
        随意点击 = self.图片.登录界面开始游戏图标
        self.Tool.existsTHENtouch(随意点击, "随意点击k", savepos=True)
        #
        取消 = Template(r"tpl1697785803856.png", record_pos=(-0.099, 0.115), resolution=(960, 540))
        关闭 = Template(r"tpl1719739199756.png", record_pos=(-0.059, 0.209), resolution=(960, 540))
        self.Tool.existsTHENtouch(取消, "取消按钮")
        self.Tool.existsTHENtouch(关闭, "关闭按钮")
        self.关闭按钮()
        self.Tool.existsTHENtouch(取消, "取消按钮")
        self.Tool.existsTHENtouch(关闭, "关闭按钮")
        if self.判断大厅中():
            return True
        #
        if self.Tool.existsTHENtouch(self.图片.登录界面开始游戏图标, "登录界面.开始游戏", savepos=False):
            sleep(10)
        #
        # 健康系统直接重新同步
        if self.健康系统_常用命令():
            return True
        # 动态下载资源提示

        回归礼物 = Template(r"tpl1699607355777.png", resolution=(1136, 640))
        if exists(回归礼物):
            self.Tool.existsTHENtouch(Template(r"tpl1699607371836.png", resolution=(1136, 640)))
        回归挑战 = Template(r"tpl1699680234401.png", record_pos=(0.314, 0.12), resolution=(1136, 640))
        self.Tool.existsTHENtouch(回归挑战, "不进行回归挑战")
        self.关闭按钮()
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
            self.Tool.existsTHENtouch(self.图片.登录界面开始游戏图标, "登录界面.开始游戏", savepos=False)
            if self.判断大厅中():
                return True
            else:
                sleep(10)
        #
        if self.判断大厅中():
            return True
        return self.登录游戏(times, 检测到登录界面)

    def 单人进入人机匹配房间(self, times=1):
        if not self.check_run_status():
            return True
        if "ios" in self.移动端.LINK:
            配件不支持 = Template(r"tpl1701523669097.png", record_pos=(-0.001, 0.002), resolution=(1136, 640))
            关闭配件不支持 = Template(r"tpl1701523677678.png", record_pos=(-0.004, 0.051), resolution=(1136, 640))
            if exists(配件不支持):
                self.Tool.existsTHENtouch(关闭配件不支持, "关闭配件不支持")
        if "模拟战" in self.对战模式:
            TimeECHO(self.prefix+f"首先进入人机匹配房间_模拟战{times}")
            return self.单人进入人机匹配房间_模拟战(times)
        if "5v5排位" == self.对战模式:
            TimeECHO(self.prefix+f"首先进入排位房间{times}")
            return self.单人进入排位房间(times)
        #
        TimeECHO(self.prefix+f"首先进入人机匹配房间{times}")
        if self.判断对战中():
            self.结束人机匹配()
        if self.判断房间中():
            return True
        #
        self.进入大厅()
        #
        if not self.check_run_status():
            return True
        TimeECHO(self.prefix+f"进入大厅,开始{fun_name(1)}")
        if times == 1:
            self.Tool.timelimit(timekey=f"单人进入人机匹配房间", limit=60*10, init=True)
        #
        times = times+1
        if not self.Tool.existsTHENtouch(self.图片.大厅对战图标, "大厅对战", savepos=False):
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
            self.APPOB.重启APP(10)
            if self.组队模式:
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
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
                    self.Tool.touch同步文件(self.Tool.辅助同步文件)
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
                    if self.组队模式:
                        self.Tool.touch同步文件(self.Tool.辅助同步文件)
                    else:
                        self.Tool.touch同步文件(self.Tool.独立同步文件)
                    return True
            return self.单人进入人机匹配房间(times)
        return True

    def 单人进入排位房间(self, times=1):
        if not self.check_run_status():
            return True
        #
        if self.判断对战中():
            self.结束人机匹配()
        if self.判断房间中():
            return True
        #
        self.进入大厅()
        #
        if not self.check_run_status():
            return True
        TimeECHO(self.prefix+f"进入大厅,开始{fun_name(1)}")
        if times == 1:
            self.Tool.timelimit(timekey=f"{fun_name(1)}", limit=60*10, init=True)
        #
        times = times+1
        if not self.Tool.existsTHENtouch(self.图片.大厅排位赛, "大厅排位赛", savepos=False):
            TimeErr(self.prefix+"找不到大厅排位赛")
            return self.单人进入排位房间(times)
        sleep(10)
        if not self.Tool.existsTHENtouch(self.图片.进入排位赛, "进入排位赛", savepos=False):
            TimeErr(self.prefix+"找不到进入排位赛")
            return self.单人进入排位房间(times)
        #
        if not self.判断房间中():
            # 有时候长时间不进去被禁赛了
            确定按钮 = Template(r"tpl1689667950453.png", record_pos=(-0.001, 0.111), resolution=(960, 540))
            while self.Tool.existsTHENtouch(确定按钮, "不匹配被禁赛的确定按钮"):
                sleep(20)
                if self.Tool.timelimit(timekey=f"{fun_name(1)}", limit=60*10, init=False):
                    TimeErr(self.prefix+f"{fun_name(1)}超时,touch同步文件")
                    if self.组队模式:
                        self.Tool.touch同步文件(self.Tool.辅助同步文件)
                    else:
                        self.Tool.touch同步文件(self.Tool.独立同步文件)
                    return True
            return self.单人进入排位房间(times)
        return True
    #

    def 进入人机匹配房间(self):
        if not self.check_run_status():
            return True
        TimeECHO(self.prefix+"进入人机匹配房间")
        self.单人进入人机匹配房间()
        if not self.组队模式:
            return
        TimeECHO(self.prefix+"进入组队匹配房间")
        # 组队时,使用青铜模式进行, 前面应该已经配置好了青铜段位,这里进一步加强青铜段位确定
        if "5v5匹配" == self.对战模式 and not self.青铜段位 and self.房主:
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
        if not self.check_run_status():
            return True
        if not self.房主:
            找到取消按钮, self.图片.房间中的取消按钮图标 = self.Tool.存在任一张图(self.图片.房间中的取消按钮图标, "房间中的取消准备按钮")
            self.Tool.timelimit(timekey=f"辅助进房{self.mynode}", limit=60*5, init=True)
            while not 找到取消按钮:
                if self.Tool.timelimit(timekey=f"辅助进房{self.mynode}", limit=60*5, init=False):
                    TimeErr(self.prefix+"辅助进房超时退出")
                    self.Tool.touch同步文件(self.Tool.辅助同步文件)
                    break
                if not self.check_run_status():
                    TimeErr(self.prefix+"辅助进房失败")
                    return True
                #
                # 需要小号和主号建立亲密关系，并在主号中设置亲密关系自动进入房间
                TimeECHO(self.prefix+"不在组队的房间中")
                if not self.判断房间中(处理=False):
                    self.单人进入人机匹配房间()
                # 这里给的是特殊账户的头像
                进房 = self.图片.房主头像
                self.Tool.timedict["当前界面"] = 0
                TimeECHO(self.prefix+"准备进入组队房间")
                if not exists(进房):
                    TimeECHO(self.prefix+"没找到房主头像, 采用通用房主头像")
                    进房 = Template(r"tpl1699181922986.png", record_pos=(0.46, -0.15), resolution=(960, 540), threshold=0.9)
                if self.Tool.existsTHENtouch(进房, "房主头像按钮", savepos=False):
                    取消确定 = Template(r"tpl1699712554213.png", record_pos=(0.003, 0.113), resolution=(960, 540))
                    取消 = Template(r"tpl1699712559021.png", record_pos=(-0.096, 0.115), resolution=(960, 540))
                    if exists(取消确定):
                        TimeECHO(self.prefix+"点击房间错误,返回")
                        self.Tool.existsTHENtouch(取消, "取消错误房间")
                        continue
                    self.Tool.existsTHENtouch(取消, "取消错误房间")
                    # 这里给的是特殊账户的头像
                    进房间 = self.图片.房主房间
                    if not exists(进房间):
                        TimeECHO(self.prefix+"没找到进房间按钮, 采用通用进房间按钮")
                        进房间 = Template(r"tpl1699181937521.png", record_pos=(0.348, -0.194), resolution=(960, 540), threshold=0.9)
                    if self.Tool.existsTHENtouch(进房间, "进房间按钮", savepos=False):
                        TimeECHO(self.prefix+"尝试进入房间中")
                        sleep(10)
                        找到取消按钮, self.图片.房间中的取消按钮图标 = self.Tool.存在任一张图(self.图片.房间中的取消按钮图标, "房间中的取消准备按钮")
                        if not 找到取消按钮:
                            TimeECHO(self.prefix+"进入房间失败,可能是今日更新太频繁,版本不一致无法进房,需要重新登录更新")
                else:
                    TimeECHO(self.prefix+"未找到组队房间,检测主节点登录状态")

        self.Tool.barriernode(self.mynode, self.totalnode, "结束组队进房间")
        return

    def 单人进入人机匹配房间_模拟战(self, times=1):
        if self.判断对战中():
            self.结束人机匹配()
        # 模拟战的房间很干净，不用处理
        if self.判断房间中(处理=False):
            return True
        self.进入大厅()
        if not self.check_run_status():
            return True
        TimeECHO(self.prefix+"大厅中.开始进入模拟战房间")
        if self.Tool.LoopTouch(self.图片.大厅万象天工, "万象天工", loop=3, savepos=False):
            sleep(30)
            if self.判断大厅中():
                TimeECHO(self.prefix+"模拟战: 进入万象天工失败, 重启设备")
                self.APPOB.重启APP()
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
        if self.判断房间中(处理=False):
            return True
        else:
            return self.单人进入人机匹配房间(times)

    def 进行人机匹配(self, times=1):
        if not self.check_run_status():
            return True
        if times == 1:
            self.Tool.timelimit(timekey="进行人机匹配", limit=60*10, init=True)
            # 这里需要barrier一下,不然下面主节点如果提前点击领匹配,这里可能无法判断
            self.Tool.barriernode(self.mynode, self.totalnode, "人机匹配预判断房间")
        times = times+1
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
            找到开始按钮, self.图片.房间中的开始按钮图标 = self.Tool.存在任一张图(self.图片.房间中的开始按钮图标, "开始匹配")
            房间中的开始按钮 = self.图片.房间中的开始按钮图标[0]
            # 记录历史上有的匹配按钮位置,历史上就执行一次
            if "房间中的开始匹配按钮" not in self.Tool.var_dict.keys():
                pos = exists(房间中的开始按钮)
                if pos:
                    self.Tool.var_dict["房间中的开始匹配按钮"] = pos
            if not 找到开始按钮:
                TimeECHO(self.prefix+f":没找到开始按钮,使用历史位置")
            self.Tool.existsTHENtouch(房间中的开始按钮, "房间中的开始匹配按钮", savepos=not 找到开始按钮)
        else:
            找到取消按钮, self.图片.房间中的取消按钮图标 = self.Tool.存在任一张图(self.图片.房间中的取消按钮图标, "房间中的取消准备按钮")
            房间中的取消按钮 = self.图片.房间中的取消按钮图标[0]

        while True:
            if self.Tool.存在同步文件():
                return True
            # 如果没找到就再找一次
            if self.房主 and not 找到开始按钮:
                找到开始按钮, self.图片.房间中的开始按钮图标 = self.Tool.存在任一张图(self.图片.房间中的开始按钮图标, "开始匹配")
                房间中的开始按钮 = self.图片.房间中的开始按钮图标[0]
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
            if "模拟战" in self.对战模式:
                if 队友确认5v5匹配:
                    TimeErr(self.prefix+":模拟战误入5v5?")
                    if self.组队模式:
                        self.Tool.touch同步文件(self.Tool.辅助同步文件)
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
            exit_code = run_class_command(self=self, prefix=self.prefix, command=self.Tool.readfile(self.重新设置英雄FILE), must_ok=True)
            if exit_code != 0:
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
                self.APPOB.重启APP(10)
                self.登录游戏()
                return False
        #
        关闭技能介绍1 = Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540))
        关闭技能介绍2 = Template(r"tpl1700918628072.png", record_pos=(-0.059, 0.211), resolution=(960, 540))
        self.Tool.existsTHENtouch(关闭技能介绍1, "关闭技能介绍1", savepos=False)
        self.Tool.existsTHENtouch(关闭技能介绍2, "关闭技能介绍2", savepos=False)
        #

    def 结束人机匹配(self):
        TimeECHO(self.prefix+f"开始结束人机匹配:{self.对战模式}")
        if not self.check_run_status():
            return True
        if "模拟战" in self.对战模式:
            return self.结束人机匹配_模拟战()
        self.Tool.timelimit(timekey="结束人机匹配", limit=60*15, init=True)
        jixu = False

        while True:
            if not self.check_run_status():
                return True
            addtime = 60*15 if self.本循环参数.标准模式 else 0
            if self.Tool.timelimit(timekey="结束人机匹配", limit=60*15 + addtime, init=False):
                TimeErr(self.prefix+"结束人机匹配时间超时")
                if self.组队模式:
                    TimeErr(self.prefix+"结束人机匹配时间超时 and 组队touch同步文件")
                    self.Tool.touch同步文件(self.Tool.辅助同步文件)
                    return
                else:
                    self.Tool.touch同步文件(self.Tool.独立同步文件)
                    return
                return self.进入大厅()
            加速对战 = False
            if self.触摸对战:
                加速对战 = True
            if self.判断对战中(加速对战):
                jixu = False
                sleep(30)
                continue
            if self.判断房间中(处理=False):
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
            if exists(self.图片.返回房间按钮):
                jixu = True
            #
            # 健康系统直接重新同步
            if self.健康系统_常用命令():
                return True
            #
            游戏结束了 = Template(r"tpl1694360304332.png", record_pos=(-0.011, -0.011), resolution=(960, 540))
            if exists(游戏结束了):
                self.Tool.existsTHENtouch(Template(r"tpl1694360310806.png", record_pos=(-0.001, 0.117), resolution=(960, 540)))
            if not self.check_run_status():
                return

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
            if not self.check_run_status():
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
            # 返回房间/大厅
            if self.对战结束返回房间:
                if self.Tool.existsTHENtouch(self.图片.返回房间按钮, "返回房间"):
                    sleep(10)
                # 万一返回房间后来一堆提示
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
        if not self.check_run_status():
            return True
        self.Tool.timelimit(timekey="结束模拟战", limit=60*20, init=True)
        while True:
            if self.Tool.timelimit(timekey="结束模拟战", limit=60*30, init=False) or self.健康系统() or self.判断大厅中():
                TimeErr(self.prefix+"结束游戏时间过长 OR 健康系统 OR 大厅中")
                return self.进入大厅()
            if self.判断房间中(处理=False):
                return
            点击屏幕继续 = Template(r"tpl1701229138066.png", record_pos=(-0.002, 0.226), resolution=(960, 540))
            self.Tool.existsTHENtouch(点击屏幕继续, self.prefix+"点击屏幕继续")
            if self.判断对战中(False):
                sleeploop = 0
                while self.判断对战中(True):  # 开始处理准备结束
                    sleep(10)
                    sleeploop = sleeploop+1
                    if not self.check_run_status():
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
                    sleep(1)
            if exists(Template(r"tpl1690545494867.png", record_pos=(0.0, 0.179), resolution=(960, 540))):
                TimeECHO(self.prefix+"检测到:[退出+观战]界面")
                self.Tool.existsTHENtouch(Template(r"tpl1690545545580.png", record_pos=(-0.101, 0.182), resolution=(960, 540)), "选择退出对战")
            if self.判断房间中(处理=False):
                return
            if self.判断大厅中():
                return
            # 为了避免识别错误，加一个强制点击的命令
            keystr = "任意点击_monizhan"
            if keystr not in self.Tool.var_dict.keys():
                if "随意点击k" in self.Tool.var_dict.keys():
                    self.Tool.var_dict[keystr] = self.Tool.var_dict["随意点击k"]
            if keystr in self.Tool.var_dict.keys():
                任意点击_monizhan = Template(r"tpl1690545762580.png", record_pos=(-0.001, 0.233), resolution=(960, 540))
                self.Tool.existsTHENtouch(任意点击_monizhan, "任意点击_monizhan", savepos=True)
            #
            if self.Tool.existsTHENtouch(Template(r"tpl1690545762580.png", record_pos=(-0.001, 0.233), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续1")
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1690545802859.png", record_pos=(0.047, 0.124), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续2")
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1690545854354.png", record_pos=(0.002, 0.227), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续3")
                sleep(5)
            #
            if exists(Template(r"tpl1690545925867.png", record_pos=(-0.001, 0.241), resolution=(960, 540))):
                if self.对战结束返回房间:
                    if self.Tool.existsTHENtouch(self.图片.返回房间按钮, "返回房间", savepos=True):
                        sleep(10)
                        if self.判断房间中(处理=False):
                            break
            if self.判断房间中(处理=False):
                return
            if self.判断大厅中():
                return
    #

    def 每日礼包(self, 强制领取=False):
        if not self.check_run_status():
            return True
        #
        if 强制领取:
            self.Tool.timedict["领游戏礼包"] = 0
            self.Tool.timedict["领营地礼包"] = 0
        #
        # 王者APP礼包
        self.王者礼包()
        #
        # 营地礼包
        if not self.王者营地礼包:
            self.王者营地礼包 = self.每日礼包_王者营地(初始化=True)
        if self.王者营地礼包 and not self.组队模式:  # 组队时不打开王者营地,不同的节点进度不同
            self.每日礼包_王者营地()
        #

    def 王者礼包(self):
        if self.Tool.timelimit("领游戏礼包", limit=60*60*3, init=False):
            self.APPOB.打开APP()
            self.进入大厅()
            #
            if self.Tool.存在同步文件():
                TimeECHO(self.prefix+"领礼包时发现同步文件, 停止领取")
                return True
            if os.path.exists(self.重新登录FILE):
                TimeECHO(self.prefix+f"领礼包时发现{self.重新登录FILE}, 停止领取")
                return
            #
            if os.path.exists(self.免费商城礼包FILE):
                if self.商城免费礼包():
                    self.Tool.removefile(self.免费商城礼包FILE)
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
            #
            if os.path.exists(self.KPL每日观赛FILE):
                TimeECHO(self.prefix+"进行KPL观赛")
                self.进入大厅()
                try:
                    观赛时长 = int(self.Tool.readfile(self.KPL每日观赛FILE)[0])
                except:
                    traceback.print_exc()
                    观赛时长 = 60*15
                self.KPL每日观赛(times=1, 观赛时长=观赛时长)
        else:
            TimeECHO(self.prefix+"时间太短,暂时不领取游戏礼包")
        #
        self.Tool.timelimit("领游戏礼包", limit=60*60*3, init=False)

    def 战队礼包(self):
        self.进入大厅()
        #
        # 战队礼包
        TimeECHO(self.prefix+f":战队礼包")
        self.Tool.existsTHENtouch(Template(r"tpl1700403158264.png", record_pos=(0.067, 0.241), resolution=(960, 540)), "战队")
        # @todo, 添加已阅战队赛
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
        #
        if not self.check_run_status():
            return True
        #
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
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
        # 因为默认的商城进入后是特效很多的皮肤，影响了界面的识别，所以切到干净的促销入口进行识别
        促销入口 = Template(r"tpl1719455432184.png", record_pos=(-0.436, 0.075), resolution=(960, 540))
        免费图标 = Template(r"tpl1719455279197.png", record_pos=(-0.122, -0.252), resolution=(960, 540))
        免费领取 = Template(r"tpl1719455299372.png", record_pos=(0.035, 0.055), resolution=(960, 540), target_pos=8)
        确定购买 = Template(r"tpl1705069645193.png", record_pos=(-0.105, 0.165), resolution=(960, 540))
        商城界面 = []
        商城界面.append(促销入口)
        商城界面.append(免费图标)
        商城界面.append(Template(r"tpl1719455683640.png", record_pos=(-0.368, -0.25), resolution=(960, 540)))
        商城界面.append(Template(r"tpl1719455836014.png", record_pos=(-0.458, 0.19), resolution=(960, 540)))
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
        # 注：如果实在无法识别，这里手动点击到促销界面，让程序savepos记住促销的位置
        for i in range(len(商城界面)):
            self.Tool.existsTHENtouch(促销入口, f"新促销入口", savepos=True)
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
            TimeECHO("如果实在无法识别，手动点击到促销界面，让程序savepos记住促销的位置")
            # 如果识别错了，可以用下面的命令删除
            # if "促销入口" in self.Tool.var_dict.keys():
            #    del self.Tool.var_dict["促销入口"]
            return self.商城免费礼包(times=times)
        #
        领取成功 = False
        if self.Tool.existsTHENtouch(免费图标, "免费图标", savepos=False):
            sleep(5)
            领取成功 = self.Tool.existsTHENtouch(免费领取, "免费领取", savepos=False)
            sleep(10)
            self.Tool.LoopTouch(确定购买, "确定购买")
            self.关闭按钮()
            self.Tool.LoopTouch(返回, "返回")
            self.确定按钮()
        else:
            TimeECHO(self.prefix+f"没检测到免费图标,可能领取过了")
            self.Tool.LoopTouch(返回, "返回")
            return True
        if not 领取成功:
            TimeECHO(self.prefix+f"领取每日礼包失败")
        return True

    def 玉镖夺魁(self, times=1):
        self.进入大厅()
        #
        # 玉镖夺魁
        TimeECHO(self.prefix+f":玉镖夺魁{times}")
        #
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
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
        #########################
        # 下面的宝箱和碎片性价比不高,由于我的账户友情币已经非常多了,可以兑换,用于换铭文和钻石
        # return
        # 铭文
        if self.Tool.existsTHENtouch(Template(r"tpl1700455034567.png", record_pos=(-0.123, 0.155), resolution=(960, 540)), "铭文碎片兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700455039770.png", record_pos=(0.321, 0.226), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454883635.png", record_pos=(0.098, 0.118), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454897119.png", record_pos=(0.0, 0.164), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
        返回图标 = Template(r"tpl1707301421376.png", record_pos=(-0.445, -0.253), resolution=(960, 540))
        # 皮肤宝箱
        if self.Tool.existsTHENtouch(Template(r"tpl1700454970340.png", record_pos=(-0.12, -0.154), resolution=(960, 540)), "友情皮肤礼包兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454978914.png", record_pos=(0.32, 0.228), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454987098.png", record_pos=(0.1, 0.117), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454996867.png", record_pos=(-0.099, 0.166), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
            self.Tool.existsTHENtouch(返回图标, "友情礼包返回图标", savepos=True)
        # 回城宝箱
        if self.Tool.existsTHENtouch(Template(r"tpl1707301299599.png", record_pos=(0.035, -0.15), resolution=(960, 540)), "友情皮肤礼包兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1707301267168.png", record_pos=(0.32, 0.228), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454987098.png", record_pos=(0.1, 0.117), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454996867.png", record_pos=(-0.099, 0.166), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
            self.Tool.existsTHENtouch(返回图标, "友情礼包返回图标", savepos=True)
        # 击败宝箱
        if self.Tool.existsTHENtouch(Template(r"tpl1707301309821.png", record_pos=(-0.279, 0.005), resolution=(960, 540)), "友情皮肤礼包兑换"):
            sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1707301267168.png", record_pos=(0.32, 0.228), resolution=(960, 540)), "友情币兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454987098.png", record_pos=(0.1, 0.117), resolution=(960, 540)), "金色确定兑换"):
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1700454996867.png", record_pos=(-0.099, 0.166), resolution=(960, 540)), "蓝色确定兑换"):
                sleep(5)
            self.Tool.existsTHENtouch(返回图标, "友情礼包返回图标", savepos=True)

    def 每日礼包_王者营地(self, 初始化=False):
        if 初始化:
            TimeECHO(self.prefix+f"[{fun_name(1)}]检测王者营地状态")
        if not self.check_run_status():
            # 连接失败，不是营地有问题，所以返回True
            if 初始化:
                return True
            # 单纯的领取失败
            return False
        #
        if 初始化:
            初始化成功 = self.王者营地.营地初始化(初始化检查=True)
            self.王者营地.APPOB.关闭APP()
            self.APPOB.打开APP()
            return 初始化成功
        #
        if not self.Tool.timelimit("领营地礼包", limit=60*60*3, init=False):
            TimeECHO(self.prefix+"时间太短,暂时不领取营地礼包")
            return False
        #
        # 关闭王者节省内存
        self.APPOB.关闭APP()
        #
        TimeECHO(self.prefix+"王者营地礼包开始")
        if self.王者营地.RUN():
            TimeECHO(self.prefix+"王者营地礼包领取成功")
        else:
            TimeErr(self.prefix+"王者营地礼包领取失败")
        self.王者营地.STOP()  # 杀掉后台,提高王者、WDA活性
        self.Tool.timelimit("领营地礼包", limit=60*60*3, init=False)
        #
        self.APPOB.打开APP()

    def KPL每日观赛(self, times=1, 观赛时长=20*60):
        if not self.check_run_status():
            return True
        #
        if times == 1:
            TimeECHO(self.prefix+f":本次KPL观赛时长{int(观赛时长/60)}min")
            self.Tool.timelimit(timekey="KPL每日观赛", limit=观赛时长, init=True)
        else:
            if self.Tool.timelimit(timekey="KPL每日观赛", limit=观赛时长, init=False):
                TimeErr(self.prefix+"KPL每日观赛超时")
                return False
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 100:
            return False
        times = times+1
        KPL观赛入口 = Template(r"tpl1707396642681.png", record_pos=(0.463, 0.126), resolution=(960, 540))
        KPL战令入口 = Template(r"tpl1707398684588.png", record_pos=(0.231, -0.231), resolution=(960, 540))
        KPL观赛界面 = []
        KPL观赛界面.append(Template(r"tpl1707396755590.png", record_pos=(-0.354, -0.264), resolution=(960, 540)))
        KPL观赛界面.append(Template(r"tpl1707398710560.png", record_pos=(-0.3, -0.269), resolution=(960, 540)))
        KPL观赛界面.append(KPL战令入口)
        进入观赛界面, KPL观赛界面 = self.Tool.存在任一张图(KPL观赛界面, "KPL观赛界面")
        if not 进入观赛界面:
            TimeECHO(self.prefix+"准备进入KPL观赛入口")
            self.进入大厅()
            # 第一次识别失败时
            if not self.Tool.existsTHENtouch(KPL观赛入口, "KPL观赛入口", savepos=True):
                return self.KPL每日观赛(times, 观赛时长)
            sleep(30)
            for i in range(15):
                进入观赛界面, KPL观赛界面 = self.Tool.存在任一张图(KPL观赛界面, "KPL观赛界面")
                if 进入观赛界面:
                    break
                sleep(5)
        if not 进入观赛界面:
            TimeECHO(self.prefix+":没能进入KPL观赛入口,重新进入")
            return self.KPL每日观赛(times, 观赛时长)
        looptimes = 0
        while not self.Tool.timelimit(timekey="KPL每日观赛", limit=观赛时长, init=False):
            TimeECHO(self.prefix+f":KPL观影中{looptimes*30.0/60}/{观赛时长/60}")
            sleep(30)
            looptimes = looptimes+1
        # 开始领战令礼包
        if not self.Tool.existsTHENtouch(KPL战令入口, "KPL战令入口", savepos=True):
            return
        KPL战令任务 = Template(r"tpl1707398869726.png", record_pos=(-0.441, -0.158), resolution=(960, 540))
        if not self.Tool.existsTHENtouch(KPL战令任务, "KPL战令任务", savepos=True):
            return
        KPL领取奖励 = Template(r"tpl1707398884057.png", record_pos=(0.359, -0.176), resolution=(960, 540))
        self.Tool.LoopTouch(KPL领取奖励, "KPL领取奖励", savepos=False)
        KPL战令返回 = Template(r"tpl1707399262936.png", record_pos=(-0.478, -0.267), resolution=(960, 540))
        self.Tool.LoopTouch(KPL战令返回, "KPL战令返回", savepos=False)
        return True

        #
    def 每日礼包_每日任务(self, times=1, 战令领取=True):
        if not self.check_run_status():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
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
        sleep(15)
        进入战令界面 = False
        进入战令界面, 赛季任务界面 = self.Tool.存在任一张图(赛季任务界面, "赛季任务界面")
        #
        if not 进入战令界面 and times > 2:
            进入战令界面 = not self.判断大厅中()
        #
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
        # 这是使用savepos，下次换了新的领取位置记得清除这些dict
        if self.Tool.existsTHENtouch(今日活跃, "今日活跃 ", savepos=True):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        if self.Tool.existsTHENtouch(本周活跃1, "本周活跃1", savepos=True):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        if self.Tool.existsTHENtouch(本周活跃2, "本周活跃2", savepos=True):
            self.Tool.existsTHENtouch(确定按钮, "确定")
            sleep(5)
        #
        self.Tool.LoopTouch(确定按钮, "确定按钮")
        self.关闭按钮()
        self.确定按钮()
        #
        # 由于王者营地也可以领战令经验, 如果在这里把战令经验领到上限，营地的经验就不能领了,所以周5之后再领取
        weekday = self.Tool.time_getweek()
        if weekday < 5:
            TimeECHO(self.prefix+f"周六统一领取战令经验,先领取营地的经验")
            self.Tool.LoopTouch(返回, "返回")
            self.确定按钮()
            return True
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
        if not self.check_run_status():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领邮件礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领邮件礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
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
        if not self.check_run_status():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包", limit=60*5, init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times % 4 == 3:
            if not connect_status(prefix=self.prefix):
                self.Tool.touch同步文件(self.Tool.独立同步文件)
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
            self.Tool.LoopTouch(确定, "确定", loop=10)
        self.Tool.existsTHENtouch(能力测试关闭, "能力测试关闭")
        self.Tool.LoopTouch(返回, "返回")
        self.确定按钮()
        return True
# 状态判断

    def 判断大厅中(self):
        #
        if self.当前界面 == "大厅中":
            if self.Tool.timelimit(timekey="当前界面", limit=60, init=False):
                self.当前界面 == "未知"
            else:
                TimeECHO(self.prefix+f"采用历史的判断结果判定当前处在:{self.当前界面}")
                return True

        存在, self.图片.大厅元素 = self.Tool.存在任一张图(self.图片.大厅元素, "大厅元素")
        #
        if 存在:
            self.当前界面 = "大厅中"
            # 减少判断次数,不用担心图片太少的问题,每日会重新更新图片
            del self.图片.大厅元素[1:]
            self.Tool.timelimit(timekey="当前界面", init=True)
        else:
            self.当前界面 = "未知"
        #
        return 存在

    def 判断房间中(self, 处理=True):
        #
        if self.当前界面 == "房间中":
            if self.Tool.timelimit(timekey="当前界面", limit=60, init=False):
                self.当前界面 == "未知"
            else:
                TimeECHO(self.prefix+f"采用历史的判断结果判定当前处在:{self.当前界面}")
                return True
        存在, self.图片.房间元素 = self.Tool.存在任一张图(self.图片.房间元素, "房间元素")
        if 存在:
            # 减少判断次数,不用担心图片太少的问题,每日会重新更新图片
            del self.图片.房间元素[1:]
        # 活动界面
        if 存在 and 处理:
            # 这些活动翻页元素一般只显示一次，新的账户每次进入房间都会提示
            存在翻页活动, self.图片.房间翻页活动元素 = self.Tool.存在任一张图(self.图片.房间翻页活动元素, "房间翻页活动元素")
            if 存在翻页活动:
                # 存在之后，这个活动只出现一次,可以删除这个变量了
                del self.图片.房间翻页活动元素[0]
                # 每天生成新的图片对象时会重新恢复原始图片的
                活动翻页 = Template(r"tpl1707787154169.png", record_pos=(0.393, -0.01), resolution=(960, 540))
                self.Tool.LoopTouch(活动翻页, "房间中活动翻页", savepos=False)
                self.Tool.existsTHENtouch(self.图片.房间我知道了, "我知道了:翻页活动", savepos=False)
            else:
                # 如果不存的话,也可以适当删除一些self.图片.房间翻页活动元素
                if len(self.图片.房间翻页活动元素) > 0:
                    if not exists(self.图片.房间翻页活动元素[-1]):
                        del self.图片.房间翻页活动元素[-1]
            #
            存在, self.图片.房间元素 = self.Tool.存在任一张图(self.图片.房间元素, "房间元素")
        #
        if 存在:
            self.当前界面 = "房间中"
            self.Tool.timelimit(timekey="当前界面", init=True)
        else:
            self.当前界面 = "未知"
        #
        return 存在

    def 判断对战中(self, 处理=False):
        if "模拟战" in self.对战模式:
            return self.判断对战中_模拟战(处理)
        #
        对战中 = False
        if self.当前界面 == "对战中":
            if self.Tool.timelimit(timekey="当前界面", limit=60, init=False):
                self.当前界面 == "未知"
            else:
                TimeECHO(self.prefix+f"采用历史的判断结果判定当前处在:{self.当前界面}")
                对战中 = True
        if not 对战中:
            对战中, self.图片.对战图片元素 = self.Tool.存在任一张图(self.图片.对战图片元素, "对战图片元素")
            if 对战中:
                self.当前界面 = "对战中"
                self.Tool.timelimit(timekey="当前界面", init=True)
            else:
                self.当前界面 = "未知"
        #
        if 对战中:
            TimeECHO(self.prefix+" 判断对战:正在对战")
        if not 对战中:
            TimeECHO(self.prefix+" 判断对战:没有对战")
        if not 处理 or not 对战中:
            return 对战中
        #
        # 开始处理加速对战
        TimeECHO(self.prefix+"加速对战中:建议把自动买装备和自动技能加点打开,更真实一些")
        self.Tool.timelimit(timekey="endgame", limit=60*30, init=True)
        self.Tool.timelimit(timekey="check_run_status", limit=60, init=True)
        # 识别到的位置
        装备pos = False
        移动pos = False
        普攻pos = False
        装备poskey = "装备pos"+self.prefix
        移动poskey = "移动pos"+self.prefix
        普攻poskey = "普攻pos"+self.prefix
        # 不同账户出装位置不同,避免点击错误, 可以删除装备位置
        if 装备poskey in self.Tool.var_dict.keys():
            del self.Tool.var_dict[装备poskey]
        # 开始模拟人手点击
        while self.判断对战中(处理=False):
            TimeECHO(self.prefix+"加速对战中:对战按钮")
            if self.Tool.timelimit(timekey="check_run_status", limit=60, init=False):
                self.check_run_status()
            if self.Tool.存在同步文件():
                return True
            if not 装备pos:
                if 装备poskey in self.Tool.var_dict.keys():
                    装备pos = self.Tool.var_dict[装备poskey]
                else:
                    存在装备图标, self.图片.装备S = self.Tool.存在任一张图(self.图片.装备S, "装备S元素")
                    装备 = self.图片.装备S[0]
                    if 存在装备图标:
                        self.Tool.existsTHENtouch(装备, 装备poskey, savepos=True)
            #
            if not 移动pos:
                if 移动poskey in self.Tool.var_dict.keys():
                    移动pos = self.Tool.var_dict[移动poskey]
                else:
                    存在移动图标, self.图片.移动S = self.Tool.存在任一张图(self.图片.移动S, "移动S元素")
                    移动 = self.图片.移动S[0]
                    if 存在移动图标:
                        self.Tool.existsTHENtouch(移动, 移动poskey, savepos=True)
            #
            if not 普攻pos:
                if 普攻poskey in self.Tool.var_dict.keys():
                    普攻pos = self.Tool.var_dict[普攻poskey]
                else:
                    存在普攻图标, self.图片.普攻S = self.Tool.存在任一张图(self.图片.普攻S, "普攻S元素")
                    普攻 = self.图片.普攻S[0]
                    if 存在普攻图标:
                        self.Tool.existsTHENtouch(普攻, 普攻poskey, savepos=True)
            #
            if 装备pos:
                touch(装备pos)
            #
            if 移动pos:
                content = self.Tool.readfile(self.触摸对战FILE)
                # 如果有血条在第一行，则进行下面的测试代码
                # 很难判断成功
                if len(content) > 1:
                    if "血条" in content[0]:
                        del content[0]
                        # 针对血条调整运动方向
                        vector = None
                        存在敌方, self.图片.敌方血条 = self.Tool.存在任一张图(self.图片.敌方血条, "敌方血条元素")
                        if 存在敌方:
                            vector = [-0.2, random.random()/5]
                        else:
                            存在友方, self.图片.友方血条 = self.Tool.存在任一张图(self.图片.友方血条, "友方血条元素")
                            if 存在友方:
                                vector = [0.2, random.random()/5]
                        if vector:
                            TimeECHO(self.prefix+"针对英雄调整位置")
                            for i in range(10):
                                swipe(移动pos, vector=[x, y])
                #
                # 随机移动和攻击
                TimeECHO(self.prefix+"加速对战中:移动按钮")
                x = None
                inputxy = content
                if len(inputxy) > 1:
                    try:
                        x = float(inputxy[0])
                        y = float(inputxy[1])
                        TimeECHO(self.prefix+": x=%5.3f, y=%5.3f" % (x, y))
                    except:
                        TimeErr(self.prefix+f" not found x y in [{self.触摸对战FILE}]")
                for i in range(random.randint(1, 5)):
                    if not x:
                        x = 0.2+random.random()/5
                        y = -0.2+random.random()/5
                    swipe(移动pos, vector=[x, y])
                    #
                    if 普攻pos:
                        sleep(0.2)
                        touch(普攻pos)
            #
            if 普攻pos:
                touch(普攻pos)
            #
            if self.Tool.timelimit(timekey="endgame", limit=60*30, init=False):
                TimeErr(self.prefix+"对战中游戏时间过长,重启游戏")  # 存在对战的时间超过20min,大概率卡死了
                self.APPOB.重启APP(10)
                self.登录游戏()
                self.进入大厅()
                return False
        return True

    def 判断对战中_模拟战(self, 处理=False):
        正在对战 = False
        #
        对战中 = False
        if self.当前界面 == "对战中_模拟战":
            if self.Tool.timelimit(timekey="当前界面", limit=60, init=False):
                self.当前界面 == "未知"
            else:
                TimeECHO(self.prefix+f"采用历史的判断结果判定当前处在:{self.当前界面}")
                对战中 = True
        if not 对战中:
            对战中, self.图片.对战图片元素_模拟战 = self.Tool.存在任一张图(self.图片.对战图片元素_模拟战, "对战图片元素_模拟战")
            if 对战中:
                self.当前界面 = "对战中_模拟战"
                self.Tool.timelimit(timekey="当前界面", init=True)
        #
        if 对战中:
            TimeECHO(self.prefix+"判断对战中_模拟战:正在对战")
        if not 对战中:
            TimeECHO(self.prefix+"判断对战中_模拟战:没有对战")
        if not 处理 or not 对战中:
            return 对战中
        #
        # 开始处理加速对战
        self.Tool.timelimit(timekey="endgame", limit=60*20, init=True)
        while self.判断对战中_模拟战(False):
            TimeECHO(self.prefix+"处理对战中")
            self.Tool.LoopTouch(self.图片.钱袋子_模拟战, "LOOP钱袋子", loop=10)  # 点击结束后,应该变成X号
            self.Tool.LoopTouch(self.图片.刷新金币_模拟战, "LOOP刷新金币", loop=10)
            if not exists(self.图片.关闭钱袋子_模拟战) and not exists(self.图片.钱袋子_模拟战):
                return False
            if self.Tool.timelimit(timekey="endgame", limit=60*20, init=False):
                break
            sleep(10)
            if not self.check_run_status():
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
            self.APPOB.关闭APP()
            if self.组队模式:
                TimeErr(self.prefix+"组队情况检测到健康系统,所以touch同步文件")
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
            else:
                TimeErr(self.prefix+"组队情况检测到健康系统,所以touch独立同步文件")
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                self.APPOB.重启APP(60*5)
            return True
        else:
            return False

    def check_run_status(self):
        #
        if self.Tool.存在同步文件(self.Tool.独立同步文件):
            if self.组队模式:
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
            TimeECHO(self.prefix+f"[{fun_name(2)}][{fun_name(1)}]失败:存在[{self.Tool.独立同步文件}]")
            return False
        if self.totalnode_bak > 1 and self.Tool.存在同步文件(self.Tool.辅助同步文件):
            TimeECHO(self.prefix+f"[{fun_name(2)}][{fun_name(1)}]:存在[{self.Tool.辅助同步文件}]")
            return False
        #
        if not connect_status(prefix=self.prefix+fun_name(2)):
            # 尝试连接一下,还不行就同步吧
            self.移动端.连接设备(times=1, timesMax=2)
            if connect_status(prefix=self.prefix+fun_name(2)):
                return True
            # 单人模式创建同步文件后等待,组队模式则让全体返回
            self.Tool.touch同步文件(self.Tool.独立同步文件)
            if self.组队模式:
                self.Tool.touch同步文件(self.Tool.辅助同步文件)
            TimeECHO(self.prefix+f"[{fun_name(2)}][{fun_name(1)}]失败:无法connect")
            return False
        else:
            return True

# 开始运行
    def 进行人机匹配对战循环(self):
        # 初始化
        if not self.check_run_status():
            return
        if self.房主:
            TimeECHO(self.prefix+"人机匹配对战循环:"+"->"*10)
        # 进入房间
        self.进入人机匹配房间()
        if not self.check_run_status():
            return
        # 进行对战
        self.进行人机匹配()
        if not self.check_run_status():
            return
        加速对战 = False
        if self.debug:
            加速对战 = True
        if "模拟战" in self.对战模式:
            加速对战 = True
        if self.标准触摸对战:
            加速对战 = True
        if self.判断对战中(加速对战):
            sleep(30)
        if not self.check_run_status():
            return
        # 结束对战
        self.结束人机匹配()
        if not self.check_run_status():
            return
        #
        if self.mynode == 0:
            self.Tool.clean文件()
        if self.房主:
            TimeECHO(self.prefix+"<-"*10)
        #

    def RUN(self):  # 程序入口
        新的一天 = False
        while True:
            # ------------------------------------------------------------------------------
            # 检测是否出现控制冲突,双脚本情况
            if self.myPID != self.Tool.readfile(self.WZRYPIDFILE)[0].strip():
                TimeErr(self.prefix+f": 本次运行PID[{self.myPID}]不同于[{self.WZRYPIDFILE}],退出中.....")
                if self.totalnode_bak > 1:  # 让其他节点抓紧结束
                    self.Tool.touch同步文件(self.Tool.辅助同步文件)
                return True
            #
            # ------------------------------------------------------------------------------
            run_class_command(self=self, prefix=self.prefix, command=self.Tool.readfile(self.临时初始化FILE))
            # ------------------------------------------------------------------------------
            # >>> 设备状态调整
            if self.Tool.存在同步文件():
                self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
            # 健康系统禁赛、系统卡住、连接失败等原因导致check_run_status不通过，这里同意处理
            if not self.check_run_status():
                #
                if not connect_status(prefix=self.prefix):
                    self.移动端.连接设备()
                #
                # 必须所有节点都能上线，否则并行任务就全部停止
                if not connect_status(times=2, prefix=self.prefix):
                    if self.totalnode_bak > 1:  # 让其他节点抓紧结束
                        TimeErr(self.prefix+"连接不上设备. 所有节点全部准备终止")
                        self.Tool.touchstopfile(f"{self.mynode}连接不上设备")
                        self.Tool.touchfile(self.无法进行组队FILE)
                        self.Tool.stoptask()
                        self.Tool.touch同步文件(self.Tool.辅助同步文件)
                    else:
                        TimeErr(self.prefix+"连接不上设备. 退出")
                    return True
                #
                # 如果个人能连上，检测是否有组队情况存在同步文件
                if self.totalnode_bak > 1:
                    # 判断是否存在self.Tool.辅助同步文件，若存在必须同步成功（除非存在readstopfile）
                    self.Tool.必须同步等待成功(mynode=self.mynode, totalnode=self.totalnode_bak,
                                       同步文件=self.Tool.辅助同步文件, sleeptime=60*5)
                    if self.Tool.readstopfile():
                        self.Tool.stoptask()
                        return True
                else:
                    TimeECHO(self.prefix+f"单账户重置完成")
                self.Tool.removefile(self.Tool.独立同步文件)
                #
                if not connect_status(prefix=self.prefix):
                    sleep(60)
                    continue
                # 重置完成
                if not self.组队模式:
                    if not self.王者营地礼包:
                        self.王者营地礼包 = self.每日礼包_王者营地(初始化=True)
                    if self.王者营地礼包:
                        self.每日礼包_王者营地()
                self.APPOB.重启APP(sleeptime=self.mynode*10+60)
                self.登录游戏()
            self.Tool.removefile(self.Tool.独立同步文件)
            #
            if os.path.exists(self.结束游戏FILE):
                TimeECHO(self.prefix+f"检测到{self.结束游戏FILE}, stop")
                self.APPOB.关闭APP()
                return
            #
            while os.path.exists(self.SLEEPFILE):
                TimeECHO(self.prefix+f"检测到{self.SLEEPFILE}, sleep(5min)")
                sleep(60*5)
            # ------------------------------------------------------------------------------
            # 这里做一个循环的判断，夜间不自动刷任务
            # 服务器5点刷新礼包和信誉积分等
            startclock = self.对战时间[0]
            endclock = self.对战时间[1]
            while self.Tool.hour_in_span(startclock, endclock) > 0:
                #
                # 还有多久开始，太短则直接跳过等待了
                leftmin = self.Tool.hour_in_span(startclock, endclock)*60.0
                if leftmin < 10:
                    TimeECHO(self.prefix+"剩余%d分钟进入新的一天" % (leftmin))
                    sleep(leftmin*60)
                    新的一天 = True
                    continue
                #
                # 这里仅领礼包
                # 在第二天的时候（新的一天=True）就不会执行这个命令了
                if not 新的一天 and leftmin > 60:
                    TimeECHO(self.prefix+"夜间停止刷游戏前领取礼包")
                    self.每日礼包(强制领取=self.强制领取礼包)
                    # 关闭APP并SLEEP等待下一个时间周期
                    self.APPOB.关闭APP()
                新的一天 = True
                #
                # 避免还存在其他进行没有同步完成的情况
                leftmin = self.Tool.hour_in_span(startclock, endclock)*60.0
                if leftmin > 60 and self.totalnode_bak > 1:
                    self.APPOB.关闭APP()
                    for i in range(6):
                        TimeECHO(self.prefix+"夜间已关闭APP, 检测是否有多账户同步残留")
                        if self.Tool.存在同步文件():
                            break
                        sleep(10*60)
                #
                # 计算休息时间
                TimeECHO(self.prefix+"准备休息")
                leftmin = self.Tool.hour_in_span(startclock, endclock)*60.0
                if self.移动端.容器优化:
                    leftmin = leftmin+self.mynode*1  # 这里的单位是分钟,每个node别差别太大
                TimeECHO(self.prefix+"预计等待%d min ~ %3.2f h" % (leftmin, leftmin/60.0))
                if self.debug:
                    leftmin = 0.5
                if leftmin > 60:
                    self.APPOB.重启APP(leftmin*60)
                else:
                    sleep(leftmin*60)
                #
            if 新的一天:
                TimeECHO(self.prefix+">>>>>>>>>>>>>>>新的一天>>>>>>>>>>>>>>>>>>>>")
                新的一天 = False
                if not connect_status(prefix=self.prefix):
                    self.移动端.连接设备()
                self.APPOB.重启APP(20)
                self.登录游戏()
                self.jinristep = 0
                self.WZ新功能 = True
                self.本循环参数 = wzry_runinfo()
                self.上循环参数 = wzry_runinfo()
                self.选择人机模式 = True
                self.青铜段位 = False
                # 因为免费商城礼包每天只领取一次
                self.Tool.touchfile(self.免费商城礼包FILE)
                # 营地礼包初始化
                self.王者营地礼包 = self.每日礼包_王者营地(初始化=True)
                self.Tool.removefile(self.青铜段位FILE)
                self.Tool.removefile(self.重新登录FILE)
                self.Tool.removefile(self.无法进行组队FILE)
                if self.totalnode_bak > 1:
                    TimeECHO(self.prefix+":新的一天创建同步文件进行初次校准")
                    self.totalnode = self.totalnode_bak
                    self.Tool.touch同步文件()
                # 更新图片
                self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
                # 更新时间戳，不然容易，第一天刚开局同步出错直接去领礼包了
                self.Tool.timelimit("领游戏礼包", limit=60*60*3, init=True)
                self.Tool.timelimit("领营地礼包", limit=60*60*3, init=True)
                continue
            # ------------------------------------------------------------------------------
            # 下面就是正常的循环流程了
            #
            if os.path.exists(self.重新登录FILE):
                if self.Tool.timelimit(timekey="检测王者登录", limit=60*60*4, init=False):
                    TimeECHO(self.prefix+f"存在[{self.重新登录FILE}],重新检测登录状态")
                    self.Tool.removefile(self.重新登录FILE)
                    if self.Tool.totalnode_bak > 1:
                        self.Tool.removefile(self.无法进行组队FILE)
                    self.APPOB.重启APP()
                    self.登录游戏()
            #
            if os.path.exists(self.重新登录FILE):
                TimeECHO(self.prefix+"存在重新登录文件,登录后删除")
                if self.Tool.totalnode_bak > 1 and not os.path.exists(self.无法进行组队FILE):
                    self.Tool.touchfile(self.无法进行组队FILE)
                for i in range(10):
                    sleep(60)
                    if self.Tool.存在同步文件():
                        break
                continue
            # ------------------------------------------------------------------------------
            # 组队模式，单人模式判断
            # 各种原因无法组队判定
            if self.totalnode_bak > 1:
                self.无法进行组队 = os.path.exists(self.无法进行组队FILE)
                组队时间内 = not self.Tool.hour_in_span(startclock, self.限时组队时间) > 0
                可以组队 = not self.无法进行组队 and 组队时间内
                # 报告运行状态
                组队原因 = ""
                单人原因 = ""
                if self.组队模式 and self.无法进行组队:
                    单人原因 = f"检测到{self.无法进行组队FILE}"
                if self.组队模式 and not 组队时间内:
                    单人原因 = f"不在组队时间[{startclock},{self.限时组队时间}]内"
                if not self.组队模式 and 可以组队:
                    组队原因 = "进入组队模式"
                    self.组队模式 = True
                if len(单人原因) > 1:
                    TimeECHO(self.prefix+f"关闭组队功能:{单人原因}")
                if len(组队原因) > 1:
                    TimeECHO(self.prefix+f"{组队原因}")
                #
                if 可以组队:
                    self.组队模式 = True
                    self.totalnode = self.totalnode_bak
                    self.Tool.totalnode = self.totalnode
                else:
                    self.组队模式 = False
                    self.totalnode = 1
                    self.Tool.totalnode = 1
            # ------------------------------------------------------------------------------
            # 运行前统一变量
            self.组队模式 = self.totalnode > 1
            if self.组队模式:
                self.runstep = self.Tool.bcastvar(self.mynode, self.totalnode, var=self.runstep, name="runstep")
                self.jinristep = self.Tool.bcastvar(self.mynode, self.totalnode, var=self.jinristep, name="jinristep")
                # 广播一些变量，这样就不用在每个文件中都写初始化参数了
                self.限时组队时间 = self.Tool.bcastvar(self.mynode, self.totalnode, var=self.限时组队时间, name="限时组队时间")
                #
                TimeECHO(self.prefix+"组队模式")
            self.房主 = self.mynode == 0 or self.totalnode == 1
            TimeECHO(self.prefix+f"运行次数{self.runstep}|今日步数{self.jinristep}")
            #
            self.Tool.barriernode(self.mynode, self.totalnode, "准备进入战斗循环")
            #
            if self.Tool.存在同步文件():
                TimeECHO(self.prefix+"准备进入战斗循环中遇到同步文件返回")
                continue
            #
            # ------------------------------------------------------------------------------
            # 计算参数设置
            self.runstep = self.runstep+1
            self.jinristep = self.jinristep+1
            if "5v5匹配" == self.对战模式:
                self.青铜段位 = os.path.exists(self.青铜段位FILE)
                self.标准模式 = os.path.exists(self.标准模式FILE)
                self.触摸对战 = os.path.exists(self.触摸对战FILE)
                self.标准触摸对战 = os.path.exists(self.标准模式触摸对战FILE)
                if self.组队模式 and not self.青铜段位:
                    TimeECHO(self.prefix+f"组队时采用青铜段位")
                    self.青铜段位 = True
                # 希望在青铜局时进行触摸对战,而不是占据星耀刷熟练度的机会
                if not self.青铜段位:
                    if self.触摸对战:
                        TimeECHO(self.prefix+f"非青铜局不模拟人手触摸")
                        self.触摸对战 = False
                    if self.标准触摸对战:
                        TimeECHO(self.prefix+f"非青铜局不进行标准模式的人手触摸")
                        self.标准触摸对战 = False
            if "5v5排位" == self.对战模式:
                self.触摸对战 = os.path.exists(self.触摸对战FILE)
            # ------------------------------------------------------------------------------
            # 若希望进行自动调整分路和设置触摸对战等参数，可以将相关指令添加到"self.对战前插入FILE",
            run_class_command(self=self, prefix=self.prefix, command=self.Tool.readfile(self.对战前插入FILE))
            if "5v5匹配" == self.对战模式 or "5v5排位" == self.对战模式:
                if self.标准触摸对战:
                    self.标准模式 = True
                    self.触摸对战 = True
                if self.触摸对战:
                    TimeECHO(self.prefix+f"本局对战:模拟人手触摸")
                if self.标准模式 and "5v5匹配" == self.对战模式:
                    TimeECHO(self.prefix+f"本局对战:使用标准模式")
                if "5v5排位" == self.对战模式:
                    TimeECHO(self.prefix+f"这是5v5排位, 小心你的信誉分啊喂")
                    TimeECHO(self.prefix+f"5v5的游戏被你完成4v5了, 会被系统检测到的")
            # ------------------------------------------------------------------------------
            # 此处开始记录本步的计算参数，此参数目前的功能只用于判断前后两步的计算参数差异
            # 后续程序的控制，仍采用 self.触摸对战等参数
            self.构建循环参数(self.本循环参数)
            # 这里判断和之前的对战是否相同,不同则直接则进行大厅后重新开始
            self.本循环参数.printinfo()
            if not self.本循环参数.compare(self.上循环参数):
                TimeECHO(self.prefix+f"上步计算参数不同,回到大厅重新初始化")
                self.图片 = wzry_figure(prefix=self.prefix, Tool=self.Tool)
                self.进入大厅()
            # ------------------------------------------------------------------------------
            # 开始辅助同步,然后开始游戏
            self.APPOB.打开APP()
            self.进行人机匹配对战循环()
            # ------------------------------------------------------------------------------
            # 如果计算过程中对参数进行了更改，这里可以记录最新的参数
            self.构建循环参数(self.上循环参数)
            # ------------------------------------------------------------------------------
            if not self.check_run_status():
                TimeECHO(self.prefix+"战斗结束,check_run_status失败,返回")
                continue
            # 礼包
            if self.runstep % 5 == 4:
                self.每日礼包()
            #
            if self.移动端.实体终端 and self.Tool.timelimit("休息手机", limit=60*60, init=False):
                TimeECHO(self.prefix+":实体终端,休息设备")
                # self.APPOB.关闭APP()
                sleep(60*2)


class auto_airtest:
    def __init__(self, mynode=0, totalnode=1, 设备类型="android", LINK_dict={}):
        self.mynode = mynode
        self.totalnode = totalnode
        self.设备类型 = 设备类型.lower()
        self.prefix = f"({self.mynode}/{self.totalnode})"
        print(self.prefix)
        # mac平台
        self.debug = "darwin" in sys.platform.lower()
        # 使用debug的LINK, mynode=0~4: 我的linux服务器上的安卓容器, 5~10: 本地模拟器、手机等测试设备
        self.debug = self.debug or os.path.exists("debug.txt") or mynode > 4
        # 设备信息
        if len(LINK_dict) == 0:
            LINK_dict = {}
            if "android" in self.设备类型:
                # BlueStack的端口, 自己创建的docker的端口
                for i in range(10):
                    LINK_dict[i] = "Android:///"+"127.0.0.1:"+str(5555+i*10)
                # LD模拟器端口
                LdPID = 0
                if os.path.exists(os.path.join(LDPlayerdir,"dnmultiplayer.exe")):
                     LdPID=getpid_win(IMAGENAME="dnmultiplayer.exe",key="dnmultiplayer")
                if LdPID > 0:
                    for i in range(10):
                        LINK_dict[i] = "Android:///"+"127.0.0.1:"+str(5555+i*2)                    
            else:
                for i in range(10):
                    LINK_dict[i] = "ios:///http://"+"192.168.12.130:"+str(8100+i)
            if self.debug:
                # 当在这里手动指定Link时,自动进行修正
                # docker容器
                LINK_dict[0] = "Android:///"+"192.168.192.10:5555"
                LINK_dict[1] = "Android:///"+"192.168.192.10:5565"
                LINK_dict[2] = "Android:///"+"192.168.192.10:5575"
                LINK_dict[3] = "Android:///"+"192.168.192.10:5585"
                LINK_dict[4] = "Android:///"+"192.168.192.10:5595"
                # 一些特殊的测试机器
                LINK_dict[5] = "Android:///"+"192.168.192.39:5555"  # windows电脑上的安卓模拟器
                LINK_dict[6] = "Android:///"+"192.168.192.39:5565"  # windows电脑上的安卓模拟器
                LINK_dict[7] = "ios:///http://127.0.0.1:8200"  # Iphone SE映射到本地
                LINK_dict[8] = "ios:///http://169.254.83.56:8100"  # Iphone 11支持无线连接
                LINK_dict[9] = "Android:///emulator-5554"  # 本地的安卓模拟器
                LINK_dict[10] = "Android:///4e86ac13"  # usb连接的安卓手机
                self.debug = False  # 仅用于设置ios连接,程序还是正常运行
        #
        self.LINK = LINK_dict[mynode]
        self.设备类型 = self.LINK.split(":")[0].lower()
        self.printINFO()
        self.移动端 = deviceOB(mynode=self.mynode, totalnode=self.totalnode, LINK=self.LINK)
        if not self.移动端.device:
            TimeErr(f"{self.prefix}"+"-"*10)
            TimeErr(f"{self.prefix}:连接设备失败,退出")
            self.printINFO(">>>")
            return
        #
        TASK = wzry_task(self.移动端)
        # 以后的测试脚本写在WZRY.0.临时初始化.txt中,不再插入到object.py中
        TASK.RUN()
        TASK.APPOB.关闭APP()
        #

    def printINFO(self, prefix=""):
        TimeECHO(prefix+f"airtest目录: {os.path.dirname(airtest.__file__)}")
        TimeECHO(prefix+f"{self.prefix}:LINK={self.LINK}")
        TimeECHO(prefix+f"{self.prefix}:设备类型={self.设备类型}")
        TimeECHO(prefix+f"{self.prefix}:mynode={self.mynode}")
        TimeECHO(prefix+f"{self.prefix}:totalnode={self.totalnode}")


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
    if len(sys.argv) == 2:
        if "LINK" in sys.argv[1]:
            auto_airtest(mynode=0, totalnode=1, LINK_dict=[sys.argv[1].split("=")[-1]])
            exit()
    if not multi_run:
        auto_airtest(mynode, totalnode, 设备类型)
    else:
        def multi_start(args):
            auto_airtest(mynode=args[0],totalnode=args[1],设备类型=args[2])
            return 0
        from pathos import multiprocessing
        m_process = totalnode
        m_cpu = [[i,totalnode,设备类型] for i in range(0, m_process)]
        if __name__ == '__main__':
            p = multiprocessing.Pool(m_process)
            out = p.map_async(multi_start, m_cpu).get()
            p.close()
            p.join()
    exit()
