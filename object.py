# -*- encoding=utf8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2023-11-10            #
# Build  : 2023-11-10            #
# What   : IOS/Android 自动化任务  #
#################################

import sys,os
from airtest.core.api import start_app,stop_app,Template,connect_device,touch,exists,sleep
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
def TimeECHO(*args):
    # 获取当前日期和时间
    current_datetime = datetime.now(eastern_eight_tz)
    # 格式化为字符串（月、日、小时、分钟、秒）
    formatted_string = current_datetime.strftime("[%m-%d %H:%M:%S]")
    modified_args = (formatted_string + str(args[0]),) + args[1:]
    print(*modified_args)
    #如果airtest客户端报错,python命令行不报错.就制定airtest的oython路径为anaconda的python

def TimeErr(info="None"):
    TimeECHO("NNNN:"+info)
#
class DQWheel:
    def __init__(self, var_dict_file='var_dict_file.txt',容器优化=False):
        self.timedict={}
        self.容器优化=容器优化
        self.辅助同步文件="NeedRebarrier.txt"
        self.barrierlimit=60*20 #同步最大时长
        self.filelist=[] #建立的所有文件，用于后期clear
        self.var_dict_file=var_dict_file
        self.var_dict=self.read_dict(self.var_dict_file)
        self.savepos=True
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
        try:
            os.remove(filename)
            TimeECHO("删除["+filename+"]成功") 
            return True    
        except:
            TimeECHO("删除["+filename+"]失败")     
            return False
    def touchfile(self,filename):
        try:
            f=open(filename,'w')
            TimeECHO("touch["+filename+"]成功")     
        except:
            TimeECHO("touch["+filename+"]失败") 
    #
    def touch同步文件(self):
        touch(self.辅助同步文件)
    def 存在同步文件(self):
        return os.path.exists(self.辅助同步文件)
    #
    def barriernode(self,mynode,totalnode,name="barrierFile"):
        if totalnode < 2: return True
        if os.path.exists(self.辅助同步文件): return True
        filelist=[]
        ionode= mynode == 0 or totalnode == 1
        for i in np.arange(1,totalnode):
            filename=f".tmp.barrier.{i}.{name}.txt"
            if ionode: self.touchfile(filename)
            filelist.append(filename)
            self.filelist.append(filename)
        #
        print(filelist)
        self.timelimit(timekey=name,limit=self.barrierlimit,init=True)
        while not self.timelimit(timekey=name,limit=self.barrierlimit,init=False):
            if ionode:
                barrieryes=True
                for i in filelist:
                    barrieryes= barrieryes and not os.path.exists(i)
                if barrieryes:
                    TimeECHO("+++++MASTER:同步完成"+name)
                    return True
            else:
                if self.removefile(filelist[mynode-1]):
                    return True
            sleep(5)
        self.touchfile(self.辅助同步文件)
        if ionode:
            for i in filelist: self.removefile(i)
            TimeErr("同步失败")
        return False
    #读取变量
    def read_dict(self,var_dict_file="position_dict.txt"):
        global 辅助
        #if 辅助: return {}
        import pickle
        var_dict={}
        if os.path.exists(var_dict_file):
            TimeECHO("读取"+var_dict_file)
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
                TimeECHO("touch (saved) "+keystr)
                sleep(0.1)
                return True
        pos=exists(png)
        if pos:
            touch(pos)
            if len(keystr) > 0: TimeECHO("touch "+keystr)
            if savepos:
                self.var_dict[keystr]=pos
                self.save_dict(self.var_dict,self.var_dict_file)
            return True
        else:
            if len(keystr) > 0:
                TimeECHO("NotFound "+keystr)
            return False

    #
    #touch的总时长timelimit s, 或者总循环次数<10
    def LoopTouch(self,png=Template(r"1.png"),keystr="",limit=0,loop=10,savepos=False):
        timekey="LOOPTOUCH"+keystr+str(random.randint(1, 500))
        if limit + loop < 0.5: limit=0;loop=1
        self.timelimit(timekey=timekey,limit=limit,init=True)
        runloop=1
        while self.existsTHENtouch(png=png,keystr=keystr,savepos=savepos):
            if limit > 0:
                if self.timelimit(timekey=timekey,limit=limit,init=False):
                    TimeErr("TOUCH"+keystr+"超时.....")
                    break
            if runloop > loop:
                TimeErr("TOUCH"+keystr+"超LOOP.....")
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
        #
        prefix=f"{(mynode/totalnode)}"
        同步初始化=True
        while True:
            #
            if not os.path.exists(同步文件): return True
            #
            #创建同步文件
            if 同步初始化:
                TimeECHO(prefix+f"监测到{同步文件},开始同步,sleep {sleeptime}s")
                self.touchfile(f"{mynode}."+同步文件)
                sleep(sleeptime)
                self.removefile(f"{mynode}."+同步文件)
                同步初始化=False
                continue
            else:
                TimeECHO(prefix+f"休息结束,检测其他节点是否休息结束")
                同步未结束=True
                for totalnode_i in range(totalnode):
                    辅助同步file_=f"{totalnode_i}."+同步文件
                    if os.path.exists(辅助同步file_):
                        同步未结束 = True
                        TimeECHO(prefix+f"监测到{辅助同步file_},继续休息")
                        break
                if 同步未结束:
                    sleep(60)
                    continue
                else:
                    self.removefile(同步文件)
                    TimeECHO(prefix+"所有节点休息结束")
                    return True
    def time_getHM(self):
        current_time=datetime.now(eastern_eight_tz)
        hour=current_time.hour
        minu=current_time.minute
        return hour,minu
    



    #旧脚本,适合几个程序,自动商量node编号
    def autonode(self,totalnode):
        if totalnode < 2: return 0
        node=-10
        PID=os.getpid()
        filename="init_node."+str(totalnode)+"."+str(PID)+".txt"
        self.touchfile(filename)
        TimeECHO("自动生成node中:"+filename)
        PID_dict={}
        for i in np.arange(60):
            for name in os.listdir("."):
                if "init_node."+str(totalnode)+"." in name:
                    PID_dict[name]=name
            if len(PID_dict) == totalnode: break
            sleep(5)
        if len(PID_dict) != totalnode:
            self.removefile(filename)
            TimeECHO("文件数目不匹配")
            return node
        #
        strname=np.array(list(PID_dict.keys()))
        PIDarr=np.zeros(strname.size)
        for i in np.arange(PIDarr.size):
            PIDarr[i]=int(strname[i].split(".")[2])
        PIDarr=np.sort(PIDarr)
        for i in np.arange(PIDarr.size):
            logger.warning("i="+str(i)+". PID="+str(PID)+". PIDarr[i]="+str(PIDarr[i]))
            if PID == PIDarr[i]: node=i

        if node < 0:
            logger.warning("node < 0")
            self.removefile(filename)
            return node
        #
        logger.warning("mynode:"+str(node))
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
        self.totalnode=totalnode
        self.PID=-10 #Windows+Blustack专用,关闭特定虚拟机
        #
        self.连接设备()
        #APPID
        self.APPID="com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.APPID=APPID if APPID else self.APPID
        start_app(self.APPID)
        #
        self.容器优化=False


    #尝试连接timesMax次,当前是times次
    def 连接设备(self,times=1,timesMax=2):
        TimeECHO(f"开始第{times}次连接:{self.LINK}")
        self.device=connect_device(self.LINK)
        if self.device:
            TimeECHO(f"({self.LINK})链接成功")
            return True
        elif times <= timesMax:
            TimeECHO(f"({self.LINK})链接失败,重启设备再次连接")
            self.启动设备()
            return self.连接设备(times+1,timesMax)
        else:
            TimeErr(f"({self.LINK})链接失败,无法继续")
            return False
    def 启动设备(self):
        if "ios" in self.设备类型:
            TimeECHO(f"({self.mynode})IOS暂不支持重启")
            sleep(10)
            return True
        #android
        try:
            if "mac" in self.控制端:
                TimeECHO(f"({self.mynode})MAC暂不支持设备管理")
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
                TimeECHO(f"({self.mynode})启动成功")
                return True
            else:
                TimeErr(f"({self.mynode})启动失败")
                return False
        except:
                TimeErr(f"({self.mynode})启动失败")
                return False
    def 关闭设备(self):
        if "ios" in self.设备类型:
            TimeECHO(f"({self.mynode})IOS暂不支持关闭")
            sleep(10)
            return True
        #android
        try:
            if "mac" in self.控制端:
                TimeECHO(f"({self.mynode})MAC暂不支持设备管理")
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
                TimeECHO(f"({self.mynode})启动成功")
                return True
            else:
                TimeECHO(f"({self.mynode})启动失败")
                return False
        except:
                TimeErr(f"({self.mynode})启动失败")
                return False
    #
    def 重启设备(self,sleeptime=0):
        TimeECHO(f"重新启动{self.LINK}")
        self.关闭设备()
        sleeptime=max(10,sleeptime-60)
        printtime=max(30,sleeptime/10)
        TimeECHO("sleep %d min"%(sleeptime/60))
        for i in np.arange(int(sleeptime/printtime)):
            TimeECHO(f"({self.mynode})...taskkill_sleep: {i}",end='\r')
            sleep(printtime)
        self.启动设备()
        self.连接设备()
    #
    def 关闭APP(self):
        TimeECHO(f"({self.mynode})关闭APP中")
        stop_app(self.APPID)
    def 打开APP(self):
        TimeECHO(f"({self.mynode})打开APP中")
        start_app(self.APPID)
        sleep(20)

    def 重启APP(self,sleeptime=0):
        TimeECHO(f"({self.mynode})重启APP中")
        try:
            self.关闭APP()
            TimeECHO(f"({self.mynode})关闭程序")
        except:
            TimeErr(f"({self.mynode})关闭程序失败")
        sleep(10)
        sleeptime=max(10,sleeptime)
        printtime=max(30,sleeptime/10)
        if sleeptime > 60*60: #>1h
            self.重启设备(sleeptime)
        else:
            print("sleep %d min"%(sleeptime/60))
            for i in np.arange(int(sleeptime/printtime)):
                TimeECHO(f"({self.mynode})...taskkill_sleep: {i}",end='\r')
                sleep(printtime)
        TimeECHO(f"({self.mynode})打开程序")
        self.打开APP()
        TimeECHO(f"({self.mynode})打开程序成功")
        sleep(60*2)
        return True







