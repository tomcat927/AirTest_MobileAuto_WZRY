# 运行方法
如果你在运行时遇到问题
* 可以先在[常见问题收录](https://github.com/cndaqiang/WZRY/issues/42)中查找
* 其次认真阅读本说明
* 其实你读读源码`wzry.py`能解决你99%的问题
* 友善的提出问题[issues](https://github.com/cndaqiang/WZRY/issues)。
* * 附上**执行结果、配置文件、运行目录、游戏页面、模拟器设置页面、cmd/powershell/terminal/vscode/pycharm等运行界面截图**，
* * **@cndaqiang或者为项目start加速解决问题的速度。**
* * 请遵守[提问的礼仪](https://github.com/tvvocold/How-To-Ask-Questions-The-Smart-Way)。没人理会你的傲慢和懒惰。

## 准备工作
* 阅读初阶教程[WZRY.pdf](doc/WZRY.pdf)
* 从Releases页面[下载**最新**代码](https://github.com/cndaqiang/WZRY/releases),不要在Code页面点击下载
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

* 其中**配置文件**可以不写，但是不能乱写。(ps. 这里的**配置文件**是个文件，不是复制配置文件这几个字)
* 不指定配置文件时，即直接**运行`python wzry.py`**，默认单进程控制 `127.0.0.1:5555` 的安卓设备
* 如果要自己写配置文件，复制`config.in`到`config.win.txt`,修改后**运行`python wzry.py config.win.txt`**
* * 下面是一些配置文件示例，足够应对各种情况。
* * 二次开发源码，可以阅读[airtest-mobileauto](https://pypi.org/project/airtest-mobileauto/)。

#### 控制一个模拟器/wifi连接的安卓手机上的王者账户[单人模式]
⭐⭐**初次写配置文件，就用这个，适合控制一个账户**

```
[client]
LINK_dict = {
    0: "Android:///127.0.0.1:5555"}
```

#### 控制两个安卓设备上的王者账户组队[双人组队模式]
⭐⭐**初次尝试组队，就用这个，适合控制两个账户**

```
[client]
totalnode = 2
multiprocessing = True
LINK_dict = {
    0: "Android:///127.0.0.1:5555",
    1: "Android:///127.0.0.1:5565"}
```

#### 这是我在windows上的配置信息及解释
* 我的python环境Anaconda
* 运行脚本流程
![](doc/anaconda.png)
* 初次尝试控制虚拟机的开关机组队可以参考
![](doc/BlueStack多开示例.png)

#### 更多配置示例
* [usb调试、雷电模拟器、MuMu模拟器、BlueStacks](doc/config.example.md)

### 使用vscode/pycharm等软件运行
修改`wzry.py`中的`config_file = ""`为`config_file = "你的配置文件"`，例如
![](doc/vscode.PNG)


## 老手可以尝试开启的功能
* **通过在代码目录创建一些文件来精细的操作代码的运行**
* **注：所有文件都放在`wzry.py`所在路径，采用txt结尾，UTF8格式编码**，

**控制文件**
* `WZRY.oneday.txt`  # 今天执行完之后，直接退出程序。里面记录了总对局数。
* `WZRY.TOUCH.txt `  # 在5v5的对战过程中,移动和平A。通过活动的挂机检测。

**注入python命令**
* 标准的python语法，不支持超过一行的python语句。
* 替换`{self.mynode}`为配置文件中的编号，详见[常见问题](https://github.com/cndaqiang/WZRY/issues/42#issuecomment-2418500316)
* example目录有一些示例文件
* 在线示例[文件控制脚本功能](https://github.com/cndaqiang/WZRY/issues/13)
* `WZRY.{self.mynode}.临时初始化.txt`    # 控制脚本功能：运行时间、礼包等功能的开启关闭。
* `WZRY.{self.mynode}.对战前插入.txt`    # 控制对局过程：快速对战、标准对战、TOUCH模式、对战分路、对战英雄
* `WZRY.{self.mynode}.重新设置英雄.txt`  # 覆盖上面的设定，选择指定英雄


## 每天定时执行脚本
### windows平台的计划任务示例
![](doc/crontab_win.png)

### Linux计划任务示例
```
50 4 * * * pkill -f 'wzry.py'
51 4 * * * /usr/lib/android-sdk/platform-tools/adb kill-server
0 5 * * * cd /home/cndaqiang/soft/AirTest_MobileAuto_WZRY && /bin/bash run.sh
50 8 * * 1-5 pkill -f 'wzry.py'
```