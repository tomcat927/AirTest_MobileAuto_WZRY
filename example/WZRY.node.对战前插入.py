# 每天早上前两局，标准模式
if self.组队模式 and self.jinristep <= 1: self.标准模式 = self.触摸对战 = True
# 组队的时候不要赢，这样获得的战令经验不到上限，可以额外从营地领经验
# 周日大概率是在刷友情币等项目，不要开模拟对战
if self.组队模式 and self.Tool.time_getweek() < 6: self.触摸对战 = True

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
#批量更新字典
#for 此步位置文件 in range(len(字典位置文件)):self.Tool.var_dict.update(self.Tool.read_dict(字典位置文件[此步位置文件]));self.Tool.save_dict(self.Tool.var_dict, 字典位置文件[此步位置文件])