class wzrj_task:
    def __init__(self,移动端,对战模式,shiftnode=0):
        self.移动端=移动端
        self.mynode=self.移动端.mynode
        self.totalnode=self.移动端.totalnode
        self.组队模式=self.totalnode > 1
        self.房主=self.mynode == 0 or self.totalnode == 1
        self.对战时间=[5,24] #单位hour
        self.对战结束返回房间=True
        self.结束游戏FILE="WZRY.ENDGAME.txt"
        self.对战模式=对战模式 #"5v5匹配" or "王者模拟战"
        self.prefix=f"({self.mynode})"
        self.Tool=DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.mynode}.txt",容器优化=False)
        self.Tool.barriernode(self.mynode,self.totalnode,"WZRYinit")
        self.Tool.removefile(self.结束游戏FILE)
        self.Tool.容器优化=self.移动端.容器优化
        self.选择人机模式=True
        self.选择英雄=True
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

    def 进入大厅(self,times=1):
        TimeECHO(self.prefix+"尝试进入大厅")
        if self.判断大厅中():
            return True
        self.Tool.timelimit(timekey="结束对战",limit=60*10)
        while self.判断对战中():
            TimeECHO(self.prefix+"尝试进入大厅:对战sleep")
            sleep(30)
            if self.Tool.timelimit(timekey="结束对战",limit=60*10,init=False): break
        #
        self.登录游戏()
        #返回图标
        返回图标=Template(r"tpl1692949580380.png", record_pos=(-0.458, -0.25), resolution=(960, 540),threshold=0.9)
        self.Tool.LoopTouch(返回图标,"返回图标",loop=10,savepos=False)
        if exists(Template(r"tpl1693886922690.png", record_pos=(-0.005, 0.114), resolution=(960, 540))):
            self.Tool.existsTHENtouch(Template(r"tpl1693886962076.png", record_pos=(0.097, 0.115), resolution=(960, 540)))
        if self.判断大厅中():return True
        #
        #邀请
        if exists(Template(r"tpl1692951548745.png", record_pos=(0.005, 0.084), resolution=(960, 540))):
            关闭邀请=Template(r"tpl1692951558377.png", record_pos=(0.253, -0.147), resolution=(960, 540),threshold=0.9)
            self.Tool.LoopTouch(关闭邀请,"关闭邀请",loop=5,savepos=False)
        if self.判断大厅中():return True
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
                self.Tool.touch同步文件()
                return True
            else:
               self.移动端.关闭APP()
               return False

    def 登录游戏(self):
        #现在打开可能会放一段视频，怎么跳过呢？
        开始游戏=Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540),threshold=0.9)
        if self.Tool.existsTHENtouch(开始游戏,"登录界面.开始游戏",savepos=False):
            sleep(10)
        #动态下载资源提示
        回归礼物=Template(r"tpl1699607355777.png")
        if exists(回归礼物):
            self.Tool.existsTHENtouch(Template(r"tpl1699607371836.png"))
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
            self.Tool.LoopTouch(i,f"活动关闭集合{i}",loop=5,savepos=False)
            if self.判断大厅中(): return True
        #
        while exists(今日不再弹出):#当活动海报太大时，容易识别关闭图标错误，此时采用历史的关闭图标位置
            TimeECHO("今日不再弹出仍在")
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
            TimeErr("找不到大厅对战图标")
            return self.单人进入人机匹配房间(times)
        #
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666019941.png", record_pos=(-0.401, 0.098), resolution=(960, 540)),"5v5王者峡谷",savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        if not self.Tool.existsTHENtouch(Template(r"tpl1689666034409.png", record_pos=(0.056, 0.087), resolution=(960, 540)),"人机",savepos=False):
            return self.单人进入人机匹配房间(times)
        sleep(2)
        if self.选择人机模式:
            TimeECHO("选择对战模式")
            if not self.Tool.existsTHENtouch(Template(r"tpl1689666057241.png", record_pos=(-0.308, -0.024), resolution=(960, 540)),"快速模式"):
                return self.单人进入人机匹配房间(times)
            #if not self.Tool.existsTHENtouch(Template(r"tpl1689666069306.png"),"标准模式"):
                return 进入匹配房间(times)
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
        重新进房file="辅助模式进房间.txt"
        self.Tool.removefile(重新进房file)
        self.Tool.barriernode(self.mynode,self.totalnode,"组队进房间")
        self.Tool.timelimit(timekey=f"组队模式进房间{self.mynode}",limit=60*5,init=True)
        while True:
            if self.Tool.timelimit(timekey=f"组队模式进房间{self.mynode}",limit=60*17,init=False):
                self.Tool.touch同步文件()
            if self.Tool.存在同步文件(): return True
            #
            取消准备=Template(r"tpl1699179402893.png", record_pos=(0.098, 0.233), resolution=(960, 540),threshold=0.9)
            if not self.房主:
                self.Tool.timelimit(timekey=f"辅助进房{self.mynode}",limit=60*5,init=True)
                while not exists(取消准备):
                    if self.Tool.timelimit(timekey=f"辅助进房{self.mynode}",limit=60*5,init=False): break
                    if self.Tool.存在同步文件(): return True
                    if os.path.exists(重新进房file): break
                    #
                    #需要小号和主号建立亲密关系，并在主号中设置亲密关系自动进入房间
                    TimeECHO(self.prefix+"不在房间中")
                    self.单人进入人机匹配房间()
                    进房=Template(r"tpl1699181922986.png", record_pos=(0.46, -0.15), resolution=(960, 540),threshold=0.9)
                    进房间=Template(r"tpl1699181937521.png", record_pos=(0.348, -0.194), resolution=(960, 540),threshold=0.9)
                    if self.Tool.existsTHENtouch(进房):
                        TimeECHO(self.prefix+"找到房间")
                        if self.Tool.existsTHENtouch(进房间):
                            TimeECHO(self.prefix+"尝试进入房间中")
                    #
                if not exists(取消准备):
                    self.Tool.touchfile(重新进房file)
            #
            if self.Tool.存在同步文件(): return True
            if not self.Tool.barriernode(self.mynode,self.totalnode,"结束组队进房间"): 
                self.Tool.touch同步文件()
            #
            if os.path.exists(重新进房file):
                TimeErr(self.prefix+"进入房间失败,...重启虚拟机中")
                self.移动端.重启APP(mynode*30)
            #
            if self.判断房间中() and not exists(取消准备):
                return True

    def 进行人机匹配(self,times=1):
        if self.Tool.存在同步文件(): return True
        if times == 1:
            self.Tool.timelimit(timekey="进行人机匹配",limit=60*10,init=True)
        times=times+1
        if not self.判断房间中():
            self.Tool.touch同步文件()
            TimeErr(self.prefix+":不在房间中,无法点击匹配按钮")
        #
        self.Tool.timelimit(timekey="确认匹配",limit=60*1,init=True)
        self.Tool.timelimit(timekey="超时确认匹配",limit=60*5,init=True)
        #
        while True:
            房间中的开始按钮=Template(r"tpl1689666117573.png", record_pos=(0.096, 0.232), resolution=(960, 540))
            if self.房主:
                if self.判断房间中(): self.Tool.existsTHENtouch(房间中的开始按钮,"开始匹配按钮")
            else:
                TimeErr(self.prefix+":不在房间中,无法点击匹配按钮")
            if self.Tool.timelimit(timekey="确认匹配",limit=60*1,init=False): TimeErr("超时,队友未确认匹配或大概率程序卡死")
            if self.Tool.timelimit(timekey="超时确认匹配",limit=60*5,init=False): 
                TimeErr("超时太久,退出匹配")
                return False
            自己确定匹配 = self.Tool.existsTHENtouch(Template(r"tpl1689666290543.png", record_pos=(-0.001, 0.152), resolution=(960, 540),threshold=0.8),"确定匹配按钮")
            队友确认匹配 = exists(Template(r"tpl1689666311144.png", record_pos=(-0.394, -0.257), resolution=(960, 540),threshold=0.9))
            if 队友确认匹配: break
            sleep(2)
        #选择英雄
        if self.选择英雄 and self.Tool.existsTHENtouch(Template(r"tpl1689666324375.png", record_pos=(-0.297, -0.022), resolution=(960, 540)),"展开英雄",savepos=False):
            sleep(1)
            self.Tool.existsTHENtouch(self.参战英雄线路,"参战英雄线路",savepos=True)
            sleep(5)
            self.Tool.existsTHENtouch(self.参战英雄头像,"参战英雄头像",savepos=True)
            sleep(1)
            #分路重复.png
            if exists(Template(r"tpl1689668119154.png", record_pos=(0.0, -0.156), resolution=(960, 540))):
                logger.warning("分路冲突，切换英雄")
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
                logger.warning("加载游戏中.....")
                self.Tool.existsTHENtouch(Template(r"tpl1689666367752.png", record_pos=(0.42, -0.001), resolution=(960, 540)),"加油按钮",savepos=False)
                sleep(10)
                if self.Tool.容器优化: sleep(30) #貌似容器容易开在这个界面ß
                if not exists(加载游戏界面): break
            if self.Tool.timelimit(timekey="加载游戏",limit=60*10,init=False):
                if self.Tool.容器优化: break
                logger.warning("加载时间过长.....重启APP")
                self.移动端.重启APP(10)
                return False
            sleep(10)

    def 结束人机匹配(self):
        if self.Tool.存在同步文件(): return True
        self.Tool.timelimit(timekey="结束人机匹配",limit=60*10,init=True)
        jixu=False
        while True:
            if self.Tool.存在同步文件(): return True
            if self.Tool.timelimit(timekey="结束人机匹配",limit=60*10,init=False):
                self.Tool.touch同步文件()
                TimeErr("结束人机匹配时间超时")
                return self.进入大厅()
            if self.健康系统() or self.判断大厅中():
                TimeErr("结束人机匹配:健康系统or处在大厅")
                return True
            if self.判断房间中(): return
            #
            游戏结束了=Template(r"tpl1694360304332.png", record_pos=(-0.011, -0.011), resolution=(960, 540))
            if exists(游戏结束了):
                self.Tool.existsTHENtouch(Template(r"tpl1694360310806.png", record_pos=(-0.001, 0.117), resolution=(960, 540)))

            #有时候会莫名进入分享界面
            if exists(Template(r"tpl1689667038979.png", record_pos=(0.235, -0.125), resolution=(960, 540))):
                TimeECHO("分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png"))
                jixu=True
                sleep(2)

            #有时候会莫名进入MVP分享界面
            pos=exists(Template(r"tpl1689727624208.png", record_pos=(0.235, -0.125), resolution=(960, 540)))
            if pos:
                TimeECHO("mvp分享界面")
                self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540)))
                jixu=True
                sleep(2)
            #
            #都尝试一次返回
            if self.Tool.existsTHENtouch(Template(r"tpl1689667050980.png", record_pos=(-0.443, -0.251), resolution=(960, 540))):
                sleep(2)

            if self.Tool.existsTHENtouch(Template(r"tpl1689667161679.png", record_pos=(-0.001, 0.226), resolution=(960, 540))):
                TimeECHO("MVP继续")
                jixu=True
                sleep(2)

            #胜利页面继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689668968217.png", record_pos=(0.002, 0.226), resolution=(960, 540))):                        
                TimeECHO("继续1/3")
                jixu=True
                sleep(2)
            #显示mvp继续
            if self.Tool.existsTHENtouch(Template(r"tpl1689669015851.png", record_pos=(-0.002, 0.225), resolution=(960, 540))):
                TimeECHO("继续2/3")
                jixu=True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1689669071283.png", record_pos=(-0.001, -0.036), resolution=(960, 540))):
                TimeECHO("友情积分继续2/3")
                jixu=True
                self.Tool.existsTHENtouch(Template(r"tpl1689669113076.png", record_pos=(-0.002, 0.179), resolution=(960, 540)))
                sleep(2)

            #todo, 暂时为空
            if self.Tool.existsTHENtouch(Template(r"tpl1689670032299.png", record_pos=(-0.098, 0.217), resolution=(960, 540))):
                TimeECHO("超神继续3/3")
                jixu=True
                sleep(2)
            if self.Tool.existsTHENtouch(Template(r"tpl1692955597109.png", record_pos=(-0.095, 0.113), resolution=(960, 540))):
                TimeECHO("网络卡顿提示")
                jixu=True
                sleep(2)         
            #
            sleep(10)  
            if not jixu:
                TimeECHO("未监测到继续,sleep...")
                continue
            # 返回大厅
            # 因为不能保证返回辅助账户返回房间，所以返回大厅更稳妥
            if self.对战结束返回房间:
                if self.Tool.existsTHENtouch(Template(r"tpl1689667226045.png", record_pos=(0.079, 0.226), resolution=(960, 540),threshold=0.9),"返回房间"):
                    sleep(10)
                if self.判断房间中(): return
            else:
                if self.Tool.existsTHENtouch(Template(r"tpl1689667243845.png", record_pos=(-0.082, 0.221), resolution=(960, 540),threshold=0.9),"返回大厅"):
                    sleep(10)
                    if self.Tool.existsTHENtouch(Template(r"tpl1689667256973.png", record_pos=(0.094, 0.115), resolution=(960, 540)),"确定返回大厅"):
                        sleep(10)
                if self.判断大厅中(): return            

    #
    def 每日礼包(self):
        self.每日礼包_每日任务()
        self.每日礼包_邮件礼包()
        self.每日礼包_妲己礼物()

    def 每日礼包_每日任务(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO("领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr("领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        #
        #每日任务
        TimeECHO("领任务礼包:每日任务")
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
        self.Tool.LoopTouch(返回)
        return True
        #
        #邮件礼包
    def 每日礼包_邮件礼包(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO("领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr("领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        TimeECHO("领任务礼包:领邮件礼包")
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
                             logger.warning("领邮件礼包超时.....")
                             return self.每日礼包_邮件礼包(times)
            self.Tool.LoopTouch(系统礼物确定,"系统礼物确定",loop=10)
        self.Tool.LoopTouch(返回)
        return True
                                      
        #妲己礼物
    def 每日礼包_妲己礼物(self,times=1):
        if self.Tool.存在同步文件(): return True
        TimeECHO("领任务礼包")
        #
        if times == 1:
            self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=True)
        else:
            if self.Tool.timelimit(timekey="领任务礼包",limit=60*5,init=False):
                TimeErr("领任务礼包超时")
                return False
        if times > 10: return False
        #
        times=times+1
        self.进入大厅()
        TimeECHO("领任务礼包:小妲己礼物")

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
        return True

#状态判断
    def 判断大厅中(self):
        if exists(self.大厅对战图标): return True
        #
        return False
    def 判断房间中(self):
        #长平之战等满人状态时
        if exists(Template(r"tpl1691463676972.png", record_pos=(0.356, -0.258), resolution=(960, 540))):
            logger.warning("正在房间中[文字判断]")
            return True        
        if exists(Template(r"tpl1690442701046.png", record_pos=(0.135, -0.029), resolution=(960, 540))):
            logger.warning("正在房间中")
            return True
        else:
            return False
    def 判断对战中(self,处理=False):
        对战=Template(r"tpl1689666416575.png", record_pos=(0.362, 0.2), resolution=(960, 540),threshold=0.9)
        if exists(对战):
            TimeECHO("正在对战中")
            if 处理:
                self.Tool.timelimit(timekey="endgame",limit=60*30,init=True)
                while self.Tool.existsTHENtouch(对战):
                    TimeECHO("加速对战中")
                    sleep(10) #
                    if self.Tool.timelimit(timekey="endgame",limit=60*30,init=False):
                        TimeErr("对战中游戏时间过长,重启游戏") #存在对战的时间超过20min,大概率卡死了
                        self.移动端.重启APP(10)
                        self.进入大厅()
                        return False
            return True
        return False

    def 健康系统(self):
        if exists(Template(r"tpl1689666921933.png", record_pos=(0.122, -0.104), resolution=(960, 540))):
            logger.warning("您已禁赛")
            if self.组队模式: self.Tool.touch同步文件()
            return True
        return False

#开始运行
    def 进行人机匹配对战循环(self):
        #初始化
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
        #结束对战
        self.结束人机匹配()
        if self.Tool.存在同步文件(): return True
        #
    def RUN(self):#程序入口
        runstep=0
        对战次数=0
        self.移动端.打开APP()
        #self.每日礼包()
        while True:
            if self.Tool.存在同步文件():
                TimeECHO(self.prefix+"存在同步文件,需要同步程序")
                self.移动端.关闭APP()
                self.Tool.同步等待(sleeptime=60)
            #运行前统一冰行变凉
            runstep=runstep+1
            self.runinfo["runstep"]=runstep
            self.runinfo=self.Tool.bcastvar(self.mynode,self.totalnode,var=self.runinfo,name="bcastruninfo")
            runstep=self.runinfo["runstep"]
            TimeECHO(self.prefix+f".运行次数{runstep}")
            #
            #运行时间检测
            startclock=5;endclock=24 #服务器5点刷新礼包和信誉积分等
            if runstep==0: startclock=-1;endclock=25
            hour,minu=self.Tool.time_getHM()
            while hour >= endclock or hour < startclock:
                TimeECHO(self.prefix+"夜间停止刷游戏")
                self.每日礼包()
                #计算休息时间
                hour,minu=self.Tool.time_getHM()
                leftmin=max((startclock-hour)*60-minu,0)
                if self.移动端.容器优化():leftmin=leftmin+self.mynode*30
                TimeECHO(self.prefix+"预计等待%d min ~ %3.2f h"%(leftmin,leftmin/60.0))
                self.移动端.重启APP(leftmin*60)
                sleep(mynode*10)
                hour,minu=self.Tool.time_getHM()
            #
            self.Tool.barriernode(self.mynode,self.totalnode,"准备进入战斗循环")
            #
            #礼包
            if runstep%10 == 0:
                self.每日礼包()
            #
            self.移动端.打开APP()
            #
            #开始辅助同步,然后开始游戏
            if "5v5" in self.对战模式:
                self.进行人机匹配对战循环()
            #break
        self.移动端.关闭APP()
        return
            



        


class auto_airtest:
    def __init__(self, mynode=0, totalnode=1,设备类型="IOS"):
        self.mynode=mynode
        self.totalnode=totalnode
        self.设备类型=设备类型.lower()
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
        #当在这里手动指定Link时,自动进行修正
        LINK_dict[0]="Android:///"+"192.168.192.10:5555"
        LINK_dict[1]="Android:///"+"192.168.192.10:5565"
        #LINK_dict[0]="ios:///http://169.254.148.222:8100"
        #
        self.LINK=LINK_dict[mynode]
        self.设备类型=self.LINK.split(":")[0].lower()
        self.APPID="com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.tmgp.sgame"
        self.printINFO()
        self.移动端=deviceOB(设备类型=self.设备类型,mynode=self.mynode,totalnode=self.totalnode,LINK=self.LINK,APPID=self.APPID)
        TASK=wzrj_task(self.移动端,"5v5匹配",0)
        TASK.RUN()
    def printINFO(self):
        TimeECHO(f"LINK={self.LINK}")
        TimeECHO(f"设备类型={self.设备类型}")
        TimeECHO(f"mynode={self.mynode}")
        TimeECHO(f"totalnode={self.totalnode}")
        TimeECHO(f"APPID={self.APPID}")


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


    
        




























