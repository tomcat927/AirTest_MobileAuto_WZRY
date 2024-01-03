# AirTest_MobileAuto_WZRY
面向对象的AirTest多进程框架

![GitHub stars](https://img.shields.io/github/stars/cndaqiang/AirTest_MobileAuto_WZRY?color=ffd700&style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/cndaqiang/AirTest_MobileAuto_WZRY?color=60c5ba&style=for-the-badge)
[![GitHub release (by tag)](https://img.shields.io/github/downloads/cndaqiang/AirTest_MobileAuto_WZRY/latest)](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/releases/latest)

* 提供了多进程支持,多个基于文件的同步广播工具
* AirTest设备控制代码,重启APP,重启设备端(androidcontain/Linux, BlueStack/Windows, iphone/MacOS)
* 仅需替换`self.APPID`和`TASK=wzrj_task(self.移动端,"5v5匹配",0)`即可对新APP进行适配
* IOS端搭建和后续更新和学习AirTest也许会在这里[Android/IOS移动平台自动化脚本(基于AirTest)](https://cndaqiang.github.io/2023/11/10/MobileAuto/)
* 全程自动运行,无人值守. 包括自动启动虚拟机/docker,自动组队对战、领礼包
* 套壳AirTest函数,减少网络故障获取截图失败导致的程序终止. 极小概率有意外:ios有时需要重新插拔数据线才能`tidevice list`检测到设备.


## 致谢
第一次尝试进行面向对象编程,还有很多面向过程的影子.

本脚本大量参考了[WZRY_AirtestIDE@XRSec](https://github.com/XRSec/WZRY_AirtestIDE)项目,是我学习AirTest脚本的主要参考.

本脚本的历史版本[WZRY_AirtestIDE_XiaoMi11@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_XiaoMi11),[WZRY_AirtestIDE_emulator@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_emulator)

## 控制端运行方式
测试稳定平台:Windows/MacOS/Linux(x86)/Linux(aarch64)

### 依赖
```
python -m pip  install -i https://pypi.tuna.tsinghua.edu.cn/simple  airtest,pathos
```
Linux
```
sudo apt-get install libgl1-mesa-glx
```
Linux(ARM)
```
cndaqiang@oracle:~/.local/lib/python3.10/site-packages/airtest/core/android/static/adb/linux$ mv adb adb.bak
cndaqiang@oracle:~/.local/lib/python3.10/site-packages/airtest/core/android/static/adb/linux$ ln -s /usr/bin/adb .
```
Mac
```
chmod +x /Users/cndaqiang/anaconda3/lib/python3.11/site-packages/airtest/core/android/static/adb/mac/adb
```

### 代码修改
mac/linux都会报错 airtest使用monkey控制安卓的命令 `monkey -p com.tencent.tmgp.sgame -c android.intent.category.LAUNCHER 1`,#会报错
```
** SYS_KEYS has no physical keys but with factor 2.0%.
airtest.core.error.AdbError: stdout[b'  bash arg: -p\n  bash arg: com.tencent.tmgp.sgame\n  bash arg: -c\n  bash arg: android.intent.category.LAUNCHER\n  bash arg: 1\n'] stderr[b'args: [-p, com.tencent.tmgp.sgame, -c, android.intent.category.LAUNCHER, 1]\n arg: "-p"\n arg: "com.tencent.tmgp.sgame"\n arg: "-c"\n arg: "android.intent.category.LAUNCHER"\n arg: "1"\ndata="com.tencent.tmgp.sgame"\ndata="android.intent.category.LAUNCHER"\n** SYS_KEYS has no physical keys but with factor 2.0%.\n']
```

添加`--pct-syskeys 0`

修改`/home/cndaqiang/.local/lib/python3.10/site-packages/airtest/core/android/adb.py`
```
1387         if not activity:
1388             self.shell(['monkey --pct-syskeys 0', '-p', package, '-c', 'android.intent.category.LAUNCHER', '1'])
1389         else:
1390             self.shell(['am', 'start', '-n', '%s/%s.%s' % (package, package, activity)])
```

### 执行
```
python -u object.py 2>&1 | tee result
```
n个进程模式
```
python -u object.py -n 2>&1 | tee result
```
分散执行n进程模式(适合调试报错)
```
#每个终端执行
python -u object.py   0   n
python -u object.py   1   n
#...
python -u object.py (n-1) n
```

## 客户端
模拟器
- Windows Bluestack 多开adb都可以,还兼容hyper-v(Pie 64bit).  不兼容hyper-v的**Nougat模式**更省电，适合不用开wsl的笔记本,而且adb的端口也不会变
- Linux使用[remote-android](https://github.com/remote-android/),支持arm服务器
- Mac 未发现合适的

移动设备
- Android
- IOS(测试通过 15.8,16.2)

## WZRY部分代码说明
### 金币获取
- 双号组队每周金币获取上限约9105
- - 5v5和模拟战共用金币上限(0/4100)
- - 六国远征、武道大会的金币不受前面限制平均(`(10个*6国*4次+5个*10局大会)*7天~2030`)
- - 每日礼包(`挑战35*5*7+日任务150*7+周任务700~2975`)
- 如何快速获取货币:
- - 六国远征、武道大会速度最快
- - 触摸形式的5v5人机耗时但是金币也远大于
- - 模拟战也出现过即使最后一名,金币也很多的情况
- 模拟战等模式账户之前没有进行过/新赛季, 自己提前操作一下, 避免有变动

### 熟练度
- `使用savepos=True`可以把英雄图像选为最后一个,并把英雄按照熟练度排序,即可不断提高最低英雄的熟练度

### 文件控制
控制文件`txt`不参与仓库同步

| 文件  | 功能  | 备注  |
| :------------: | :------------: | :------------: |
|  `self.结束游戏FILE="WZRY.ENDGAME.txt"` | 本局结束后关闭WZRYAPP, 同时结束对战循环  | 用户创建  |
|  `self.SLEEPFILE="WZRY.SLEEP.txt"` |  本局结束后`sleep(5min)`直到该文件被删除, 用于暂停代码,手动进行抽奖领礼包  | 用户创建   |
|`self.触摸对战FILE="WZRY.TOUCH.txt"` |在对战过程中尝试移动英雄和平A,通过非挂机的检测判断金币更多 |用户创建 |
|`self.标准模式触摸对战FILE="WZRY.标准模式TOUCH.txt" ` |使用标准模式对战, 并在对战过程中尝试移动英雄和平A,用于满足一些任务对标准人机对战非挂机的检测判断 |用户创建 |
| `self.临时组队FILE="WZRY.组队.txt"`| 仅适用于并行组队模式, 现在代码中组队模式仅在每天的前几个小时, 后面如果还想组队又不想重跑程序，可以通过创建该文件恢复组队模式| 用户创建|
| `self.临时初始化FILE = f"WZRY.{self.mynode}.临时初始化.txt"`| 仅适用于王者荣耀循环对战的开头插入任意自己想添加的代码,亦可在这里强制进行一些计算| 用户创建|
| `self.对战前插入FILE = f"WZRY.{self.mynode}.对战前插入.txt"`| 在对战循环前再次修改配置,初始化和对战前还是会自动计算相关参数,这里强制覆盖提高自由度| 用户创建|
|`self.重新设置英雄FILE=f"WZRY.{self.mynode}.重新设置英雄.txt"` |不修改代码和重启程序,修改对战过程中使用的英雄,内容见`WZRY.node.重新设置英雄.py`,通过控制`savepos`来决定是否更新字典  |用户创建 |
|`sself.重新登录FILE = f"WZRY.{self.mynode}.重新登录FILE.txt"` |因为各种原因账户退出后,程序自动创建,若存在该文件则等待10min,直到用户删除 |程序自动生成、用户创建 |
|`var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.mynode}.txt"` | 存储很多图片坐标点的文件,减少图片识别时间,删除后重新识别 | 程序自动生成|
|`青铜模式.txt`|存在则进行青铜快速人机,不存在则进行星耀人机|程序自动生成/用户创建
|`self.prefix+"六国远征.txt"`|每日自动创建,如存在该文件则进行相关计算,计算完成后删除该文件|程序自动生成/用户创建
|`self.prefix+"武道大会.txt"`|每日自动创建,如存在该文件则进行相关计算,计算完成后删除该文件|程序自动生成/用户创建
|`self.玉镖夺魁签到=os.path.exists("玉镖夺魁签到.txt")`|是否进行玉镖夺魁,定期的活动|程序自动生成/用户创建
|`NeedRebarrier.txt`|多进程运行时,强制跳过当前所有任务,进行统一的barrier. 即使多进程模式已经处于独立组队模式，这一文件也强制让所有进程进行一次barrier|程序出错自动生成/用户创建|
| `self.prefix+"NeedRebarrier.txt"` |本进程跳过所有任务,回到循环开头,重新初始化 |  程序出错自动生成/用户创建 |
|`self.prefix+"重新登录体验服.txt"` | 营地需要定期重新登录才可以兑换礼包| 程序生成,用户删除|
|`self.独立同步文件 = self.prefix+"NeedRebarrier.txt"` | 同步工具, 单个进程出错重新初始化 | 程序自动生成/用户创建
|`self.辅助同步文件 = "NeedRebarrier.txt"` | 同步工具, 单个进程出错创建所有进程重新初始化 | 程序自动生成/用户创建


### WZRY更新
- 2023-12-26 autopep8格式化代码,添加格式化参数`--max-line-length=1000`避免换行
- 2023-12-25 增加娱乐模式中的武道大会,金币获取上限增加<br>注:使用这些功能需要提前进行过这些对战，不然wzry总演示对战,与正常对战流程不同
- 2023-12-22 增加娱乐模式中的六国远征,金币获取速度更快


![](./tpl1703206481443.png)


## DQWheel说明

## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=cndaqiang/AirTest_MobileAuto_WZRY&type=Date)](https://star-history.com/#cndaqiang/AirTest_MobileAuto_WZRY&Date)