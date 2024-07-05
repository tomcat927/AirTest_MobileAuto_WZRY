# AirTest_MobileAuto_WZRY

基于AirTest框架的面向对象的**多进程移动APP控制**

![GitHub forks](https://img.shields.io/github/forks/cndaqiang/AirTest_MobileAuto_WZRY?color=60c5ba&style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/cndaqiang/AirTest_MobileAuto_WZRY?color=ffd700&style=for-the-badge)

## 介绍

* 仅需替换`self.APPID`和`TASK=wzrj_task(self.移动端,"5v5匹配",0)`即可对新APP进行适配

### Features of AirTest_MobileAuto

#### 增强稳定性

* 连接状态检查
* 套壳AirTest函数, 多次运行失败则尝试重新连接而不是报错
* * 减少网络故障获取截图失败导致的程序终止. 
* * 极小概率有意外:ios有时需要重新插拔数据线才能`tidevice list`检测到设备.
* * 修复`start_app`在一些安卓系统上的报错
* 全程自动运行, 无人值守. 检测到出错, 自动重启APP, 仍无法恢复则重启控制端(如docker、安卓模拟器)进行重置.
* 时间采用`UTC/GMT+08:00`, 方便根据中国游戏的任务刷新时间执行脚本
* 格式化输出`[%m-%d %H:%M:%S]+info`

#### 设备管理模块 `deviceOB`

* 面向对象: 传递对象, 各个模块应用统一进行设备管理
* 客户端: 
* - Android(手机, BlueStack for Windows, [docker](https://github.com/remote-android/) for Linux)
* - IOS(Iphone and Ipad with [WebDriverAgent(WDA)&tidevice](https://cndaqiang.github.io/2023/11/10/MobileAuto/))
* 控制端: Windows/Mac/Linux
* APP管理: 打开、关闭、重启
* 设备管理: 

|  客户端 | 控制端  | 客户端控制  |
| ------------ | ------------ | ------------ |
| BlueStack/**LDPlayer** |  Windows | 打开、关闭、重启模拟器  |
| USB线连接的手机 |  Windows | 重启安卓系统  |
| Docker  | Linux  | 打开、关闭、重启容器  |
| IOS  | Mac  | tidevice重连、重启IOS  |
| 远程/无线Android设备  | ALL  | adb重新连接  |

#### APP管理模块 `appOB`
* 打开、关闭、重启APP

#### 相关工具DQWheel

* 基于文件系统的多进程支持
* - 单脚本n进程`python -u object.py -n`
* - 多脚本n进程`python -u object.py i n`
* - 同步、广播
* 文件管理和变量存储读写
* 时间管理: 获取时间、计时
* 增强AirTest
* - 利用文件&字典进行存取图片坐标, 减少重复寻找元素坐标时间.<br>亦可用于选中特定位置(如王者荣耀英雄按熟练度排序选择熟练度最低的英雄的坐标)
* - 存在则点击, 不断存在点击等



## 开发实例: 王者荣耀脚本

### 💻 运行方式
🌟[**Howto**](howtorun.md)
* [下载最最新代码](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/releases)
* [配置控制端、客户端](howtorun.md)
* 启动


一些实例
* 重装了Windows系统, 记录了全新安装python+雷电模拟器使用本脚本控制王者荣耀的详细过程[Windows全新安装python、依赖+雷电模拟器](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/issues/5#issuecomment-1901771876)
* [图形化控制单台小米手机示例](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/issues/5#issuecomment-1890969863)
* [全终端控制单台小米手机示例](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/issues/5#issuecomment-1890967828)
* [Android/IOS移动平台自动化脚本(基于AirTest)](https://cndaqiang.github.io/2023/11/10/MobileAuto/)


### Features

* 全部自动化操作
* - 自动开关机
* - 自动切换对战
* - 自动组队.(现在通过房主和其他账户建立友情关系, 利用友情关系自动进入房主账户)
* - 自动领礼包
* - 出错自动同步
* - 健康系统自动休息启动
* 创建文件控制已有脚本的运行方式[实例](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/issues/3)
* - 控制程序暂停、终止、对战模式
* - 永久/暂时替换对战英雄
* - 直接插入代码运行

### 礼包

* 友情对战: 友情币领取、奖励兑换(积分夺宝券、皮肤碎片、英雄碎片、友情重燃皮肤礼包、铭文碎片)
* 邮件礼包: 好友邮件、系统邮件
* 妲己一键领奖
* ~~日常任务礼包(2024赛年每日礼包转移至战令系统)~~
* 战令礼包、战令任务礼包(2024赛年)
* KPL观赛战令自动观赛领取经验升级
* 战队商店自动领取英雄碎片
* 商城每日免费钻石碎片随机礼包
* 王者营地: 体验服兑换碎片礼包、每日签到、每日任务、营地币每周兑换英雄碎片
* 玉镖夺魁自动领每日两个飞镖, 后面可以自己换积分夺宝券

### 对战

* 自动切换组队与单人模式、对战方式、对战模式等
* 常规5v5人机匹配(优先星耀其次青铜), 适合完成每日任务和提高熟练度, 对战每次可以获取金币和王者等级经验
* 模拟人手(移动+平A)进行标准/快速的青铜5v5模式, 每日会自动进行几次, 适合完成活动的*标准对战非挂机*条件. <br>此外模拟人手+快速对战对战胜利几率低, 不适合刷英雄熟练度, 但是不挂机能获得更多的金币奖励
* 王者模拟战, 刷信誉分专用, 每日5分. 站令的每期任务:20场娱乐模式, 可以用模拟战刷齐
* ~~冒险模式(2024赛年官方关闭入口/功能): 武道大会、六国远征. 额外的金币上限、商店兑换~~
* `使用savepos=True`可以把英雄图像选为最后一个, 并把英雄按照熟练度排序, 即可不断提高最低英雄的熟练度. 例如[自动调整分路并选择熟练度最低的英雄](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY/issues/13#issuecomment-2205392546)



## 致谢

* ❤️ 本脚本大量参考了[WZRY_AirtestIDE@XRSec](https://github.com/XRSec/WZRY_AirtestIDE)项目, 是我学习AirTest脚本的主要参考.
* 本脚本的历史版本[WZRY_AirtestIDE_XiaoMi11@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_XiaoMi11), [WZRY_AirtestIDE_emulator@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_emulator)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=cndaqiang/AirTest_MobileAuto_WZRY&type=Date)](https://star-history.com/#cndaqiang/AirTest_MobileAuto_WZRY&Date)
