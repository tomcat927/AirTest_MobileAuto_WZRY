## 运行方式

### 控制端

测试稳定平台: Windows/MacOS/Linux(x86)/Linux(aarch64)

#### 依赖

```
python -m pip  install -i https://pypi.tuna.tsinghua.edu.cn/simple  airtest
python -m pip  install -i https://pypi.tuna.tsinghua.edu.cn/simple  pathos
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

#### 代码修改
使用start_app启动安卓软件的各种坑
- 方式1(monkey). `start_app(package_name)`, 需要修改Airtest的代码添加`--pct-syskeys 0`
- 方式2(am start). `start_app(package_name, activity)`<br>
获得Activity的方法`adb -s 127.0.0.1:5565 shell dumpsys package com.tencent.tmgp.sgame`有一个Activity Resolver Table
<br> Airtest代码中是 `adb -s 127.0.0.1:5565  shell am start -n package_name/package_name.activity`
<br>可并不是所有的app的启动都遵循这一原则,所以如果相同方式2，还是要修改Airtest的代码，变为`package_name/activity`

* ~~本脚本已针对WZRY和WZYD，使用`start_app("com.tencent.gamehelper.smoba","","SGameActivity")`的方式打开程序，不会报错~~
* **综合上述原因，采取方式1**, 按照[https://cndaqiang.github.io/2023/11/10/MobileAuto/](https://cndaqiang.github.io/2023/11/10/MobileAuto/), 添加`--pct-syskeys 0`

#### 执行

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

### 客户端

windows模拟器
* [推荐]Bluestack, 目前支持打开关闭Bluestack更省电. 
* * 兼容hyper-v(Pie 64bit).  
* * [推荐]不兼容hyper-v的**Nougat模式**更省电，适合不用开wsl的笔记本, 而且adb的端口也不会变
* LDPlayer等模拟器
* * 目前通过`adb reboot`实现设备管理，还是费一点电
* * 将object.py中的`os.path.exists("D:\\GreenSoft\\LDPlayer")`替换为你正在使用的模拟器路径即可

Linux 容器
* 使用[remote-android](https://github.com/remote-android/), 支持arm服务器

Mac未发现合适的

移动设备
* Android
* IOS(测试通过 15.8, 16.2)
* IOS端搭建和后续更新和学习AirTest也许会在这里[Android/IOS移动平台自动化脚本(基于AirTest)](https://cndaqiang.github.io/2023/11/10/MobileAuto/)
