
#### 控制usb连接的安卓手机[单人模式]

```
[client]
LINK_dict = {
    0: "Android:///4e86ac13"}
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