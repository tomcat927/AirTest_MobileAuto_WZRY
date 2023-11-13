#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2023-11-10            #
# Build  : 2023-11-10            #
# What   : IOS/Android 自动化任务  #
#################################

import sys,os
from airtest.core.api import start_app,stop_app,Template,connect_device,touch,exists,sleep,swipe
import numpy as np
import random
import logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.WARNING)

from airtest.core.settings import Settings as ST
ST.OPDELAY = 1
# 全局阈值的范围为[0, 1]
ST.THRESHOLD_STRICT = 0.8  # assert_exists语句touch(Template(r"tpl1689665366952.png", record_pos=(-0.425, -0.055), resolution=(960, 540)))的默认阈值，一般比THRESHOLD更高一些
ST.THRESHOLD = 0.8  # 其他语句的默认阈值

#时间参数
import time
#防止服务器时区不同,设定时间为东八区
from datetime import datetime, timezone, timedelta
# 创建一个表示东八区时区的 timedelta 对象
eastern_eight_offset = timedelta(hours=8)
# 创建一个时区对象
eastern_eight_tz = timezone(eastern_eight_offset)
#这个设置可以极低的降低airtest输出到屏幕的信息

#设置,虚拟机,android docker, iphone, etc,主要进行设备的连接和重启
def TimeECHO(info="None",end=""):
    # 获取当前日期和时间
    current_datetime = datetime.now(eastern_eight_tz)
    # 格式化为字符串（月、日、小时、分钟、秒）
    formatted_string = current_datetime.strftime("[%m-%d %H:%M:%S]")
    modified_args = formatted_string+info
    if len(end) > 0:
        print(modified_args,end=end)
    else:
        print(modified_args)
    #如果airtest客户端报错,python命令行不报错.就制定airtest的oython路径为anaconda的python

def TimeErr(info="None"):
    TimeECHO("NNNN:"+info)
#
class DQWheel:
    def __init__(self, var_dict_file='var_dict_file.txt',mynode=-10,totalnode=-10,容器优化=False):
        self.timedict={}
        self.容器优化=容器优化
        self.辅助同步文件="NeedRebarrier.txt"
        self.mynode=mynode
        self.totalnode=totalnode
        self.prefix=""
        if  self.mynode >= 0: self.prefix=f"({mynode})"
        #
        self.barrierlimit=60*20 #同步最大时长
        self.filelist=[] #建立的所有文件，用于后期clear
        self.var_dict_file=var_dict_file
        self.var_dict=self.read_dict(self.var_dict_file)
        self.savepos=True

    def list_files(self,path):
        files=[]
        with os.scandir(path) as entries:
            for entry in entries:
                files.append(entry.name)
        return files
    #
    def init_clean(self):
        self.removefile(self.辅助同步文件)
        #os.listdir(".")不显示隐藏文件
        for name in self.list_files("."):
            text=".tmp.barrier."
            if text == name[:len(text)]:
                TimeECHO(self.prefix+"清理旧文件:",end='\r')
                self.removefile(name)
    #
    def timelimit(self,timekey="",limit=0,init=True):
        if self.容器优化: limit=limit+120 #容器中比较卡,多反应一会
        if len(timekey) == 0: timekey="none"
        if not timekey in self.timedict.keys(): init = True
        if init:
            self.timedict[timekey]=time.time()
        else:
            if time.time()-self.timedict[timekey] > limit:
                self.timedict[timekey]=time.time()
                return True
            else:
                return False
    def removefile(self,filename):
        #
        try:
            os.remove(filename)
            TimeECHO(self.prefix+"删除["+filename+"]成功") 
            return True    
        except:
            TimeECHO(self.prefix+"删除["+filename+"]失败")     
            return False
    def touchfile(self,filename,content=""):
        try:
            f=open(filename,'w')
            f.write(str(content))
            f.close()
            end=""
            if len(content) > 0: end = f"with ({content})"
            TimeECHO(self.prefix+f"创建[{filename}] {end} 成功")     
        except:
            TimeECHO(self.prefix+"创建["+filename+"]失败")
    def readfile(self,filename):
        try:
            f=open(filename,'r')
            content=f.readlines()
            f.close()
            TimeECHO(self.prefix+"Read["+filename+"]成功")     
            return content
        except:
            TimeECHO(self.prefix+"Read["+filename+"]失败")     
            return [""]

    #
    def touch同步文件(self):
        TimeECHO(self.prefix+f"创建同步文件{self.辅助同步文件}")
        self.touchfile(self.辅助同步文件)
        #该文件不添加到列表,仅在成功同步后才删除
        #self.filelist.append(self.辅助同步文件)
    def 存在同步文件(self):
        return os.path.exists(self.辅助同步文件)
    def clean文件(self):
        for i in self.filelist:
            if os.path.exists(i):
                self.removefile(i)
        self.filelist=[]
    #
    def barriernode(self,mynode,totalnode,name="barrierFile"):
        if totalnode < 2: return True
        if self.Tool.存在同步文件(): return True
        filelist=[]
        ionode= mynode == 0 or totalnode == 1
        #
        if ionode:
            TimeECHO(self.prefix+"."*10)
            TimeECHO(self.prefix+f">>>>>同步开始>{name}")
        #
        for i in np.arange(1,totalnode):
            filename=f".tmp.barrier.{i}.{name}.txt"
            if ionode: self.touchfile(filename)
            filelist.append(filename)
            self.filelist.append(filename)
        #
        self.timelimit(timekey=name,limit=self.barrierlimit,init=True)
        while not self.timelimit(timekey=name,limit=self.barrierlimit,init=False):
            if self.Tool.存在同步文件(): return True
            if ionode:
                barrieryes=True
                for i in filelist:
                    barrieryes= barrieryes and not os.path.exists(i)
                if barrieryes:
                    TimeECHO(self.prefix+"."*10)
                    TimeECHO(self.prefix+f"<<<<<同步完成>{name}")
                    return True
            else:
                if self.removefile(filelist[mynode-1]):
                    return True
            sleep(10)
        for i in filelist: self.removefile(i)
        self.touch同步文件()
        TimeErr(self.prefix+":barriernode>{name}<同步失败")
        return False
    #读取变量
    def read_dict(self,var_dict_file="position_dict.txt"):
        global 辅助
        #if 辅助: return {}
        import pickle
        var_dict={}
        if os.path.exists(var_dict_file):
            TimeECHO(self.prefix+"读取"+var_dict_file)
            with open(var_dict_file, 'rb') as f:
                var_dict = pickle.load(f)
        return var_dict
        #保存变量
    def save_dict(self,var_dict,var_dict_file="position_dict.txt"):
        global 辅助
        #if 辅助: return True
        import pickle
        f = open(var_dict_file, "wb") 
        pickle.dump(var_dict, f)
        f.close

    def bcastvar(self,mynode,totalnode,var,name="bcastvar"):
        if totalnode < 2:
            return var
        dict_file=name+".txt"
        if mynode == 0: self.save_dict(var,dict_file)
        self.barriernode(mynode,totalnode,name)
        if self.存在同步文件(): return var
        #
        var_new=self.read_dict(dict_file)
        for key in var:
            var[key] = var_new[key]
        return var
    def existsTHENtouch(self,png=Template(r"1.png"),keystr="",savepos=False):
        savepos=savepos and len(keystr) > 0 and self.savepos
        if savepos:
            if keystr in self.var_dict.keys():
                touch(self.var_dict[keystr])
                TimeECHO(self.prefix+"touch (saved) "+keystr)
                sleep(0.1)
                return True
        pos=exists(png)
        if pos:
            touch(pos)
            if len(keystr) > 0: TimeECHO(self.prefix+"touch "+keystr)
            if savepos:
                self.var_dict[keystr]=pos
                self.save_dict(self.var_dict,self.var_dict_file)
            return True
        else:
            if len(keystr) > 0:
                TimeECHO(self.prefix+"NotFound "+keystr)
            return False

    #
    #touch的总时长timelimit s, 或者总循环次数<10
    def LoopTouch(self,png=Template(r"1.png"),keystr="",limit=0,loop=10,savepos=False):
        timekey="LOOPTOUCH"+keystr+str(random.randint(1, 500))
        if limit + loop < 0.5: limit=0;loop=1
        self.timelimit(timekey=timekey,limit=limit,init=True)
        runloop=1
        while self.existsTHENtouch(png=png,keystr=keystr+f".{runloop}",savepos=savepos):
            if limit > 0:
                if self.timelimit(timekey=timekey,limit=limit,init=False):
                    TimeErr(self.prefix+"TOUCH"+keystr+"超时.....")
                    break
            if runloop > loop:
                TimeErr(self.prefix+"TOUCH"+keystr+"超LOOP.....")
                break
            sleep(10)
            runloop=runloop+1
        #
        if exists(png):
            TimeErr(keystr+"图片仍存在")
            return False
        else:
            return True
    def 同步等待(self,mynode,totalnode,同步文件="",sleeptime=60*5):
        同步文件=同步文件 if len(同步文件) > 1 else self.辅助同步文件
        if totalnode < 2: return True
        ionode= mynode == 0 or totalnode == 1
        self.filelist.append(同步文件)
        #同步等待是为了处理,程序因为各种原因无法同步,程序出粗.
        #重新校验各个进程
        #Step1. 检测到主文件{同步文件} 进入同步状态
        #Step2. 确定所有进程均检测到主文件状态
        #Step3. 检测其余进程是否都结束休息状态
        prefix=f"({mynode})"
        主辅节点通信完成=False
        发送信标=True
        #一个节点、一个节点的check
        if not os.path.exists(同步文件):return True
        TimeECHO(self.prefix+":进入同步等待")
        同步成功=True
        name=同步文件
        全部通信成功文件=同步文件+".同步完成.txt"
        self.filelist.append(全部通信成功文件)
        if ionode: self.removefile(全部通信成功文件)
        for i in np.arange(1,totalnode):
            if mynode > 0 and mynode != i: continue
            sleep(mynode*5)
            if not os.path.exists(同步文件): return True
            #
            主辅通信成功=False
            filename=f".tmp.barrier.mom.{i}.{name}.in.txt"
            if ionode:
                hour,minu,sec=self.time_getHMS()
                myrandom=str(random.randint(totalnode+100, 500))+f"{hour}{minu}{sec}"
                self.removefile(filename)
                self.touchfile(filename,content=myrandom)
                lockfile=f".tmp.barrier.mom.{myrandom}.{name}.in.txt"
                self.touchfile(lockfile)
                self.filelist.append(filename)
                self.filelist.append(lockfile)
                for sleeploop in np.arange(60*5):
                    if not os.path.exists(lockfile):
                        主辅通信成功=True
                        break
                    sleep(1)
                同步成功=同步成功 and 主辅通信成功
                if 同步成功:
                    TimeECHO(prefix+f"同步{i}成功")
                else:
                    TimeECHO(prefix+f"同步{i}失败")
                continue
            else:
                #辅助节点,找到特定
                for sleeploop in np.arange(60*(5+totalnode*5)):
                    if not 主辅通信成功:
                        myrandom=self.readfile(filename)[0].strip()
                        if len(myrandom) <=1:
                            sleep(1)
                            continue
                        lockfile=f".tmp.barrier.mom.{myrandom}.{name}.in.txt"
                        主辅通信成功=self.removefile(lockfile)
                        同步成功=False
                    else:
                        TimeECHO(prefix+f"正在寻找全部通信成功文件>{全部通信成功文件}<")
                        if os.path.exists(全部通信成功文件):
                            同步成功=True
                            break
                        sleep(5)
                    sleep(1)
        #到此处完成
        #因为是逐一进行同步的,所以全部通信成功文件只能由最后一个node负责删除
        if 同步成功:
            TimeECHO(prefix+"同步等待成功")
            if ionode:
                self.clean文件()
                self.touchfile(全部通信成功文件)
                self.removefile(同步文件)
        else:
            TimeErr(prefix+"同步等待失败")
            return False
        #
        sleep(sleeptime)
        self.barriernode(mynode,totalnode,"同步等待结束")
        return True
    
    def time_getHM(self):
        current_time=datetime.now(eastern_eight_tz)
        hour=current_time.hour
        minu=current_time.minute
        return hour,minu
    def time_getHMS(self):
        current_time=datetime.now(eastern_eight_tz)
        hour=current_time.hour
        minu=current_time.minute
        sec=current_time.second
        return hour,minu,sec
    



    #旧脚本,适合几个程序,自动商量node编号
    def autonode(self,totalnode):
        if totalnode < 2: return 0
        node=-10
        PID=os.getpid()
        filename="init_node."+str(totalnode)+"."+str(PID)+".txt"
        self.touchfile(filename)
        TimeECHO(self.prefix+"自动生成node中:"+filename)
        PID_dict={}
        for i in np.arange(60):
            for name in os.listdir("."):
                if "init_node."+str(totalnode)+"." in name:
                    PID_dict[name]=name
            if len(PID_dict) == totalnode: break
            sleep(5)
        if len(PID_dict) != totalnode:
            self.removefile(filename)
            TimeECHO(self.prefix+"文件数目不匹配")
            return node
        #
        strname=np.array(list(PID_dict.keys()))
        PIDarr=np.zeros(strname.size)
        for i in np.arange(PIDarr.size):
            PIDarr[i]=int(strname[i].split(".")[2])
        PIDarr=np.sort(PIDarr)
        for i in np.arange(PIDarr.size):
            TimeECHO(self.prefix+"i="+str(i)+". PID="+str(PID)+". PIDarr[i]="+str(PIDarr[i]))
            if PID == PIDarr[i]: node=i

        if node < 0:
            TimeECHO(self.prefix+"node < 0")
            self.removefile(filename)
            return node
        #
        TimeECHO(self.prefix+"mynode:"+str(node))
        if self.barriernode(node,totalnode,"audfonode"):
            self.removefile(filename)
            return node
    

