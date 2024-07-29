#self.触摸对战=True
#self.标准触摸对战=True
#组队时顺便完成人机检测
if self.组队模式 and hour <= self.限时组队时间 and self.jinristep < 4: self.标准触摸对战 = True
#
#自动分配对战位置
字典位置文件=[]
字典位置文件.append("字典.中路.android.var_dict_N.txt")
字典位置文件.append("字典.打野.android.var_dict_N.txt")
字典位置文件.append("字典.发育.android.var_dict_N.txt")
字典位置文件.append("字典.游走.android.var_dict_N.txt")
字典位置文件.append("字典.对抗.android.var_dict_N.txt")
此步位置文件=(self.runstep+self.mynode)%len(字典位置文件)
TimeECHO(f"本步{self.runstep}使用字典文件{字典位置文件[此步位置文件]}")
self.Tool.var_dict.update(self.Tool.read_dict(字典位置文件[此步位置文件]))
#如果新赛季，一些元素的位置变了，要
#if "今日活跃" in self.Tool.var_dict.keys(): del self.Tool.var_dict["今日活跃"]
#if "本周活跃1" in self.Tool.var_dict.keys(): del self.Tool.var_dict["本周活跃1"]
#if "本周活跃2" in self.Tool.var_dict.keys(): del self.Tool.var_dict["本周活跃2"]
#并更新字典位置
#批量更新字典
#for 此步位置文件 in range(len(字典位置文件)):self.Tool.var_dict.update(self.Tool.read_dict(字典位置文件[此步位置文件]));self.Tool.save_dict(self.Tool.var_dict, 字典位置文件[此步位置文件])
