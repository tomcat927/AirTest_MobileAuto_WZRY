self.移动端.重启APP()
self.登录游戏()
self.Tool.timedict["领游戏礼包"] = 0
self.Tool.timedict["领营地礼包"] = 0
self.Tool.timedict["六国远征战"] = 0
self.Tool.timedict["武道大会"] = 0
if self.王者营地礼包: self.每日礼包_王者营地()
self.每日礼包()
self.武道大会()
self.六国远征()
#self.Tool.removefile(self.临时初始化FILE)