class deviceOB:
    def __init__(self,设备类型="IOS",mynode=0,totalnode=1,LINK="ios:///http://192.168.12.130:8100",APPID=None):
        self.LINK=LINK
        self.device=None
        self.控制端=sys.platform.lower()
        if "darwin" in self.控制端: #避免和windows一致
            self.控制端="macos"
        self.设备类型=设备类型.lower()
        #设备ID,用于控制设备重启关闭省电等,为docker和虚拟机使用
        self.设备ID=None
        self.mynode=mynode
        self.prefix=f"({self.mynode})"
        self.totalnode=totalnode
        self.PID=-10 #Windows+Blustack专用,关闭特定虚拟机
        #
        self.连接设备()
        self.prefix=f"({self.mynode})"
        #APPID
        self.APPID="com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.APPID=APPID if APPID else self.APPID
        start_app(self.APPID)
        #
        self.实体终端=False
        self.实体终端 = "mac" in self.控制端 or "ios" in self.设备类型
        self.容器优化 = "linux" in self.控制端 and "android" in self.设备类型
        #


    #尝试连接timesMax次,当前是times次
    def 连接设备(self,times=1,timesMax=5):
        TimeECHO(self.prefix+f"{self.LINK}:开始第{times}次连接")
        try:
            self.device=connect_device(self.LINK)
            if self.device:
                TimeECHO(self.prefix+f"{self.LINK}:链接成功")
                return True
        except:
            TimeErr(self.prefix+f"{self.LINK}:链接失败")
        #
        if times <= timesMax:
            TimeECHO(self.prefix+f"{self.LINK}:链接失败,重启设备再次连接")
            sleep(random.randint(1, 30))
            self.启动设备()
            return self.连接设备(times+1,timesMax)
        else:
            TimeErr(self.prefix+f"{self.LINK}:链接失败,无法继续")
            return False
    def 启动设备(self):
        if "ios" in self.设备类型:
            try:
                TimeECHO(self.prefix+f"IOS测试重启中")
                os.system("tidevice wdaproxy -B  com.cndaqiang.WebDriverAgentRunner.xctrunner > tidevice.result.txt 2>&1 &")
            except:
                TimeECHO(self.prefix+f"IOS重启失败")
            sleep(10)
            return True
        #android
        try:
            if "mac" in self.控制端:
                TimeECHO(self.prefix+f"MAC暂不支持设备管理")
                return True
            if "win" in self.控制端: #BlueStack虚拟机
                CMDtitle="cndaqiangHDPlayer"+str(self.mynode)
                command=f"start \"{CMDtitle}\" /MIN C:\Progra~1\BlueStacks_nxt\HD-Player.exe --instance Nougat32_%{self.mynode}"
            if "linux" in self.控制端: #容器
                虚拟机ID=f"androidcontain{self.mynode}"
                command=f"docker restart {虚拟机ID}"
            exit_code = os.system(command)
            if exit_code == 0:
                sleep(60) #等待设备启动过程
                TimeECHO(self.prefix+f"启动成功")
                return True
            else:
                TimeErr(self.prefix+f"启动失败")
                return False
        except:
                TimeErr(self.prefix+f"启动失败")
                return False
    def 关闭设备(self):
        if "ios" in self.设备类型:
            TimeECHO(self.prefix+f"IOS暂不支持关闭")
            sleep(10)
            return True
        #android
        try:
            if "mac" in self.控制端:
                TimeECHO(self.prefix+f"MAC暂不支持设备管理")
                sleep(10)
                return True

            if "win" in self.控制端: #BlueStack虚拟机
                CMDtitle="cndaqiangHDPlayer"+str(mynode)
                command=f"start \"{CMDtitle}\" /MIN C:\Progra~1\BlueStacks_nxt\HD-Player.exe --instance Nougat32_%{self.mynode}"
                if int(self.PID) > 0:
                    command=f'taskkill /F /FI "PID eq {self.PID}"'
                else:# 关闭所有虚拟机，暂时用不到
                    command='taskkill /f /im HD-Player.exe'
            if "linux" in self.控制端: #容器
                虚拟机ID=f"androidcontain{self.mynode}"
                command=f"docker stop {虚拟机ID}"
            #
            exit_code = os.system(command)
            if exit_code == 0:
                TimeECHO(self.prefix+f"启动成功")
                return True
            else:
                TimeECHO(self.prefix+f"启动失败")
                return False
        except:
                TimeErr(self.prefix+f"启动失败")
                return False
    #
    def 重启设备(self,sleeptime=0):
        TimeECHO(self.prefix+f"重新启动{self.LINK}")
        self.关闭设备()
        sleeptime=max(10,sleeptime-60)
        printtime=max(30,sleeptime/10)
        TimeECHO(self.prefix+"sleep %d min"%(sleeptime/60))
        for i in np.arange(int(sleeptime/printtime)):
            TimeECHO(self.prefix+f"...taskkill_sleep: {i}",end='\r')
            sleep(printtime)
        self.启动设备()
        self.连接设备()

    #
    def 关闭APP(self):
        TimeECHO(self.prefix+f"关闭APP中")
        stop_app(self.APPID)
    def 打开APP(self):
        TimeECHO(self.prefix+f"打开APP中")
        start_app(self.APPID)
        sleep(20)

    def 重启APP(self,sleeptime=0):
        TimeECHO(self.prefix+f"重启APP中")
        try:
            self.关闭APP()
            TimeECHO(self.prefix+f"关闭程序")
        except:
            TimeErr(self.prefix+f"关闭程序失败")
        sleep(10)
        sleeptime=max(10,sleeptime)
        printtime=max(30,sleeptime/10)
        if sleeptime > 60*60: #>1h
            self.重启设备(sleeptime)
        else:
            print("sleep %d min"%(sleeptime/60))
            for i in np.arange(int(sleeptime/printtime)):
                TimeECHO(self.prefix+f"...taskkill_sleep: {i}",end='\r')
                sleep(printtime)
        TimeECHO(self.prefix+f"打开程序")
        self.打开APP()
        TimeECHO(self.prefix+f"打开程序成功")
        sleep(60*2)
        return True





