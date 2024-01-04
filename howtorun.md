## 运行方式

### 控制端

测试稳定平台: Windows/MacOS/Linux(x86)/Linux(aarch64)

#### 依赖

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

#### 代码修改

mac/linux都会报错 airtest使用monkey控制安卓的命令 `monkey -p com.tencent.tmgp.sgame -c android.intent.category.LAUNCHER 1` , #会报错

```
** SYS_KEYS has no physical keys but with factor 2.0%.
airtest.core.error.AdbError: stdout[b'  bash arg: -p\n  bash arg: com.tencent.tmgp.sgame\n  bash arg: -c\n  bash arg: android.intent.category.LAUNCHER\n  bash arg: 1\n'] stderr[b'args: [-p, com.tencent.tmgp.sgame, -c, android.intent.category.LAUNCHER, 1]\n arg: "-p"\n arg: "com.tencent.tmgp.sgame"\n arg: "-c"\n arg: "android.intent.category.LAUNCHER"\n arg: "1"\ndata="com.tencent.tmgp.sgame"\ndata="android.intent.category.LAUNCHER"\n** SYS_KEYS has no physical keys but with factor 2.0%.\n']
```

添加 `--pct-syskeys 0`

修改 `/home/cndaqiang/.local/lib/python3.10/site-packages/airtest/core/android/adb.py`

```
1387         if not activity:
1388             self.shell(['monkey --pct-syskeys 0', '-p', package, '-c', 'android.intent.category.LAUNCHER', '1'])
1389         else:
1390             self.shell(['am', 'start', '-n', '%s/%s.%s' % (package, package, activity)])
```

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

模拟器
* Windows Bluestack 多开adb都可以, 还兼容hyper-v(Pie 64bit).  不兼容hyper-v的**Nougat模式**更省电，适合不用开wsl的笔记本, 而且adb的端口也不会变
* Linux使用[remote-android](https://github.com/remote-android/), 支持arm服务器
* Mac 未发现合适的

移动设备
* Android
* IOS(测试通过 15.8, 16.2)
* IOS端搭建和后续更新和学习AirTest也许会在这里[Android/IOS移动平台自动化脚本(基于AirTest)](https://cndaqiang.github.io/2023/11/10/MobileAuto/)
