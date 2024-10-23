# 每天的第一局，标准模式+触摸模式
self.标准模式 = False
self.触摸对战 = False
self.jinristep <= 1: self.标准模式 = True
self.jinristep <= 1: self.触摸对战 = True

# 第三局开始不再组队
self.jinristep >= 3: self.组队模式 = False
self.jinristep >= 3: self.totalnode = 1


# 自动选择熟练度
字典位置文件=[]
字典位置文件.append("字典.中路.android.var_dict_N.txt")
字典位置文件.append("字典.打野.android.var_dict_N.txt")
字典位置文件.append("字典.发育.android.var_dict_N.txt")
字典位置文件.append("字典.游走.android.var_dict_N.txt")
字典位置文件.append("字典.对抗.android.var_dict_N.txt")
此步位置文件=(self.runstep+self.mynode)%len(字典位置文件)
TimeECHO(f"本步{self.runstep}使用字典文件{字典位置文件[此步位置文件]}")
#当游戏界面改版时，很多位置会变，这里只读入对战的字典
#self.Tool.var_dict.update(self.Tool.read_dict(字典位置文件[此步位置文件]))
dictfile=self.Tool.read_dict(字典位置文件[此步位置文件])
for key in ["参战英雄线路","参战英雄头像"]: self.Tool.var_dict[key]=dictfile[key]
dictfile.update(self.Tool.var_dict)
self.Tool.save_dict(dictfile, 字典位置文件[此步位置文件])