class wzyd_libao:
   def __init__(self):
      self.Tool=DQWheel()
      self.体验币成功=False
      self.APPID="com.tencent.gamehelper.smoba"
      self.prefix="王者营地:"
   def RUN(self):
      self.体验货币()
      self.营地币兑换碎片()
      self.每日福利()
      stop_app(self.APPID)
   def 体验货币(self,times=0):
      TimeECHO(self.prefix+"体验币")
      start_app(self.APPID)
      sleep(5)
      times=times+1
      if times > 10: return False
      战绩图标=Template(r"tpl1699873801012.png", record_pos=(0.187, 0.726), resolution=(540, 960))
      if not self.Tool.existsTHENtouch(战绩图标,self.prefix+"战绩图标"): return self.体验货币(times)
      图标=Template(r"tpl1699873841208.png", record_pos=(-0.441, -0.809), resolution=(540, 960))
      if not self.Tool.existsTHENtouch(图标,self.prefix+"集合"): return self.体验货币(times)
      图标=Template(r"tpl1699873913813.png", record_pos=(-0.374, -0.043), resolution=(540, 960))
      if not self.Tool.existsTHENtouch(图标,self.prefix+"体验服"): return self.体验货币(times)
      图标=Template(r"tpl1699873941409.png", record_pos=(0.387, -0.128), resolution=(540, 960))
      if not self.Tool.existsTHENtouch(图标,self.prefix+"进入体验服"): return self.体验货币(times)
      图标=Template(r"tpl1699873949811.png", record_pos=(-0.006, 0.176), resolution=(540, 960))
      if not self.Tool.existsTHENtouch(图标,self.prefix+"奖励兑换"): return self.体验货币(times)
      #
      奖励页面=Template(r"tpl1699874011609.png", record_pos=(0.165, 0.48), resolution=(540, 960))
      pos=False
      for i in range(10):
          sleep(10)
          pos=exists(奖励页面)
          if pos: break
      if not pos:
         TimeECHO(self.prefix+"没进入奖励兑换页面")
         return self.体验货币(times)
      #
      swipe(pos, vector=[-0.0372, -0.5912])
      碎片奖励=Template(r"tpl1699874679212.png", record_pos=(-0.233, 0.172), resolution=(540, 960),threshold=0.9)
      奖励位置=False
      for i in range(10):
          sleep(2)
          奖励位置=exists(碎片奖励)
          if 奖励位置: break
          swipe(pos, vector=[-0.0372, -0.5912])
      if not 奖励位置:
         TimeECHO(self.prefix+"没找到体验币")
         return self.体验货币(times)
      #
      touch(奖励位置)
      成功领取=Template(r"tpl1699874950410.png", record_pos=(-0.002, -0.006), resolution=(540, 960))
      if exists(成功领取):
         TimeECHO(self.prefix+"成功领取")
      else:
         TimeECHO(self.prefix+"领取过了/体验币不够")
      return
      #
   
   def 每日福利(self):
      TimeECHO(self.prefix+"每日福利")
      #每日签到
      start_app(self.APPID)
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872241675.png", record_pos=(0.313, -0.372), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872252481.png", record_pos=(0.146, 0.446), resolution=(540, 960)))
      #每日任务
      sleep(5)
      start_app(self.APPID)
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872273081.png", record_pos=(0.326, 0.046), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872252481.png", record_pos=(0.146, 0.446), resolution=(540, 960)))
      return
   
   def 营地币兑换碎片(self,times=0):
      TimeECHO(self.prefix+"营地币兑换碎片")
      times=times+1
      if times > 10: return False
      start_app(self.APPID)
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960)))
      sleep(5)
      self.Tool.existsTHENtouch(Template(r"tpl1699872561488.png", record_pos=(-0.317, 0.331), resolution=(540, 960)))
      兑换页面=Template(r"tpl1699873075417.png", record_pos=(0.437, 0.167), resolution=(540, 960))
      pos=False
      for i in range(10):
          sleep(10)
          pos=exists(兑换页面)
          if pos: break
      if not pos:
         TimeECHO(self.prefix+"没进入营地币兑换页面")
         return self.营地币兑换碎片(times)
      swipe(pos, vector=[0.0156, -0.4067])
      碎片奖励=Template(r"tpl1699873407201.png", record_pos=(0.009, 0.667), resolution=(540, 960))
      奖励位置=False
      for i in range(10):
          sleep(2)
          奖励位置=exists(碎片奖励)
          if 奖励位置: break
          swipe(pos, vector=[0.0156, -0.4067])
      if not 奖励位置:
         TimeECHO(self.prefix+"没找到营地币")
         return self.营地币兑换碎片(times)
      touch(奖励位置)
      self.Tool.existsTHENtouch(Template(r"tpl1699873472386.png", record_pos=(0.163, 0.107), resolution=(540, 960)))
      self.Tool.existsTHENtouch(Template(r"tpl1699873480797.png", record_pos=(0.163, 0.104), resolution=(540, 960)))

