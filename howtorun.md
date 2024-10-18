# 运行方法
如果你在运行时遇到问题
* 可以先在[常见问题收录](https://github.com/cndaqiang/WZRY/issues/42)中查找
* 其次认真阅读本说明
* 其实你读读源码`wzry.py`能解决你99%的问题
* 友善的提出问题[issues](https://github.com/cndaqiang/WZRY/issues)
* * 提问时，附上你的执行结果、配置文件、模拟器截图，
* * 提示时@cndaqiang或者为项目start提醒我有人提问。


## 准备工作

* [下载**最新**代码](https://github.com/cndaqiang/WZRY/releases)
* **WZRY有特殊活动(比如周年庆)时，可以看看我是否提供了**[资源更新包](https://github.com/cndaqiang/WZRY/issues/8)。
* * 等不急更新的，可以自己使用AirTestIDE修改对应的图片。
* 升级依赖

```
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  --upgrade
```


## 开启模拟器/手机的ADB调试。
* 本脚本测试通过的[模拟器推荐](https://github.com/cndaqiang/WZRY/issues/23)
* 建议采用**`960x540`的分辨率`dpi=160`**，脚本内部有额外的加速命令
* * 该分辨率可以利用我的[example/字典.分路.android.var_dict_N.zip](example/字典.分路.android.var_dict_N.zip)进行加速
* * 即复制`字典.游走.android.var_dict_N.txt`为`android.var_dict_mynode.txt`(`mynode`默认是`0`,具体解释[13](https://github.com/cndaqiang/WZRY/issues/13#issue-2381467976))
* * 以及[自动调整分路并选择熟练度最低的英雄](https://github.com/cndaqiang/WZRY/issues/13#issuecomment-2205392546)。
* 其他分辨率也可以运行，代码会自动生成你的字典文件`android.var_dict_mynode.txt`，执行速度会越来越快。
* * 但是有些活动图标在不同的分辨率上显示效果不同，可能无法识别成功，需要你使用AirTestIDE修改对应的图片。

![Alt text](doc/LDplayer.png)

## 运行方式

### 终端运行

```
python -u wzry.py 配置文件
```

* **其中配置文件可以省略，但是不能乱写**
* 不指定配置文件时，即直接**运行`python wzry.py`**，默认单进程控制 `127.0.0.1:5555` 的安卓设备
* 如果要自己写配置文件，复制`config.in`到`config.win.txt`,修改后**运行`python wzry.py config.win.txt`**
* * 下面是一些配置文件示例，足够应对各种情况。
* * 二次开发源码，可以阅读[airtest-mobileauto](https://pypi.org/project/airtest-mobileauto/)。

#### 控制usb连接的安卓手机[单人模式]

```
[client]
LINK_dict = {
    0: "Android:///4e86ac13"}
```

#### 控制一个模拟器/wifi连接的安卓手机上的王者账户[单人模式]
⭐⭐**新手初次写配置文件，就用这个，适合控制一个账户**

```
[client]
LINK_dict = {
    0: "Android:///127.0.0.1:5555"}
```

#### 控制两个安卓设备上的王者账户组队[双人组队模式]

```
[client]
totalnode = 2
multiprocessing = True
LINK_dict = {
    0: "Android:///192.168.192.10:5555",
    1: "Android:///4e86ac13"}
```

####  控制两个BlueStacks模拟器上的王者账户[双人组队模式]
* 注: BlueStacks模拟的ADB端口是`5555+10*i`

```
[client]
totalnode = 2
# 不设置BlueStackdir，脚本也可以正常运行。
# 设置后支持启动、隐藏模拟器等操作，7*24h运行时更省电。
BlueStackdir = C:\Program Files\BlueStacks_nxt
#BlueStack模拟器的名字,在BlueStack多开管理器中设定，该参数用于关闭模拟器
BlueStack_Windows = {
    0: "BlueStacks_multi0",
    1: "BlueStacks_multi1"}
multiprocessing = True
LINK_dict = {
    0: "Android:///127.0.0.1:5555",
    1: "Android:///127.0.0.1:5565"}
```

####  控制两个LDPlayer模拟器上的王者账户[双人组队模式]
* 注: LDPlayer模拟的ADB端口是`5555+2*i`

```
[client]
totalnode = 2
# 不设置LDPlayerdir，脚本也可以正常运行。
# 设置后支持关闭、启动、隐藏模拟器等操作，7*24h运行时更省电。
LDPlayerdir = D:\GreenSoft\LDPlayer
multiprocessing = True
LINK_dict = {
    0: "Android:///127.0.0.1:5555",
    1: "Android:///127.0.0.1:5557"}
```

####  控制两个MuMu模拟器上的王者账户[双人组队模式]
* 注: MuMu模拟的ADB端口是`16384+32*i`

```
[client]
totalnode = 2
# 不设置MuMudir，脚本也可以正常运行。
# 设置后支持关闭、启动、隐藏模拟器等操作，7*24h运行时更省电。
MuMudir = D:\Program Files\Netease\MuMu Player 12\shell
multiprocessing = True
LINK_dict = {
    0: "Android:///127.0.0.1:16384",
    1: "Android:///127.0.0.1:16416"}
#
[control]
#将运行日志输出到文件，适合于监控windows的计划任务
logfile={
    0: "result.0.txt",
    1: "result.1.txt"}
```


#### Linux控制三个docker容器上的王者账户[三人组队模式]

```
# 节点配置
totalnode = 3
# 不设置dockercontain，脚本也可以正常运行。
# 设置后支持关闭、启动、容器等操作，7*24h运行时更省电。
dockercontain = {
    0: "androidcontain0.high",
    1: "androidcontain1"}
    2: "androidcontain2"}
multiprocessing = True
LINK_dict = {
    0: "Android:///127.0.0.1:15555",
    1: "Android:///127.0.0.1:5565",
    2: "Android:///127.0.0.1:5575"}
```

####  一个MuMu模拟器(主号)和一个BlueStack模拟器(小号)混合使用[双人组队模式][multiprocessing=False分离控制]
* MuMu适合手机控制模拟器打游戏,资源消耗大, 两个MuMu同时运行容易闪退
* BlueStack非常稳定, 作为小号的模拟器使用

config.0.txt
```
[client]
mynode = 0
totalnode = 2
multiprocessing = False
MuMudir = D:\Program Files\Netease\MuMu Player 12\shell
MuMu_Instance ={0: "0"}
LINK_dict = {0: "Android:///127.0.0.1:16384"}
[control]
figdir=assets
logfile={0: "result.0.txt"}
```
config.1.txt
```
[client]
mynode = 1
totalnode = 2
multiprocessing = False
BlueStackdir = C:\Program Files\BlueStacks_nxt
BlueStack_Instance ={1: "Nougat32"}
BlueStack_Windows = {1: "BlueStacks_multi0"}
LINK_dict = {1: "Android:///127.0.0.1:5555"}
[control]
figdir=assets
logfile={1: "result.1.txt"}
```
使用powershell运行示例
```
PS D:\SoftData\git\WZRY> Start-Process -FilePath "python" -ArgumentList "wzry.py", "config.0.txt" -NoNewWindow;Start-Process -FilePath "python" -ArgumentList "wzry.py", "config.1.txt" -NoNewWindow
```

### 使用AirTestIDE软件运行

* **不推荐, 我只用AirTestIDE修改脚本的图片资源**
* 下载地址[AirTestIDE](https://airtest.netease.com/), 配置python的路径
* 用AirTest直接打开wzry.py
* 如果要修改配置参数，更改`config_file = ""`为`config_file = "你的配置文件"`
* 点击运行

![Alt text](doc/airtestguirun.png)

# 高级功能
* **通过在代码目录创建一些文件来动态调整代码的运行模式，可以实现自动切换分路、选择熟练度最低的英雄，进行王者模拟战等操作**
* 控制文件 `txt` 不参与仓库同步, [文件控制运行示例](https://github.com/cndaqiang/WZRY/issues/13)
* **注：所有文件都默认采用UTF8格式编码**
* 以最新代码为准, 下面的内容仅供参考。


## 控制参数
控制参数决定软件的运行模式
```
self.只战一天FILE = "WZRY.oneday.txt"  # 今天执行完之后，直接结束程序。适用采用crontab等模式周期性运行脚本，而不采用本脚本自带的循环。
self.今日休战FILE = "WZRY.tomorrow.txt"  # 今天不打了，明天开始，适合于离开办公室时运行脚本，但是不要执行任何命令，明天早上开始执行
self.触摸对战FILE = "WZRY.TOUCH.txt"  # 在5v5的对战过程中,频繁触摸,提高金币数量
self.标准模式FILE = f"WZRY.{self.mynode}.标准模式.txt"  # 检测到该文件后该次对战使用5v5标准对战模式
self.临时组队FILE = "WZRY.组队.txt"
self.玉镖夺魁签到FILE = "玉镖夺魁签到.txt"
self.免费商城礼包FILE = f"WZRY.{self.mynode}.免费商城礼包.txt"  # 检测到该文件后领每日商城礼包
self.KPL每日观赛FILE = f"WZRY.KPL每日观赛FILE.txt"
self.更新体验服FILE = f"WZRY.{self.mynode}.更新体验服.txt"  # 检测到该文件后登录体验服领取体验币
```

## 注入命令
也可以通过python命令，直接修改计算参数和控制
```
self.重新设置英雄FILE = f"WZRY.{self.mynode}.重新设置英雄.txt"
self.临时初始化FILE = f"WZRY.{self.mynode}.临时初始化.txt"
self.对战前插入FILE = f"WZRY.{self.mynode}.对战前插入.txt"
```

## 更新资源
```
self.图片更新FILE = "WZRY.图片更新.txt"
```


# 其他补充
## 关于windows平台的计划任务
* [**推荐**]`只在用户登录时运行`
* * 启动脚本时会跳出窗口，可以自动打开模拟器,和正常执行脚本相同。
* * 锁屏之后还可以执行，可以正常启动模拟器 
* `不管用户是否登录都要运行`
* * 需要输入密码，启动脚本时不会跳出窗口，可以自动打开模拟器。
* * 多开器，和用户界面以及任务管理器无论怎么找都找不到模拟器的进程。无法限制模拟器只用的资源。
* * 脚本和其他ADB工具可以调试这些隐藏的模拟器。

### 配置示例
![](doc/crontab_win.png)

## Linux计划任务示例
```
50 4 * * * pkill -f 'wzry.py'
51 4 * * * /usr/lib/android-sdk/platform-tools/adb kill-server
0 5 * * * cd /home/cndaqiang/soft/AirTest_MobileAuto_WZRY && /bin/bash run.sh
50 8 * * 1-5 pkill -f 'wzry.py'
```