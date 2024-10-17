#mklink  WZRY.1.临时初始化.txt WZRY.0.临时初始化.txt 创建软连接
#ln -s  WZRY.0.临时初始化.txt WZRY.1.临时初始化.txt 创建软连接
self.devmode=True
#self.组队模式=False
#self.登录游戏()
#................................................................................
uptime=23.9
self.对战时间=[0.1,uptime]
self.限时组队时间=uptime
#................................................................................
#每天组队打0,1,2,...,nstep-1共nstep场，组队5v5匹配
#每天组队打0,1,2,...,ostep-1共ostep场，单人5v5匹配|模拟战
nstep=3
ostep=0  # 为了获得更多的经验，可以将 ostep 设为模拟战 或者 0。
self.对战模式="5v5匹配" if self.jinristep <  nstep else "模拟战"
if self.Tool.time_getweek() == 6: self.对战模式 = "5v5匹配" #周日一直打人机模式
#..................................................................................
# 组队模式
if self.新的一天: self.组队模式 = True
self.组队模式 = self.组队模式 and self.jinristep < nstep
if not self.组队模式: self.限时组队时间=self.对战时间[0]+0.1
if not self.组队模式: self.Tool.touchfile(self.无法进行组队FILE)
#................................................................................
#结束游戏时的操作
endgame = self.jinristep >=  nstep+ostep
if self.jinristep > 1 and not self.组队模式: endgame = True
if self.mynode >  0: endgame = self.jinristep >=  nstep # 辅助账户退场，节约算力
if os.path.exists(self.青铜段位FILE): endgame = True # 只刷星耀局
if endgame: self.对战时间[1]=self.对战时间[0]+0.1
if endgame and self.mynode == 0: self.Tool.timedict["领营地礼包"] = 0 # 主进程多领一次营地，提高从营地礼包的成功率
if endgame and self.mynode == 0: self.每日礼包_王者营地()
#................................................................................
# 每日任务礼包=False，周末前不领取王者的战令经验，可以额外从营地获取战令经验
self.每日任务礼包=self.Tool.time_getweek() > 5 # 5 == 周六
#................................................................................
self.友情礼包_积分夺宝 = True
self.友情礼包_皮肤碎片 = True
self.友情礼包_英雄碎片 = False
self.友情礼包_铭文碎片 = True
self.友情礼包_皮肤宝箱 = True
self.友情礼包_回城宝箱 = True
self.友情礼包_击败宝箱 = True
self.活动礼包 = True
self.祈愿礼包 = False
self.外置礼包_王者营地 = False