class wzry_task:
#备注
#新账户,第一次打开各种模块,如万向天宫,会有动画等展示,脚本不做处理,手动点几下，之后就不会出现了
    def __init__(self,移动端,对战模式,shiftnode=-1,debug=False):
        self.移动端=移动端
        self.mynode=self.移动端.mynode
        self.totalnode=self.移动端.totalnode
        self.组队模式=self.totalnode > 1
        self.prefix=f"({self.mynode})"
        #
        self.房主=self.mynode == 0 or self.totalnode == 1
        self.对战时间=[5,24] #单位hour
        self.对战结束返回房间=True
        self.异常终止=False
        self.异常信息=None
        self.对战模式=对战模式 #"5v5匹配" or "王者模拟战"
        self.debug="darwin" in sys.platform.lower() #本地调试模式
        TimeECHO(self.prefix+f"对战模式:{self.对战模式}")
        self.选择人机模式=True
        self.选择英雄=True
        #
        self.Tool=DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.mynode}.txt",
                          mynode=self.mynode,totalnode=self.totalnode,容器优化=self.移动端.容器优化)
        if self.房主: self.Tool.init_clean()
        if self.totalnode > 1:
            self.Tool.touch同步文件()
            self.Tool.同步等待(self.mynode,self.totalnode,sleeptime=10)
        self.Tool.barriernode(self.mynode,self.totalnode,"WZRYinit")
        #.
        self.结束游戏FILE="WZRY.ENDGAME.txt"
        self.Tool.removefile(self.结束游戏FILE)
        #

        self.runinfo={}
        #一些图库
        self.大厅对战图标=Template(r"tpl1689666004542.png", record_pos=(-0.102, 0.145), resolution=(960, 540))
        #一些数据
        参战英雄线路_dict={}
        参战英雄头像_dict={}
        参战英雄线路_dict[(shiftnode+0)%6]=Template(r"tpl1689665490071.png", record_pos=(-0.315, -0.257), resolution=(960, 540)) 
        参战英雄头像_dict[(shiftnode+0)%6]=Template(r"tpl1685515357752.png", record_pos=(-0.359, 0.129), resolution=(960, 540))
        参战英雄线路_dict[(shiftnode+1)%6]=Template(r"tpl1689665455905.png", record_pos=(-0.066, -0.256), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+1)%6]=Template(r"tpl1691818492021.png", record_pos=(-0.278, 0.029), resolution=(960, 540))
        参战英雄线路_dict[(shiftnode+2)%6]=Template(r"tpl1689665540773.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+2)%6]=Template(r"tpl1690442530784.png", record_pos=(0.11, -0.083), resolution=(960, 540))
        参战英雄线路_dict[(shiftnode+3)%6]=Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+3)%6]=Template(r"tpl1690442560069.png", record_pos=(0.11, 0.025), resolution=(960, 540))
        参战英雄线路_dict[(shiftnode+4)%6]=Template(r"tpl1686048521443.png", record_pos=(0.06, -0.259), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+4)%6]=Template(r"tpl1689665521942.png", record_pos=(0.108, -0.086), resolution=(960, 540))
        参战英雄线路_dict[(shiftnode+5)%6]=Template(r"tpl1689665577871.png", record_pos=(0.183, -0.26), resolution=(960, 540))
        参战英雄头像_dict[(shiftnode+5)%6]=Template(r"tpl1690442560069.png", record_pos=(0.11, 0.025), resolution=(960, 540))
        self.参战英雄线路=参战英雄线路_dict[self.mynode%6]
        self.参战英雄头像=参战英雄头像_dict[self.mynode%6]
        self.备战英雄线路=参战英雄线路_dict[(self.mynode+3)%6]
        self.备战英雄头像=参战英雄头像_dict[(self.mynode+3)%6]

    #网络优化提示
    def 网络优化(self):
        if exists(Template(r"tpl1693669091002.png", record_pos=(-0.003, -0.015), resolution=(960, 540))):
            TimeECHO(self.prefix+"网络优化提示")
            self.Tool.existsTHENtouch(Template(r"tpl1693669117249.png", record_pos=(-0.102, 0.116), resolution=(960, 540)),"下次吧")
    def 确定按钮(self):
        确定按钮=[]
        确定按钮.append(Template(r"tpl1693194657793.png", record_pos=(0.001, 0.164), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1693886962076.png", record_pos=(0.097, 0.115), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1693660628972.png", record_pos=(-0.003, 0.118), resolution=(960, 540)))
        确定按钮.append(Template(r"tpl1689666290543.png", record_pos=(-0.001, 0.152), resolution=(960, 540),threshold=0.8))
        for i in 确定按钮:
            self.Tool.existsTHENtouch(i,f"确定{i}",savepos=False)
    def 关闭按钮(self):
        关闭按钮=[]
        关闭按钮.append(Template(r"tpl1692947351223.png",record_pos=(0.428, -0.205), resolution=(960, 540),threshold=0.9))
        关闭按钮.append(Template(r"tpl1699616162254.png", record_pos=(0.38, -0.237), resolution=(960, 540),threshold=0.9))
        关闭按钮.append(Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540)))
        关闭按钮.append(Template(r"tpl1693271987720.png", record_pos=(0.428, -0.205), resolution=(960, 540),threshold=0.9))
        for i in 关闭按钮:
            self.Tool.LoopTouch(i,f"确定{i}",savepos=False)
        #
    def 进入大厅(self,times=1):
        TimeECHO(self.prefix+"尝试进入大厅")
        if self.Tool.存在同步文件(): return True
        self.移动端.打开APP()
        if self.判断大厅中():
            return True
        if self.判断对战中():
            self.Tool.timelimit(timekey="结束对战",limit=60*15)
            处理对战="模拟战" in self.对战模式
            if self.mynode > 2: 处理对战=True
            while self.判断对战中(处理对战):
                TimeECHO(self.prefix+"尝试进入大厅:对战sleep")
                sleep(30)
                if self.Tool.timelimit(timekey="结束对战",limit=60*15,init=False): break
            self.结束人机匹配()
        战绩页面=[]
        战绩页面.append(Template(r"tpl1699677816333.png", record_pos=(0.408, 0.226), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1699677826933.png", record_pos=(-0.011, -0.257), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1699766285319.png", record_pos=(-0.009, -0.257), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1699677835926.png", record_pos=(0.011, -0.134), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1699677870739.png", record_pos=(-0.369, 0.085), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1689727624208.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
        战绩页面.append(Template(r"tpl1689667038979.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
                
        战绩页面中=False 
        for i in 战绩页面:
            if exists(i):
                战绩页面中=True
                TimeECHO(self.prefix+"尝试进入大厅:战绩页面")
                break
        if 战绩页面中: self.结束人机匹配()
        self.网络优化()
        #各种异常，异常图标,比如网速不佳、画面设置、
        self.Tool.existsTHENtouch(Template(r"tpl1692951507865.png", record_pos=(-0.106, 0.12), resolution=(960, 540),threshold=0.9),"关闭画面设置")
        #更新资源
        WIFI更新资源=Template(r"tpl1694357134235.png", record_pos=(-0.004, -0.019), resolution=(960, 540))
        if exists(WIFI更新资源):
            self.Tool.existsTHENtouch(Template(r"tpl1694357142735.png", record_pos=(-0.097, 0.116), resolution=(960, 540)))
        if self.判断大厅中():return True
        #更新图形显示设置
        显示设置=Template(r"tpl1694359268612.png", record_pos=(-0.002, 0.12), resolution=(960, 540))
        if exists(显示设置):
            self.Tool.existsTHENtouch(Template(r"tpl1694359275922.png", record_pos=(-0.113, 0.124), resolution=(960, 540)))
        if self.判断大厅中():return True
        #
        if self.Tool.存在同步文件(): return True
        self.登录游戏()
        #返回图标
        返回图标=Template(r"tpl1692949580380.png", record_pos=(-0.458, -0.25), resolution=(960, 540),threshold=0.9)
        self.Tool.LoopTouch(返回图标,"返回图标",loop=5,savepos=False)
        if self.判断大厅中():return True
        self.确定按钮()
        if exists(Template(r"tpl1693886922690.png", record_pos=(-0.005, 0.114), resolution=(960, 540))):
            self.Tool.existsTHENtouch(Template(r"tpl1693886962076.png", record_pos=(0.097, 0.115), resolution=(960, 540)),"确定按钮")
        if self.判断大厅中():return True
        if self.Tool.存在同步文件(): return True
        #邀请
        if exists(Template(r"tpl1692951548745.png", record_pos=(0.005, 0.084), resolution=(960, 540))):
            关闭邀请=Template(r"tpl1692951558377.png", record_pos=(0.253, -0.147), resolution=(960, 540),threshold=0.9)
            self.Tool.LoopTouch(关闭邀请,"关闭邀请",loop=5,savepos=False)
        if self.判断大厅中():return True
        if self.Tool.存在同步文件(): return True
        #
        times=times+1
        #
        if self.健康系统():
            if self.组队:
                self.Tool.touch同步文件()
                sleep(30)
                return True
            else:
                self.移动端.重启APP(60*20)
                return self.进入大厅(times)
        #次数上限
        if times < 15 and times%4 == 0:
            self.移动端.重启APP(10)
        if times > 15:
            if self.组队:
                TimeErr(self.prefix+"进入大厅times太多,创建同步文件")
                self.Tool.touch同步文件()
                return True
            else:
               self.移动端.关闭APP()
               return False

    def 登录游戏(self):
        #更新公告
        if self.Tool.存在同步文件(): return True
        更新公告=Template(r"tpl1692946575591.png", record_pos=(0.103, -0.235), resolution=(960, 540),threshold=0.9)
        self.移动端.打开APP()
        if exists(更新公告):
            for igengxin in np.arange(30):
                TimeECHO(self.prefix+"更新中%d"%(igengxin))
                关闭更新=Template(r"tpl1693446444598.png", record_pos=(0.428, -0.205), resolution=(960, 540),threshold=0.9)
                if self.Tool.existsTHENtouch(关闭更新,"关闭更新",savepos=False):
                    sleep(10)
                    break
                if exists(Template(r"tpl1692946702006.png", record_pos=(-0.009, -0.014), resolution=(960, 540),threshold=0.9)):
                    TimeECHO(self.prefix+"更新完成")
                    touch(Template(r"tpl1692946738054.png", record_pos=(-0.002, 0.116), resolution=(960, 540),threshold=0.9))
                    sleep(60)
                    break
                elif not exists(更新公告):
                    TimeECHO(self.prefix+"找不到更新公告.break")
                    break
                if exists(Template(r"tpl1692952266315.png", record_pos=(-0.411, 0.266), resolution=(960, 540),threshold=0.9)): TimeECHO(self.prefix+"正在下载资源包")
                sleep(60)
        if exists(Template(r"tpl1692946837840.png", record_pos=(-0.092, -0.166), resolution=(960, 540),threshold=0.9)):
            TimeECHO(self.prefix+"同意游戏")
            touch(Template(r"tpl1692946883784.png", record_pos=(0.092, 0.145), resolution=(960, 540),threshold=0.9))
        #这里需要重新登录了
        if exists(Template(r"tpl1692946938717.png", record_pos=(-0.108, 0.159), resolution=(960, 540),threshold=0.9)):
            TimeECHO(self.prefix+"需要重新登录")
            if self.移动端.容器优化: 
                TimeECHO(self.prefix+"需要重新登录")
                self.移动端.重启APP(60*60*4)
            else:
                TimeErr(self.prefix+"需要重新登录:创建同步文件")
                self.Tool.touch同步文件()
                self.异常终止=True
                self.异常信息="需要重新登录"
                return
        #
        #
        if exists(Template(r"tpl1692951324205.png", record_pos=(0.005, -0.145), resolution=(960, 540))):
            TimeECHO(self.prefix+"关闭家长莫模式")
            touch(Template(r"tpl1692951358456.png", record_pos=(0.351, -0.175), resolution=(960, 540)))
            sleep(5)
        #现在打开可能会放一段视频，怎么跳过呢？使用0.1的精度测试一下.利用历史记录了
        随意点击=Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540),threshold=0.9)
        self.Tool.existsTHENtouch(随意点击,"随意点击k",savepos=True)
        #
        开始游戏=Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540),threshold=0.9)
        if self.Tool.existsTHENtouch(开始游戏,"登录界面.开始游戏",savepos=False):
            sleep(10)

        #
        用户协议同意=Template(r"tpl1692952132065.png", record_pos=(0.062, 0.099), resolution=(960, 540),threshold=0.9)
        self.Tool.existsTHENtouch(用户协议同意,"用户协议同意")
        #
        #动态下载资源提示
        回归礼物=Template(r"tpl1699607355777.png", resolution=(1136, 640))
        if exists(回归礼物):
            self.Tool.existsTHENtouch(Template(r"tpl1699607371836.png", resolution=(1136, 640)))
        回归挑战=Template(r"tpl1699680234401.png", record_pos=(0.314, 0.12), resolution=(1136, 640))
        self.Tool.existsTHENtouch(回归挑战,"不进行回归挑战")

        动态下载资源=Template(r"tpl1697785792245.png", record_pos=(-0.004, -0.009), resolution=(960, 540))
        if exists(动态下载资源):
            取消=Template(r"tpl1697785803856.png", record_pos=(-0.099, 0.115), resolution=(960, 540))
            self.Tool.existsTHENtouch(取消,"取消按钮")
        #活动界面
        今日不再弹出=Template(r"tpl1693272038809.png", record_pos=(0.38, 0.215), resolution=(960, 540),threshold=0.9)
        活动关闭图标1=Template(r"tpl1692947351223.png",record_pos=(0.428, -0.205), resolution=(960, 540),threshold=0.9)
        活动关闭图标2=Template(r"tpl1699616162254.png", record_pos=(0.38, -0.237), resolution=(960, 540),threshold=0.9)
        活动关闭图标3=Template(r"tpl1692951432616.png", record_pos=(0.346, -0.207), resolution=(960, 540))
        活动关闭图标4=Template(r"tpl1693271987720.png", record_pos=(0.428, -0.205), resolution=(960, 540),threshold=0.9)
        特殊关闭图标1=活动关闭图标4
        关闭图标集合=[]
        关闭图标集合.append(活动关闭图标1)
        关闭图标集合.append(活动关闭图标2)
        关闭图标集合.append(活动关闭图标3)
        关闭图标集合.append(活动关闭图标4)
        关闭图标集合.append(特殊关闭图标1)
        #
        self.Tool.timelimit(timekey="活动关闭",limit=60*5,init=True)
        for i in 关闭图标集合:
            self.Tool.LoopTouch(i,f"活动关闭集合{i}",loop=3,savepos=False)
            if self.判断大厅中(): return True
        #
        while exists(今日不再弹出):#当活动海报太大时，容易识别关闭图标错误，此时采用历史的关闭图标位置
            TimeECHO(self.prefix+"今日不再弹出仍在")
            for i in 关闭图标集合:
                self.Tool.LoopTouch(i,f"活动关闭集合{i}",loop=5,savepos=True)
                if self.判断大厅中(): return True
            else:
                sleep(10)
            if self.Tool.timelimit(timekey="活动关闭",limit=60,init=False): break
        #
        if self.判断大厅中(): return True

    




    def 单人进入人机匹配房间(self,times=1):
        if self.Tool.存在同步文件(): return True
        if "模拟战" in self.对战模式:
            TimeECHO(self.prefix+"单人进入人机匹配房间_模拟战")
            return self.单人进入人机匹配房间_模拟战(times)
        #
        TimeECHO(self.prefix+"单人进入人机匹配房间")
        if self.判断对战中(): self.结束人机匹配()
        if self.判断房间中(): return True
        self.进入大厅()
        if self.Tool.存在同步文件(): return True
        TimeECHO(self.prefix+"进入大厅,开始进入匹配房间")
        if times == 1:
            self.Tool.timelimit(timekey="单人进入人机匹配房间",limit=60*10,init=True)
        #
        times=times+1
        if not self.Tool.existsTHENtouch(self.大厅对战图标,"大厅对战",savepos=False):
            TimeErr(self.prefix+"找不到大厅对战图标")
            return self.单人进入人机匹配房间(times)
        #
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666019941.png", record_pos=(-0.401, 0.098), resolution=(960, 540)),"5v5王者峡谷",savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666034409.png", record_pos=(0.056, 0.087), resolution=(960, 540)),"人机",savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        if self.选择人机模式:
            TimeECHO(self.prefix+"选择对战模式")
            if not self.Tool.existsTHENtouch(Template(r"tpl1689666057241.png", record_pos=(-0.308, -0.024), resolution=(960, 540)),"快速模式"):
                return self.单人进入人机匹配房间(times)
            # 选择难度
            青铜段位=True
            if 青铜段位:
                段位=Template(r"tpl1689666083204.png", record_pos=(0.014, -0.148), resolution=(960, 540))
            else:
                段位=Template(r"tpl1689666092009.png", record_pos=(0.0, 0.111), resolution=(960, 540))
            self.选择人机模式 = not self.Tool.existsTHENtouch(段位,"选择段位",savepos=True)
        #
        # 开始练习
        开始练习 = Template(r"tpl1689666102973.png", record_pos=(0.323, 0.161), resolution=(960, 540),threshold=0.9)
        if not self.Tool.existsTHENtouch(开始练习,"开始练习"): return self.单人进入人机匹配房间(times)
        sleep(10)
        if not self.判断房间中():
            #有时候长时间不进去被禁赛了
            while self.Tool.existsTHENtouch(Template(r"tpl1689667950453.png", record_pos=(-0.001, 0.111), resolution=(960, 540)),"不匹配被禁赛的确定按钮"):
                sleep(20)
                if self.Tool.existsTHENtouch(开始练习,"开始练习"): sleep(10)
                if self.Tool.timelimit(timekey="单人进入人机匹配房间",limit=60*10,init=False):
                    TimeErr(self.prefix+":单人进入人机匹配房间超时,touch同步文件")
                    self.Tool.touch同步文件()
                    return True
            return self.单人进入人机匹配房间(times)
        return True


    def 进入人机匹配房间(self):
        if self.Tool.存在同步文件(): return True
        self.单人进入人机匹配房间()
        if not self.组队模式: return
        #...............................................................
        #当多人组队模式时，这里要暂时保证是房间中，因为邀请系统还没写好
        self.Tool.barriernode(self.mynode,self.totalnode,"组队进房间")
        if not self.房主: sleep(self.mynode*10)
        self.Tool.timelimit(timekey=f"组队模式进房间{self.mynode}",limit=60*5,init=True)
        if self.Tool.存在同步文件(): return True
        取消准备=Template(r"tpl1699179402893.png", record_pos=(0.098, 0.233), resolution=(960, 540),threshold=0.9)
        if not self.房主:
            self.Tool.timelimit(timekey=f"辅助进房{self.mynode}",limit=60*5,init=True)
            while not exists(取消准备):
                if self.Tool.timelimit(timekey=f"辅助进房{self.mynode}",limit=60*5,init=False): break
                if self.Tool.存在同步文件(): return True
                #
                #需要小号和主号建立亲密关系，并在主号中设置亲密关系自动进入房间
                TimeECHO(self.prefix+"不在房间中")
                self.单人进入人机匹配房间()
                进房=Template(r"tpl1699181922986.png", record_pos=(0.46, -0.15), resolution=(960, 540),threshold=0.9)
                进房间=Template(r"tpl1699181937521.png", record_pos=(0.348, -0.194), resolution=(960, 540),threshold=0.9)
                if self.Tool.existsTHENtouch(进房):
                    取消确定=Template(r"tpl1699712554213.png", record_pos=(0.003, 0.113), resolution=(960, 540))
                    取消=Template(r"tpl1699712559021.png", record_pos=(-0.096, 0.115), resolution=(960, 540))
                    if exists(取消确定):
                        TimeECHO(self.prefix+"点击房间错误,返回")
                        self.Tool.existsTHENtouch(取消,"取消错误房间")
                        continue
                    self.Tool.existsTHENtouch(取消,"取消错误房间")
                    TimeECHO(self.prefix+"找到房间")
                    if self.Tool.existsTHENtouch(进房间):
                        TimeECHO(self.prefix+"尝试进入房间中")
        self.Tool.barriernode(self.mynode,self.totalnode,"结束组队进房间")
        return
    def 单人进入人机匹配房间_模拟战(self,times=1):
        if self.判断对战中(): self.结束人机匹配()
        if self.判断房间中(): return True
        self.进入大厅()
        if self.Tool.存在同步文件(): return True
        TimeECHO(self.prefix+"大厅中.开始进入模拟战房间")
        万象天工=Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540))
        if not self.Tool.existsTHENtouch(万象天工,"万象天工"):
            self.单人进入人机匹配房间_模拟战(times)
        #

        王者模拟战图标=Template(r"tpl1693660105012.png", record_pos=(-0.435, -0.134), resolution=(960, 540))
        任意位置继续=Template(r"tpl1693660122898.png", record_pos=(0.001, 0.252), resolution=(960, 540))#多次
        任意位置继续2=Template(r"tpl1693660165029.png", record_pos=(-0.001, 0.244), resolution=(960, 540))
        任意位置继续3=Template(r"tpl1693660182958.png", record_pos=(-0.004, 0.25), resolution=(960, 540))
        self.Tool.existsTHENtouch(王者模拟战图标,"王者模拟战图标")
        while self.Tool.existsTHENtouch(任意位置继续,"任意位置继续"): sleep(5)
        while self.Tool.existsTHENtouch(任意位置继续2,"任意位置继续"): sleep(5)
        while self.Tool.existsTHENtouch(任意位置继续3,"任意位置继续"): sleep(5)
        图标1=Template(r"tpl1693660308858.png", record_pos=(0.0, -0.071), resolution=(960, 540))
        图标2=Template(r"tpl1693660322376.png", record_pos=(0.059, 0.161), resolution=(960, 540))
        if self.Tool.existsTHENtouch(图标1,"图标1"): sleep(5)
        if self.Tool.existsTHENtouch(图标2,"图标2"): sleep(5)
    #新手要跳过教学局,自己先跳过
        #
        #
        进入队列失败=Template(r"tpl1693660615126.png", record_pos=(-0.19, -0.141), resolution=(960, 540))
        确定失败=Template(r"tpl1693660628972.png", record_pos=(-0.003, 0.118), resolution=(960, 540))
        邀请好友=Template(r"tpl1693660666527.png", record_pos=(0.408, 0.166), resolution=(960, 540)) #就是进入房间
        self.Tool.LoopTouch(邀请好友,"邀请好友",loop=10)
        while exists(进入队列失败):
            self.Tool.existsTHENtouch(确定失败)
            sleep(20)
            self.Tool.existsTHENtouch(邀请好友,"邀请好友")
        if self.判断房间中(): return True
        #
        if self.判断房间中():
            return True
        else:
            return self.单人进入人机匹配房间(times)

    def 进行人机匹配(self,times=1):
        if self.Tool.存在同步文件(): return True
        if times == 1:
            self.Tool.timelimit(timekey="进行人机匹配",limit=60*10,init=True)
        times=times+1
        if not self.判断房间中():
            self.Tool.touch同步文件()
            TimeErr(self.prefix+":不在房间中,无法进行匹配")
        #
        self.Tool.timelimit(timekey="确认匹配",limit=60*1,init=True)
        self.Tool.timelimit(timekey="超时确认匹配",limit=60*5,init=True)
        #
        while True:
            房间中的开始按钮=Template(r"tpl1689666117573.png", record_pos=(0.096, 0.232), resolution=(960, 540))
            if self.房主:
                if self.判断房间中(): 
                    self.Tool.existsTHENtouch(房间中的开始按钮,"开始匹配按钮")
                else:
                    TimeECHO(self.prefix+":不在房间中,无法点击匹配按钮")
            if self.Tool.timelimit(timekey="确认匹配",limit=60*1,init=False): TimeErr(self.prefix+"超时,队友未确认匹配或大概率程序卡死")
            if self.Tool.timelimit(timekey="超时确认匹配",limit=60*5,init=False): 
                TimeErr(self.prefix+"超时太久,退出匹配")
                return False
            自己确定匹配 = self.Tool.existsTHENtouch(Template(r"tpl1689666290543.png", record_pos=(-0.001, 0.152), resolution=(960, 540),threshold=0.8),"确定匹配按钮")
            if 自己确定匹配: sleep(15) #自己确定匹配后给流出时间
            队友确认5v5匹配 = exists(Template(r"tpl1689666311144.png", record_pos=(-0.394, -0.257), resolution=(960, 540),threshold=0.9))
            #
            if "模拟战" in self.对战模式:
                if 队友确认5v5匹配:
                    TimeErr(self.prefix+":模拟战误入5v5")
                    self.进入大厅()
                    self.Tool.touch同步文件()
                    return
                队友确认匹配=self.判断对战中()
                if 队友确认匹配:
                    TimeECHO(self.prefix+":队友确认匹配")
                    return True#模拟战确定匹配后就结束了
                else:
                    TimeECHO(self.prefix+":队友未确认匹配")
                    continue
            else:
                队友确认匹配=队友确认5v5匹配
            if 队友确认匹配: break
            sleep(2)
        #
        #选择英雄
        if self.选择英雄 and self.Tool.existsTHENtouch(Template(r"tpl1689666324375.png", record_pos=(-0.297, -0.022), resolution=(960, 540)),"展开英雄",savepos=False):
            sleep(1)
            self.Tool.existsTHENtouch(self.参战英雄线路,"参战英雄线路",savepos=True)
            sleep(5)
            self.Tool.existsTHENtouch(self.参战英雄头像,"参战英雄头像",savepos=True)
            sleep(1)
            #分路重复.png
            if exists(Template(r"tpl1689668119154.png", record_pos=(0.0, -0.156), resolution=(960, 540))):
                TimeECHO(self.prefix+"分路冲突，切换英雄")
                #分路重复取消按钮.png
                if self.Tool.existsTHENtouch(Template(r"tpl1689668138416.png", record_pos=(-0.095, 0.191), resolution=(960, 540)),"冲突取消英雄",savepos=False):
                    #选择备选英雄
                    self.Tool.existsTHENtouch(self.备战英雄线路,"备战英雄线路",savepos=True)
                    self.Tool.existsTHENtouch(self.备战英雄头像,"备战英雄",savepos=True)
            #确定英雄后一般要等待队友确定，这需要时间
            sleep(5)
            #   确定
            self.Tool.existsTHENtouch(Template(r"tpl1689666339749.png", record_pos=(0.421, 0.237), resolution=(960, 540)),"确定英雄",savepos=True) #这里是用savepos的好处就是那个英雄的熟练度低点哪个英雄
            sleep(5)
            #万一是房主
            self.Tool.existsTHENtouch(Template(r"tpl1689666339749.png", record_pos=(0.421, 0.237), resolution=(960, 540)),"确定阵容",savepos=True)
            sleep(5)
        #加载游戏界面
        加载游戏界面=Template(r"tpl1693143323624.png", record_pos=(0.003, -0.004), resolution=(960, 540))
        self.Tool.timelimit(timekey="加载游戏",limit=60*5,init=True)
        加载中=exists(加载游戏界面)
        while True:
            if not 加载中:
                加载中=exists(加载游戏界面)
            if 加载中:
                TimeECHO(self.prefix+"加载游戏中.....")
                self.Tool.existsTHENtouch(Template(r"tpl1689666367752.png", record_pos=(0.42, -0.001), resolution=(960, 540)),"加油按钮",savepos=False)
                sleep(10)
                if self.Tool.容器优化: sleep(30) #貌似容器容易开在这个界面ß
                if not exists(加载游戏界面): break
            if self.Tool.timelimit(timekey="加载游戏",limit=60*10,init=False):
                if self.Tool.容器优化: break
                TimeECHO(self.prefix+"加载时间过长.....重启APP")
                self.移动端.重启APP(10)
                return False
            sleep(10)
        #

    def 结束人机匹配(self):
        if self.Tool.存在同步文件(): return True
        if "模拟战" in self.对战模式:
            return self.结束人机匹配_模拟战()        
        self.Tool.timelimit(timekey="结束人机匹配",limit=60*15,init=True)
        jixu=False
        返回房间按钮=Template(r"tpl1689667226045.png", record_pos=(0.079, 0.226), resolution=(960, 540),threshold=0.9)
        while True:
            if self.Tool.存在同步文件(): return True
            if exists(返回房间按钮): jixu=True
            if self.Tool.timelimit(timekey="结束人机匹配",limit=60*15,init=False):
                TimeErr(self.prefix+"结束人机匹配时间超时")
                self.Tool.touch同步文件()
                return self.进入大厅()
            if self.健康系统() or self.判断大厅中():
                TimeErr(self.prefix+"结束人机匹配:健康系统or处在大厅")
                return True
            if self.判断房间中(): return
            #
            游戏结束了=Template(r"tpl1694360304332.png", record_pos=(-0.011, -0.011), resolution=(960, 540))
            if exists(游戏结束了):
                self.Tool.existsTHENtouch(Template(r"tpl1694360310806.png", record_pos=(-0.001, 0.117), resolution=(960, 540)))

            #有时候会莫名进入分享界面
            if exists(Template(r"tpl1689667038979.png", record_pos=(0.235, -0.125), resolution=(960, 540))):
                TimeECHO(self.prefix+"分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png"))
                jixu=True
                sleep(2)

            #有时候会莫名进入MVP分享界面
            pos=exists(Template(r"tpl1689727624208.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
            if pos:
                TimeECHO(self.prefix+"mvp分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540)))
                jixu=True
                sleep(2)
            #
            #都尝试一次返回
            if self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540))):
                sleep(2)
            self.确定按钮()

            if self.Tool.existsTHENtouch(Template(r"tpl1689667161679.png", record_pos=(-0.001, 0.226), resolution=(960, 540))):
                TimeECHO(self.prefix+"MVP继续")
                jixu=True
                sleep(2)

            #胜利页面继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689668968217.png", record_pos=(0.002, 0.226), resolution=(960, 540))):                        
                TimeECHO(self.prefix+"继续1/3")
                jixu=True
                sleep(2)
            #显示mvp继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689669015851.png", record_pos=(-0.002, 0.225), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续2/3")
                jixu=True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1689669071283.png", record_pos=(-0.001, -0.036), resolution=(960, 540))):
                TimeECHO(self.prefix+"友情积分继续2/3")
                jixu=True
                self.Tool.existsTHENtouch(Template(r"tpl1689669113076.png", record_pos=(-0.002, 0.179), resolution=(960, 540)))
                sleep(2)

            #todo, 暂时为空
            if self.Tool.existsTHENtouch(Template(r"tpl1689670032299.png", record_pos=(-0.098, 0.217), resolution=(960, 540))):
                TimeECHO(self.prefix+"超神继续3/3")
                jixu=True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1692955597109.png", record_pos=(-0.095, 0.113), resolution=(960, 540))):
                TimeECHO(self.prefix+"网络卡顿提示")
                jixu=True
                sleep(2)         
            #
            sleep(10)  
            if not jixu:
                if self.Tool.timelimit(timekey="结束人机匹配",limit=60*2,init=False):
                    jixu=True
                TimeECHO(self.prefix+"未监测到继续,sleep...")
                sleep(20)
                continue
            # 返回大厅
            # 因为不能保证返回辅助账户返回房间，所以返回大厅更稳妥
            if self.对战结束返回房间:
                if self.Tool.existsTHENtouch(返回房间按钮,"返回房间"):
                    sleep(10)
                self.网络优化()
                if self.判断房间中(): return
            else:
                if self.Tool.existsTHENtouch(Template(r"tpl1689667243845.png", record_pos=(-0.082, 0.221), resolution=(960, 540),threshold=0.9),"返回大厅"):
                    sleep(10)
                    if self.Tool.existsTHENtouch(Template(r"tpl1689667256973.png", record_pos=(0.094, 0.115), resolution=(960, 540)),"确定返回大厅"):
                        sleep(10)
                if self.判断大厅中(): return            
    #
    def 结束人机匹配_模拟战(self):
        TimeECHO(self.prefix+"准备结束本局")
        if self.Tool.存在同步文件(): return True
        self.Tool.timelimit(timekey="结束人机匹配",limit=60*20,init=True)
        self.Tool.barriernode(self.mynode,self.totalnode,"checkend_init")
        while True:
            if self.Tool.timelimit(timekey="结束人机匹配",limit=60*30,init=False) or self.健康系统() or self.判断大厅中():
                TimeErr(self.prefix+"结束游戏时间过长 OR 健康系统 OR 大厅中")
                return self.进入大厅()
            if self.判断房间中(): return
            if self.判断对战中(False):
                sleeploop=0
                while self.判断对战中(True): #开始处理准备结束
                    sleep(10)
                    sleeploop=sleeploop+1
                    if sleeploop > 20: break #虚拟机王者程序卡住了
                #++++++滴哦
                for loop in range(30):#等待时间太长
                    if exists(Template(r"tpl1690545494867.png", record_pos=(0.0, 0.179), resolution=(960, 540))):
                        TimeECHO(self.prefix+"正在退出")
                        if self.Tool.existsTHENtouch(Template(r"tpl1690545545580.png", record_pos=(-0.101, 0.182), resolution=(960, 540))):
                            TimeECHO(self.prefix+"点击退出")
                            break
                    sleep(30)
            if self.判断房间中(): return
            if self.判断大厅中(): return

            if self.Tool.existsTHENtouch(Template(r"tpl1690545762580.png", record_pos=(-0.001, 0.233), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续1")
                jixu=True
                sleep(5)
            if self.Tool.existsTHENtouch(Template(r"tpl1690545802859.png", record_pos=(0.047, 0.124), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续2")
                jixu=True
                sleep(5)            
            if self.Tool.existsTHENtouch(Template(r"tpl1690545854354.png", record_pos=(0.002, 0.227), resolution=(960, 540))):
                TimeECHO(self.prefix+"继续3")
                jixu=True
                sleep(5)             
            #
            # 因为不能保证返回辅助账户返回房间，所以返回大厅更稳妥
            if exists(Template(r"tpl1690545925867.png", record_pos=(-0.001, 0.241), resolution=(960, 540))):
                if self.对战结束返回房间:
                    if self.Tool.existsTHENtouch(Template(r"tpl1690545951270.png", record_pos=(0.075, 0.239), resolution=(960, 540)),"返回房间",savepos=True):
                        sleep(10)
    #@todo ,添加barrier
                        if self.判断房间中(): break 
            if self.判断房间中(): return
            if self.判断大厅中(): return
    #
    def 每日礼包(self):
        if self.Tool.存在同步文件(): return True
        self.每日礼包_每日任务()
        self.每日礼包_邮件礼包()
        self.每日礼包_妲己礼物()
        if self.mynode == 0:
            if "android" in self.移动端.设备类型:
                try:
                    王者营地=wzyd_libao()
                    王者营地.RUN()
                    TimeECHO(self.prefix+"王者营地礼包通过")
                except:
                    TimeECHO(self.prefix+"王者营地礼包出错")
            self.移动端.打开APP()


    def 每日礼包_每日任务(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO(self.prefix+"领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        #
        #每日任务
        TimeECHO(self.prefix+"领任务礼包:每日任务")
        赛季任务界面=Template(r"tpl1693294751097.png", record_pos=(-0.11, -0.001), resolution=(960, 540))
        任务=Template(r"tpl1693192971740.png", record_pos=(0.204, 0.241), resolution=(960, 540),threshold=0.9)
        self.Tool.existsTHENtouch(任务,"任务按钮")
        if not exists(赛季任务界面):
            if not self.判断大厅中(): self.进入大厅()
            if self.Tool.existsTHENtouch(任务,"任务按钮"):
                sleep(10)
                点击屏幕继续=Template(r"tpl1693193459695.png", record_pos=(0.006, 0.223), resolution=(960, 540))
                self.Tool.existsTHENtouch(点击屏幕继续,"点击屏幕继续")
                sleep(5)
            if not exists(赛季任务界面): return self.每日礼包_每日任务(times)
        #
        一键领取 =Template(r"tpl1693193500142.png", record_pos=(0.392, 0.227), resolution=(960, 540))
        今日活跃 =Template(r"tpl1693192993256.png", record_pos=(0.228, -0.239), resolution=(960, 540))
        本周活跃1=Template(r"tpl1693359350755.png", record_pos=(0.401, -0.241), resolution=(960, 540))
        本周活跃2=Template(r"tpl1693193026234.png", record_pos=(0.463, -0.242), resolution=(960, 540))
        确定按钮=Template(r"tpl1693194657793.png", record_pos=(0.001, 0.164), resolution=(960, 540))
        返回=Template(r"tpl1694442171115.png", record_pos=(-0.441, -0.252), resolution=(960, 540))
        if self.Tool.existsTHENtouch(一键领取 ,"一键领取 "): self.Tool.existsTHENtouch(确定按钮,"确定"); sleep(5)
        if self.Tool.existsTHENtouch(今日活跃 ,"今日活跃 "): self.Tool.existsTHENtouch(确定按钮,"确定"); sleep(5)
        if self.Tool.existsTHENtouch(本周活跃1,"本周活跃1"): self.Tool.existsTHENtouch(确定按钮,"确定"); sleep(5)
        if self.Tool.existsTHENtouch(本周活跃2,"本周活跃2"): self.Tool.existsTHENtouch(确定按钮,"确定"); sleep(5)
        #
        self.Tool.LoopTouch(返回,"返回")
        self.确定按钮()
        return True
        #
        #邮件礼包
    def 每日礼包_邮件礼包(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO(self.prefix+"领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        TimeECHO(self.prefix+"领任务礼包:领邮件礼包")
        邮件图标=Template(r"tpl1694441018032.png", record_pos=(0.35, -0.251), resolution=(960, 540))
        好友邮件=Template(r"tpl1694441042380.png", record_pos=(-0.453, -0.188), resolution=(960, 540))
        收到邮件=Template(r"tpl1694441057562.png", record_pos=(-0.31, -0.199), resolution=(960, 540))
        快速领取=Template(r"tpl1694441070767.png", record_pos=(0.385, 0.23), resolution=(960, 540))
        下次吧=Template(r"tpl1694443587766.png", record_pos=(-0.097, 0.118), resolution=(960, 540))
        金币确定=Template(r"tpl1694443607846.png", record_pos=(0.002, 0.167), resolution=(960, 540))
        点击屏幕继续=Template(r"tpl1694487484286.png", record_pos=(-0.006, 0.237), resolution=(960, 540))
        友情确定=Template(r"tpl1694487498294.png", record_pos=(-0.097, 0.24), resolution=(960, 540))
        系统邮件=Template(r"tpl1694441115819.png", record_pos=(-0.446, -0.127), resolution=(960, 540))
        系统快速领取=Template(r"tpl1694451260084.png", record_pos=(0.415, 0.236), resolution=(960, 540))
        解锁语音界面=Template(r"tpl1694441160296.png", record_pos=(-0.01, -0.015), resolution=(960, 540))
        我知道了=Template(r"tpl1694441175302.png", record_pos=(-0.1, 0.116), resolution=(960, 540))
        系统礼物确定=Template(r"tpl1694441190629.png", record_pos=(0.0, 0.165), resolution=(960, 540))
        黄色礼物确定=Template(r"tpl1694441373245.png", record_pos=(-0.002, 0.116), resolution=(960, 540))

        返回=Template(r"tpl1694442171115.png", record_pos=(-0.441, -0.252), resolution=(960, 540))
        self.Tool.existsTHENtouch(邮件图标)
        if not exists(好友邮件):
            if not self.判断大厅中(): self.进入大厅()
            if self.Tool.existsTHENtouch(邮件图标,"邮件图标"):
                sleep(10)
            if not exists(好友邮件): return self.每日礼包_邮件礼包(times)
        #
        if self.Tool.existsTHENtouch(好友邮件):
            self.Tool.existsTHENtouch(收到邮件,"收到邮件",savepos=False)
            self.Tool.existsTHENtouch(快速领取,"快速领取",savepos=False)
            #缺少确定
            self.Tool.LoopTouch(下次吧,"下次吧",loop=10)
            self.Tool.existsTHENtouch(金币确定,"金币确定")
            self.Tool.existsTHENtouch(点击屏幕继续,"点击屏幕继续")
            self.Tool.existsTHENtouch(友情确定,"友情确定")
            #
        if self.Tool.existsTHENtouch(系统邮件):
            self.Tool.existsTHENtouch(系统快速领取,"系统快速领取",savepos=False)
            self.Tool.LoopTouch(黄色礼物确定,"黄色礼物确定",loop=10)
            while self.Tool.existsTHENtouch(系统礼物确定,"系统礼物确定"):
                if exists(解锁语音界面): self.Tool.existsTHENtouch(我知道了,"我知道了")
                self.Tool.LoopTouch(黄色礼物确定,"黄色礼物确定",loop=10)
                if self.Tool.timelimit(timekey="领邮件礼包",limit=60*5,init=False):
                             TimeECHO(self.prefix+"领邮件礼包超时.....")
                             return self.每日礼包_邮件礼包(times)
            self.Tool.LoopTouch(系统礼物确定,"系统礼物确定",loop=10)
        self.Tool.LoopTouch(返回,"返回")
        return True
                                      
        #妲己礼物
    def 每日礼包_妲己礼物(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO(self.prefix+"领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr(self.prefix+"领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        TimeECHO(self.prefix+"领任务礼包:小妲己礼物")

        小妲己=Template(r"tpl1694441259292.png", record_pos=(0.458, 0.21), resolution=(960, 540))
        一键领奖=Template(r"tpl1694442066106.png", record_pos=(-0.134, 0.033), resolution=(960, 540))
        去领取=Template(r"tpl1694442088041.png", record_pos=(-0.135, 0.107), resolution=(960, 540))
        收下=Template(r"tpl1694442103573.png", record_pos=(-0.006, 0.181), resolution=(960, 540))
        确定=Template(r"tpl1694442122665.png", record_pos=(-0.003, 0.165), resolution=(960, 540))
        返回=Template(r"tpl1694442136196.png", record_pos=(-0.445, -0.251), resolution=(960, 540))
        能力测试关闭=Template(r"tpl1699626801240.png", record_pos=(0.34, -0.205), resolution=(960, 540))

        #
        if not self.Tool.existsTHENtouch(小妲己,"小妲己"):
            if not self.判断大厅中(): self.进入大厅()
            if not self.Tool.existsTHENtouch(小妲己,"小妲己"): return self.每日礼包_妲己礼物(times)
        #
        if exists(一键领奖):
            self.Tool.existsTHENtouch(去领取,"去领取")
            self.Tool.LoopTouch(收下,"收下",loop=10)
            self.Tool.LoopTouch(确定,"确定",loop=10)
            self.Tool.LoopTouch(收下,"收下",loop=10)
        self.Tool.existsTHENtouch(能力测试关闭,"能力测试关闭")
        self.Tool.LoopTouch(返回,"返回")
        self.确定按钮()
        return True

#状态判断
    def 判断大厅中(self):
        if exists(self.大厅对战图标): return True
        #
        return False
    def 判断房间中(self):
        #长平之战等满人状态时
        if exists(Template(r"tpl1691463676972.png", record_pos=(0.356, -0.258), resolution=(960, 540))):
            TimeECHO(self.prefix+"正在房间中[文字判断]")
            return True        
        if exists(Template(r"tpl1690442701046.png", record_pos=(0.135, -0.029), resolution=(960, 540))):
            TimeECHO(self.prefix+"正在房间中")
            return True
        else:
            return False
    def 判断对战中(self,处理=False):
        if "模拟战" in self.对战模式:
            return self.判断对战中_模拟战(处理)
        对战=Template(r"tpl1689666416575.png", record_pos=(0.362, 0.2), resolution=(960, 540),threshold=0.9)
        if exists(对战):
            TimeECHO(self.prefix+"正在对战中")
            if 处理:
                self.Tool.timelimit(timekey="endgame",limit=60*30,init=True)
                while self.Tool.existsTHENtouch(对战):
                    if self.Tool.存在同步文件(): return True
                    TimeECHO(self.prefix+"加速对战中")
                    sleep(30) #
                    if self.Tool.timelimit(timekey="endgame",limit=60*30,init=False):
                        TimeErr(self.prefix+"对战中游戏时间过长,重启游戏") #存在对战的时间超过20min,大概率卡死了
                        self.移动端.重启APP(10)
                        self.进入大厅()
                        return False
            return True
        return False
    def 判断对战中_模拟战(self,处理=False):
        正在对战=False
        if exists(Template(r"tpl1690546926096.png", record_pos=(-0.416, -0.076), resolution=(960, 540))):
            TimeECHO(self.prefix+"开始中")
            if not 处理: return True
            sleep(5)
            正在对战=True
        #立信界面

        if exists(Template(r"tpl1690547491681.png", record_pos=(0.471, 0.165), resolution=(960, 540))):
            TimeECHO(self.prefix+"战斗界面")
            if not 处理: return True
            sleep(5)
            正在对战=True

        if exists(Template(r"tpl1690552290188.png", record_pos=(0.158, 0.089), resolution=(960, 540))):
            TimeECHO(self.prefix+"方案界面")
            if not 处理: return True
            sleep(5)
            正在对战=True
        钱袋子=Template(r"tpl1690546610171.png", record_pos=(0.391, 0.216), resolution=(960, 540))
        刷新金币=Template(r"tpl1690547053276.png", record_pos=(0.458, -0.045), resolution=(960, 540))
        关闭钱袋子=Template(r"tpl1690547457483.png", record_pos=(0.392, 0.216), resolution=(960, 540))
        if exists(钱袋子):
            TimeECHO(self.prefix+"钱袋子")
            if not 处理: return True
        if exists(刷新金币):
            TimeECHO(self.prefix+"刷新金币")
            if not 处理: return True
        #
        if not 处理: return 正在对战
        if not 正在对战: return 正在对战
        #
        #
        #下面开始处理对战
        self.Tool.LoopTouch(钱袋子,"钱袋子",loop=10)
        self.Tool.LoopTouch(刷新金币,"刷新金币",loop=10)
        self.Tool.timelimit(timekey="endgame",limit=60*20,init=True)
        while self.判断对战中_模拟战(False):
            TimeECHO(self.prefix+"处理对战中")
            self.Tool.LoopTouch(钱袋子,"钱袋子",loop=10) #点击结束后,应该变成X号
            self.Tool.LoopTouch(刷新金币,"刷新金币",loop=10)
            if not exists(关闭钱袋子) and not exists(钱袋子): return False
            if self.Tool.timelimit(timekey="endgame",limit=60*20,init=False): break
            sleep(10)

        return 正在对战

    def 健康系统(self):
        if exists(Template(r"tpl1689666921933.png", record_pos=(0.122, -0.104), resolution=(960, 540))):
            TimeECHO(self.prefix+"您已禁赛")
            if self.组队模式: self.Tool.touch同步文件()
            return True
        return False

#开始运行
    def 进行人机匹配对战循环(self):
        #初始化
        self.移动端.打开APP()
        if self.房主:TimeECHO("->"*10)
        if self.Tool.存在同步文件(): return True
        if not self.判断房间中():
            self.进入大厅()
            self.单人进入人机匹配房间()
        if self.Tool.存在同步文件(): return True
        #进入房间
        self.进入人机匹配房间()
        if self.Tool.存在同步文件(): return True
        #进行对战
        self.进行人机匹配()
        if self.Tool.存在同步文件(): return True
        加速对战=False
        if self.debug : 加速对战=True
        while self.判断对战中_模拟战(加速对战):
            TimeECHO(self.prefix+"处理对战中")
            if self.Tool.存在同步文件(): return True
        #结束对战
        self.结束人机匹配()
        self.Tool.barriernode(self.mynode,self.totalnode,"结束对战")
        #
        if self.Tool.存在同步文件(): return True
        #
        if self.mynode == 0: self.Tool.clean文件()
        if self.房主: TimeECHO("<-"*10)
        #
    def RUN(self):#程序入口
        runstep=0
        对战次数=0
        self.移动端.打开APP()
        #self.每日礼包()
        while True:
            if self.Tool.存在同步文件():#单进程各种原因出错时,多进程无法同步时
                TimeECHO(self.prefix+"存在同步文件,需要同步程序")
                if not self.移动端.device: self.移动端.连接设备()
                self.移动端.关闭APP()
                if not self.Tool.同步等待(self.mynode,self.totalnode,sleeptime=60*5): #后面出现健康系统警告也会直接回来的
                   continue
            #运行前统一冰行变凉
            runstep=runstep+1
            self.runinfo["runstep"]=runstep
            self.runinfo=self.Tool.bcastvar(self.mynode,self.totalnode,var=self.runinfo,name="bcastruninfo")
            runstep=self.runinfo["runstep"]
            TimeECHO(self.prefix+f".运行次数{runstep}")
            #
            #运行时间检测
            startclock=5;endclock=12 #服务器5点刷新礼包和信誉积分等
            if runstep==0: startclock=-1;endclock=25
            hour,minu=self.Tool.time_getHM()
            while hour >= endclock or hour < startclock:
                TimeECHO(self.prefix+"夜间停止刷游戏")
                self.每日礼包()
                #计算休息时间
                hour,minu=self.Tool.time_getHM()
                leftmin=max((startclock-hour)*60-minu,0)
                if self.移动端.容器优化:leftmin=leftmin+self.mynode*1#这里的单位是分钟,每个node别差别太大
                TimeECHO(self.prefix+"预计等待%d min ~ %3.2f h"%(leftmin,leftmin/60.0))
                if self.debug: leftmin=0.5
                self.移动端.重启APP(leftmin*60)
                if self.debug: break
                sleep(mynode*10)
                hour,minu=self.Tool.time_getHM()
            #
            if self.Tool.存在同步文件(): continue
            self.Tool.barriernode(self.mynode,self.totalnode,"准备进入战斗循环")
            #
            #礼包
            if runstep%10 == 0:
                self.每日礼包()
            #
            if self.Tool.存在同步文件(): continue
            self.移动端.打开APP()
            #
            #开始辅助同步,然后开始游戏
            self.进行人机匹配对战循环()
            if self.Tool.存在同步文件(): continue
            #
            if self.移动端.实体终端 and self.debug: 
                TimeECHO(self.prefix+":实体终端,休息设备")
                self.移动端.关闭APP()
                sleep(60*0.5)
        


class auto_airtest:
    def __init__(self, mynode=0, totalnode=1,设备类型="IOS"):
        self.mynode=mynode
        self.totalnode=totalnode
        self.设备类型=设备类型.lower()
        self.prefix=f"({self.mynode}/{self.totalnode})"
        self.debug=True
        #设备信息
        LINK_dict={}
        if "android" in self.设备类型:
            LINK_dict[0]="Android:///"+"127.0.0.1:"+str( 5555 )
            LINK_dict[1]="Android:///"+"127.0.0.1:"+str( 5565 )
            LINK_dict[2]="Android:///"+"127.0.0.1:"+str( 5575 )
            LINK_dict[3]="Android:///"+"127.0.0.1:"+str( 5555 )
            LINK_dict[4]="Android:///"+"127.0.0.1:"+str( 5555 )
        else:
            LINK_dict[0]="ios:///http://"+"192.168.12.130:8100"
            LINK_dict[1]="ios:///http://"+"192.168.12.130:8100"
            LINK_dict[2]="ios:///http://"+"192.168.12.130:8100"
            LINK_dict[3]="ios:///http://"+"192.168.12.130:8100"
            LINK_dict[4]="ios:///http://"+"192.168.12.130:8100"
        if self.debug:
            #当在这里手动指定Link时,自动进行修正
            LINK_dict[0]="Android:///"+"192.168.192.10:5555"
            LINK_dict[1]="Android:///"+"192.168.192.10:5565"
            #LINK_dict[totalnode-1]="ios:///http://169.254.148.222:8100"
        #if "ios" in LINK_dict[0]: os.system("tidevice wdaproxy -B  com.cndaqiang.WebDriverAgentRunner.xctrunner > tidevice.result.txt 2>&1 &")
        #
        self.LINK=LINK_dict[mynode]
        self.设备类型=self.LINK.split(":")[0].lower()
        self.APPID="com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.printINFO()
        self.移动端=deviceOB(设备类型=self.设备类型,mynode=self.mynode,totalnode=self.totalnode,LINK=self.LINK,APPID=self.APPID)
        if not self.移动端.device:
            TimeErr(self.prefix+f"{self.prefix}:连接设备失败,退出")
            return
        #
        对战模式="模拟战" if "moni" in __file__ else "5v5匹配"
        TASK=wzry_task(self.移动端,对战模式,shiftnode=-1,debug=self.debug)
        TASK.RUN()
        #
    def printINFO(self):
        TimeECHO(self.prefix+f"{self.prefix}:LINK={self.LINK}")
        TimeECHO(self.prefix+f"{self.prefix}:设备类型={self.设备类型}")
        TimeECHO(self.prefix+f"{self.prefix}:mynode={self.mynode}")
        TimeECHO(self.prefix+f"{self.prefix}:totalnode={self.totalnode}")
        TimeECHO(self.prefix+f"{self.prefix}:APPID={self.APPID}")

#@todo
#给ios设备添加休息冷却的时间
#
# 如果文件被直接执行，则执行以下代码块
if __name__ == "__main__":
    multi_run=False
    设备类型="android"
    #设备类型="ios"
    if len(sys.argv) <= 1:  #直接跑
        mynode=0;totalnode=1
    elif len(sys.argv) <= 2:  #直接跑,或者指定node跑
        try:
            para2=int(sys.argv[1])
        except:
            para2=1
        mynode=0;totalnode=abs(para2)
        multi_run = para2 < 0
    else:#组队模式,但是自己单进程跑
        mynode=int(sys.argv[1])
        totalnode=int(sys.argv[2])
    if not multi_run:
        auto_airtest(mynode,totalnode,设备类型)
    else:
        def multi_start(i):
            auto_airtest(i,totalnode,设备类型)
        from pathos import multiprocessing
        m_process=totalnode
        #barrier=multiprocessing.Barrier(totalnode)
        m_cpu = [i for i in range(0, m_process)]
        if __name__ == '__main__':
            p = multiprocessing.Pool(m_process)
            out = p.map_async(multi_start,m_cpu).get()
            p.close()
            p.join()


    



















