#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2024-07-28            #
# Build  : 2024-07-28            #
# What   : 王者营地的礼包         #
##################################

from airtest_mobileauto.control import *


class wzyd_libao:
    def __init__(self, 设备类型="android", Tool=None, 初始化检查=False):
        # 默认只创建对象, 开启初始化检查才会检查
        self.体验币成功 = False
        self.营地活动 = True
        self.设备类型 = 设备类型
        self.prefix = "王者营地"+f".{Settings.mynode}"
        self.营地初始化FILE = self.prefix+f".初始化.txt"
        self.营地需要登录FILE = self.prefix+f".需要登录.txt"
        self.Tool = DQWheel(var_dict_file=f"{self.设备类型}.var_dict_{self.prefix}.txt") if Tool == None else Tool
        self.APPID = "com.tencent.smoba" if "ios" in self.设备类型 else "com.tencent.gamehelper.smoba"
        self.APPOB = appOB(APPID=self.APPID)
        self.IOS = "ios" in self.设备类型
        #
        # 这两个图标会根据活动变化,可以用下面的注入替换
        self.个人界面图标 = Template(r"tpl1699872206513.png", record_pos=(0.376, 0.724), resolution=(540, 960))
        self.游戏界面图标 = Template(r"tpl1704381547456.png", record_pos=(0.187, 0.726), resolution=(540, 960))
        self.社区界面图标 = Template(r"tpl1717046076553.png", record_pos=(-0.007, 0.759), resolution=(540, 960))
        self.每日福利图标 = Template(r"tpl1699872219891.png", record_pos=(-0.198, -0.026), resolution=(540, 960))
        self.一键领取按钮 = Template(r"tpl1706338731419.png", record_pos=(0.328, -0.365), resolution=(540, 960))
        self.赛事入口 = Template(r"tpl1717046009399.png", record_pos=(-0.269, -0.804), resolution=(540, 960), threshold=0.9, target_pos=6)
        self.资讯入口 = Template(r"tpl1717046009399.png", record_pos=(-0.269, -0.804), resolution=(540, 960), threshold=0.9)
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
        if not connect_status():
            TimeECHO(":营地暂时无法触摸,返回")
            if 初始化检查:
                return True
            return False
        # 打开APP
        if not self.APPOB.重启APP(10):
            TimeECHO(":营地无法打开,返回")
            self.APPOB.关闭APP()
            return False
        sleep(20)  # 等待营地打开
        run_class_command(self=self, command=self.Tool.readfile(self.营地初始化FILE))
        #
        # 判断营地是否登录的界面
        if self.判断营地登录中():
            TimeECHO(":检测到营地登录界面,不领取礼包")
            self.Tool.touchfile(self.营地需要登录FILE)
            self.APPOB.关闭APP()
            return False
        # 这里很容易出问题，主页的图标变来变去
        if not self.判断营地大厅中():
            TimeECHO(":营地未知原因没能进入大厅,再次尝试")
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
                TimeECHO(f"存在[{self.营地需要登录FILE}],重新检测登录状态")
                self.Tool.removefile(self.营地需要登录FILE)
                self.营地初始化(初始化检查=False)
        #
        if os.path.exists(self.营地需要登录FILE):
            TimeECHO(f"检测到{self.营地需要登录FILE}, 不领取礼包")
            return False
        #
        self.初始化成功 = self.营地初始化(初始化检查=False)
        if not self.初始化成功:
            TimeECHO(":营地初始化失败")
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
                TimeECHO(f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.赛事入口, "赛事入口", savepos=True)
        去直播间 = Template(r"tpl1717046024359.png", record_pos=(0.033, 0.119), resolution=(540, 960))
        for i in range(5):
            if self.Tool.existsTHENtouch(去直播间, "去直播间图标"):
                sleep(120)
                return True
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(f"{keystr}{times}超时退出")
                return False
        TimeECHO(f"没进入直播间")
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
                TimeECHO(f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.社区界面图标, "社区界面图标", savepos=True)
        sleep(10)
        #
        圈子图标 = Template(r"tpl1717047527808.png", record_pos=(-0.254, -0.809), resolution=(540, 960))
        if not self.Tool.existsTHENtouch(圈子图标, "圈子图标", savepos=True):
            TimeECHO(f"找不到圈子图标")
            return self.营地任务_圈子签到(times)
        #
        # 需要提前自己加入一些圈子
        营地圈子 = []
        营地圈子.append(Template(r"tpl1717046264179.png", record_pos=(-0.178, -0.511), resolution=(540, 960)))
        营地圈子.append(Template(r"tpl1724585182506.png", record_pos=(0.02, -0.474), resolution=(540, 960)))
        营地圈子.append(Template(r"tpl1724585186597.png", record_pos=(0.22, -0.476), resolution=(540, 960)))
        进入小组 = False
        for i in range(5):
            if self.Tool.existsTHENtouch(营地圈子[0], "营地圈子"):
                sleep(6)
                进入小组 = True
            else:
                sleep(6)
                存在, 营地圈子 = self.Tool.存在任一张图(营地圈子, "营地.资讯入口图标")
                continue
        if not 进入小组:
            TimeECHO(f"找不到互助小组圈子")
            return self.营地任务_圈子签到(times)
        圈子签到图标 = Template(r"tpl1717046286604.png", record_pos=(0.393, -0.3), resolution=(540, 960))
        签到成功图标 = Template(r"tpl1717047898461.png", record_pos=(-0.004, 0.237), resolution=(540, 960))
        if self.Tool.existsTHENtouch(圈子签到图标, "圈子签到图标"):
            if self.Tool.existsTHENtouch(签到成功图标, "签到成功图标"):
                TimeECHO(f"签到成功")
        else:
            TimeECHO(f"可能签到过了")
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
                TimeECHO(f"{keystr}{times}超时退出")
                return False
        #
        TimeECHO(f"{keystr}{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        #
        self.Tool.existsTHENtouch(self.资讯入口, "资讯入口.推荐", savepos=True)
        资讯入口图标 = []
        资讯入口图标.append(Template(r"tpl1717046344191.png", record_pos=(-0.422, -0.37), resolution=(540, 960)))
        资讯入口图标.append(Template(r"tpl1724584561119.png", record_pos=(-0.419, -0.433), resolution=(540, 960)))
        存在, 资讯入口图标 = self.Tool.存在任一张图(资讯入口图标, "营地.资讯入口图标")
        if not 存在 and "资讯入口图标" not in self.Tool.var_dict.keys():
            TimeECHO(f"找不到资讯入口图标")
            return self.营地任务_浏览资讯(times)
        self.Tool.existsTHENtouch(资讯入口图标[0], "资讯入口图标", savepos=True)
        点赞图标 = Template(r"tpl1717046512030.png", record_pos=(0.424, 0.02), resolution=(540, 960))
        评论区 = Template(r"tpl1723599264627.png", record_pos=(0.115, 0.717), resolution=(540, 960))
        资讯页面元素 = [点赞图标, 评论区]
        存在, 资讯页面元素 = self.Tool.存在任一张图(资讯页面元素, "营地.资讯页面元素")
        if not 存在:
            if times % 4 == 3 and "资讯入口图标" in self.Tool.var_dict.keys():
                del self.Tool.var_dict["资讯入口图标"]
            return self.营地任务_浏览资讯(times)
        # 开始滑动点赞
        pos = self.Tool.var_dict["资讯入口图标"]
        for i in range(180):
            sleep(1)
            if self.Tool.existsTHENtouch(点赞图标, "点赞图标", savepos=False):
                sleep(0.5)
            else:
                sleep(1)
                if i % 15 == 0:
                    self.Tool.existsTHENtouch(评论区, "评论区图标", savepos=False)
            TimeECHO(f"浏览资讯中{i}")
            swipe(pos, vector=[0.0, -0.5])
            if self.Tool.timelimit(timekey=f"{keystr}", limit=60*5, init=False):
                TimeECHO(f"浏览资讯时间到")
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
                TimeECHO(f"营地战令经验{times}超时退出")
                return False
        #
        TimeECHO(f"营地战令经验{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.游戏界面图标, "游戏界面图标", savepos=True)
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
            TimeECHO(f"没有找到正式服入口,有可能营地有更新")
            return self.营地战令经验(times)
        # 点开工具箱
        self.Tool.existsTHENtouch(正式服判断图标, "正式服工具图标", savepos=True)
        sleep(10)
        战令入口 = Template(r"tpl1715609828196.png", record_pos=(0.209, -0.004), resolution=(540, 960))
        self.Tool.existsTHENtouch(战令入口, "战令入口", savepos=True)
        sleep(10)
        重新登录 = Template(r"tpl1724463208462.png", record_pos=(0.0, -0.035), resolution=(540, 960))
        if self.Tool.existsTHENtouch(重新登录, "重新登录"):
            self.Tool.touchfile("重新登录营地战令.txt")
            return
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
                TimeECHO(f"没找到战令页面")
                return self.营地战令经验(times)
        战令任务 = Template(r"tpl1715609874404.png", record_pos=(-0.25, -0.706), resolution=(540, 960))
        self.Tool.existsTHENtouch(战令任务, "战令任务", savepos=True)
        sleep(10)
        一键领取 = Template(r"tpl1715610610922.png", record_pos=(0.337, -0.18), resolution=(540, 960))
        self.Tool.existsTHENtouch(一键领取, "一键领取战令经验", savepos=True)
        sleep(5)
        pos = exists(一键领取)
        if pos:
            TimeECHO("仍检测到一键领取战令经验，更新坐标中")
            self.Tool.var_dict["一键领取战令经验"] = pos
            self.Tool.existsTHENtouch(一键领取, "一键领取战令经验", savepos=True)
            sleep(10)

    def 体验服礼物(self, times=1):
        #
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="体验服礼物", limit=60*5, init=False):
                TimeECHO(f"体验服礼物{times}超时退出")
                return False
        #
        TimeECHO(f"体验币{times}")
        self.APPOB.重启APP(10)
        sleep(10)
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        # 都保存位置,最后进不去再return
        self.Tool.existsTHENtouch(self.游戏界面图标, "游戏界面图标", savepos=True)
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
            TimeECHO(f"没有找到体验服入口,有可能营地有更新")
            return self.体验服礼物(times)
        #
        奖励兑换图标 = Template(r"tpl1704381904053.png", record_pos=(-0.209, -0.026), resolution=(540, 960))
        self.Tool.existsTHENtouch(奖励兑换图标, "体验服奖励兑换图标", savepos=True)
        sleep(5)
        奖励兑换网页图标 = Template(r"tpl1704381965060.png", rgb=True, target_pos=7, record_pos=(0.243, -0.496), resolution=(540, 960))
        if not self.Tool.existsTHENtouch(奖励兑换网页图标, "奖励兑换网页图标", savepos=False):
            sleep(20)
            if not self.Tool.existsTHENtouch(奖励兑换网页图标, "奖励兑换网页图标", savepos=False):
                return self.体验服礼物(times)
        # 有时候会让重新登录
        重新登录 = Template(r"tpl1702610976931.png", record_pos=(0.0, 0.033), resolution=(540, 960))
        if self.Tool.existsTHENtouch(重新登录, "重新登录"):
            self.Tool.touchfile("重新登录体验服.txt")
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
                TimeECHO(f"寻找奖励兑换页面中{i}")

        if not pos:
            TimeECHO(":没进入奖励兑换页面")
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
                TimeECHO(f"寻找碎片奖励中{i}")
            swipe(pos, vector=[0.0, -0.5])
        if not 奖励位置:
            TimeECHO("没找到体验币")
            return self.体验服礼物(times)
        #
        touch(奖励位置)
        成功领取 = Template(r"tpl1699874950410.png", record_pos=(-0.002, -0.006), resolution=(540, 960))
        if exists(成功领取):
            TimeECHO(":成功领取")
        else:
            TimeECHO(":领取过了/体验币不够")
        return
        #

    def 每日签到任务(self, times=1):
        TimeECHO(f"营地每日签到{times}")
        #
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地每日签到", limit=60*5, init=False):
                TimeECHO(f"营地每日签到{times}超时退出")
                return False
        #
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 5:
            return False
        # 每日签到
        self.APPOB.重启APP(10)
        sleep(10)
        self.Tool.existsTHENtouch(self.个人界面图标, "王者营地个人界面", savepos=True)
        sleep(5)
        if not self.Tool.existsTHENtouch(self.每日福利图标, "王者营地每日福利", savepos=False):
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
        TimeECHO(f"营地币兑换碎片{times}")
        #
        if self.Tool.存在同步文件():
            return True
        #
        if times == 1:
            self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=True)
        else:
            if self.Tool.timelimit(timekey="营地币兑换碎片", limit=60*5, init=False):
                TimeECHO(f"营地币兑换碎片{times}超时退出")
                return False
        #
        times = times+1
        if times % 4 == 3:
            if not connect_status():
                self.Tool.touch同步文件(self.Tool.独立同步文件)
                return False
        if times > 10:
            return False
        self.APPOB.重启APP(10)
        sleep(10)
        self.Tool.existsTHENtouch(self.个人界面图标, "个人界面")
        sleep(5)
        self.Tool.existsTHENtouch(self.每日福利图标, "每日福利")
        sleep(5)
        self.Tool.existsTHENtouch(self.一键领取按钮, "一键领取按钮")
        # 老款营地币兑换
        if not self.Tool.existsTHENtouch(Template(r"tpl1706338003287.png", record_pos=(0.389, 0.524), resolution=(540, 960)), "营地币兑换"):
            return self.营地币兑换碎片(times)
        兑换页面 = Template(r"tpl1699873075417.png", record_pos=(0.437, 0.167), resolution=(540, 960))
        pos = False
        for i in range(10):
            sleep(5)
            pos = exists(兑换页面)
            if pos:
                break
            else:
                TimeECHO(f":寻找兑换页面中{i}")
        if not pos:
            TimeECHO(":没进入营地币兑换页面")
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
                TimeECHO(f"寻找营地币换碎片中{i}")
            swipe(pos, vector=[0.0, -0.5])
        if not 奖励位置:
            TimeECHO(":没找到营地币")
            return self.营地币兑换碎片(times)
        touch(奖励位置)
        self.Tool.existsTHENtouch(Template(r"tpl1699873472386.png", record_pos=(0.163, 0.107), resolution=(540, 960)))
        self.Tool.existsTHENtouch(Template(r"tpl1699873480797.png", record_pos=(0.163, 0.104), resolution=(540, 960)))
