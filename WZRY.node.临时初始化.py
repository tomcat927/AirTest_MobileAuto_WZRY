#self.移动端.重启APP()
#self.登录游戏()
#self.Tool.timedict["领游戏礼包"] = 0
#self.Tool.timedict["领营地礼包"] = 0
#self.Tool.timedict["六国远征战"] = 0
#self.Tool.timedict["武道大会"] = 0
#if self.王者营地礼包: self.每日礼包_王者营地()
#self.每日礼包()
#self.武道大会()
#self.六国远征()
#self.Tool.removefile(self.临时初始化FILE)

#临时调整对战模式
#self.进入大厅()
#self.对战模式="模拟战"
#self.对战模式="5v5匹配"

#
#特殊活动
#王者营地的图标变化


#修改虚拟机类型
#self.移动端.LINK="127.0.0.1:5585"
#self.LINKport = self.移动端.LINK.split(":")[-1]
#self.LINKhead = self.移动端.LINK[:-len(self.移动端.LINKport)]
#self.移动端.mynode=3
#self.移动端.连接设备()

## 一些图库, 后期使用图片更新
#self.登录界面开始游戏图标 = Template(r"tpl1692947242096.png", record_pos=(-0.004, 0.158), resolution=(960, 540), threshold=0.9)
#self.大厅对战图标 = Template(r"tpl1689666004542.png", record_pos=(-0.102, 0.145), resolution=(960, 540))
#self.大厅万象天工= Template(r"tpl1693660085537.png", record_pos=(0.259, 0.142), resolution=(960, 540))
#self.房间中的开始按钮图标 = []
#self.房间中的开始按钮图标.append(Template(r"tpl1689666117573.png", record_pos=(0.096, 0.232), resolution=(960, 540)))
#self.房间中的开始按钮图标.append(Template(r"tpl1704331759027.png", record_pos=(0.105, 0.235), resolution=(960, 540)))
##新年活动结束时,替换一个常规的取消准备按钮
#self.房间中的取消准备按钮 =  []
#self.房间中的取消准备按钮 .append(Template(r"tpl1707180405239.png", record_pos=(0.104, 0.235), resolution=(960, 540)))
#self.大厅元素=[]
#self.大厅元素.append(self.大厅对战图标)
#self.大厅元素.append(self.大厅万象天工)
#self.房间元素=[]
#self.房间元素.extend(self.房间中的开始按钮图标)
#self.房间元素.extend(self.房间中的取消准备按钮)
#self.房间元素.append(Template(r"tpl1690442701046.png", record_pos=(0.135, -0.029), resolution=(960, 540)))
#self.房间元素.append(Template(r"tpl1700304317380.png", record_pos=(-0.38, -0.252), resolution=(960, 540)))
#self.房间元素.append(Template(r"tpl1691463676972.png", record_pos=(0.356, -0.258), resolution=(960, 540)))
#self.房间元素.append(Template(r"tpl1700304304172.png", record_pos=(0.39, -0.259), resolution=(960, 540)))
    
self.登录界面开始游戏图标=Template(r"tpl1707180169881.png", record_pos=(0.002, 0.16), resolution=(960, 540))
self.大厅对战图标 = Template(r"tpl1707180221045.png", record_pos=(-0.106, 0.141), resolution=(960, 540))
self.大厅元素.append(self.大厅对战图标)
self.大厅元素 = list(set(self.大厅元素))
self.房间中的开始按钮图标.append(Template(r"tpl1707180283040.png", record_pos=(0.102, 0.235), resolution=(960, 540)))
self.房间中的取消准备按钮 .append(Template(r"tpl1707180405239.png", record_pos=(0.104, 0.235), resolution=(960, 540)))
self.房间元素.extend(self.房间中的开始按钮图标)
self.房间元素.extend(self.房间中的取消准备按钮)
self.房间元素.append(Template(r"tpl1707180444046.png", record_pos=(-0.424, -0.029), resolution=(960, 540)))
self.房间元素 = list(set(self.房间元素))
