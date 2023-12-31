## AirTest_MobileAuto NewYear-1.0

* 仓库[AirTest_MobileAuto_WZRY@cndaqiang](https://github.com/cndaqiang/AirTest_MobileAuto_WZRY)

* 相关资源[Android/IOS移动平台自动化脚本(基于AirTest)](https://cndaqiang.github.io/2023/11/10/MobileAuto/)

### Features of AirTest_MobileAuto

#### 增强稳定性

* 连接状态检查
* 套壳AirTest函数, 多次运行失败则尝试重新连接而不是报错
* 统一时区
* 格式化输出`[%m-%d %H:%M:%S]+info`

#### 设备管理deviceOB

* 面向对象: 传递对象, 各个模块应用统一进行设备管理
* 客户端: 
* - Android(手机, BlueStack for Windows, [docker](https://github.com/remote-android/) for Linux)
* - IOS(Iphone and Ipad with [WebDriverAgent(WDA)&tidevice](https://cndaqiang.github.io/2023/11/10/MobileAuto/))
* 控制端: Windows/Mac/Linux
* APP管理: 打开、关闭、重启
* 设备管理: 

|  客户端 | 控制端  | 客户端控制  |
| ------------ | ------------ | ------------ |
|  BlueStack |  Windows | 打开、关闭、重启  |
| Docker  | Linux  | 打开、关闭、重启  |
| IOS  | Mac  | tidevice重连、重启  |
| Android  | -  | adb重新连接  |

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

### 王者荣耀: A Showcase of AirTest's Prowess

#### Features

* 全部自动化操作
* - 自动开关机
* - 自动切换对战
* - 自动领礼包
* - 出错自动同步
* - 健康系统自动休息启动
* 创建文件控制程序运行
* - 控制程序暂停、终止、对战模式
* - 永久/暂时替换对战英雄
* - 直接插入代码运行

#### 礼包

* 友情对战: 友情币领取、奖励兑换(积分夺宝券、皮肤碎片、英雄碎片、友情重燃皮肤礼包、铭文碎片)
* 邮件礼包: 好友邮件、系统邮件
* 妲己一键领奖
* 日常任务礼包(仅限2023赛年)(2024赛年官方关闭, 礼包转移至战令系统)
* 战令礼包、战令任务礼包(仅限2024赛年)
* 战队商店自动领取英雄碎片
* 王者营地: 体验服兑换碎片礼包、每日签到、每日任务、营地币每周兑换英雄碎片

#### 对战

* 自动切换组队与单人模式、对战方式、对战模式等
* 常规5v5人机匹配(优先星耀其次青铜), 适合完成每日任务和提高熟练度, 对战每次可以获取金币和王者等级经验
* 模拟人手(移动+平A)进行标准/快速的青铜5v5模式, 每日会自动进行几次, 适合完成活动的*标准对战非挂机*条件. 此外模拟人手+快速对战对战胜利几率低, 不适合刷英雄熟练度, 但是不挂机能获得更多的金币奖励
* 王者模拟战, 刷信誉分专用, 每日5分
* 冒险模式(2024赛年官方关闭入口/功能): 武道大会、六国远征. 额外的金币上限、商店兑换
