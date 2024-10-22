## 王者荣耀脚本

基于[AirTest](https://airtest.netease.com/)和[airtest-mobileauto@cndaqiang](https://github.com/cndaqiang/airtest_mobileauto)的王者荣耀日活脚本。

![GitHub forks](https://img.shields.io/github/forks/cndaqiang/WZRY?color=60c5ba&style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/cndaqiang/WZRY?color=ffd700&style=for-the-badge)

### 运行方式

更多细节见:[**Howto**](howtorun.md)

### 自动化功能

* 自动开启关闭模拟器、容器、手机
* [多开组队](https://github.com/cndaqiang/WZRY/issues/42#issuecomment-2418505810)
* 无人值守：出错重新进行同步
* 检测游戏闪退、模拟器关闭，重新启动王者或重启模拟器
* 健康系统自动休息启动
* 优先星耀人机模式，次数达到上限后自动切换青铜人机
* [调整分路并选择熟练度最低的英雄](https://github.com/cndaqiang/WZRY/issues/13#issuecomment-2205392546)
* 移动和平A
* 丰富的自定义功能




### 礼包

* 友情对战: 友情币领取、选择性的奖励兑换
* - 积分夺宝券、皮肤碎片、英雄碎片、友情重燃皮肤礼包、铭文碎片
* 邮件礼包: 好友邮件、系统邮件
* 妲己一键领奖
* 战令礼包、战令任务礼包
* 回忆礼册
* 祈愿页面领取每日的免费祈愿币, 之后可以手动换积分、钻石等
* - 玉镖夺魁自动领对战签到的飞镖
* [停止更新]KPL观赛战令自动观赛领取经验升级
* [停止更新]战队商店自动领取英雄碎片
* [停止更新]商城每日免费钻石碎片随机礼包

### 王者营地和体验服
`wzry.py`支持自动领取相同虚拟机内部的王者营地礼包和体验币
* 王者营地: 体验服兑换碎片礼包、每日签到、每日任务、营地币每周兑换英雄碎片、战令经验
* - 营地的不同版本界面有差异、QQ微信登录的界面也有差异, 个别礼包可能无法识别完成
* 更新体验服，领取体验币
* - 注: 在Root的安卓上登录体验服，会被封号，与本脚本无关。如使用体验服的功能，请关闭模拟器的Root选项

王者营地礼包和体验服更新也可以独立启动、不依赖于wzry.py。手册无。运行方式:
* `python -u wzyd.py config.ce.txt`
* `python -u tiyanfu.py config.ce.txt`


### 对战

* 5v5人机单人模式、组队模式、标准模式、快速模式、星耀难度、青铜难度
* - 人机模式无法举报、人机不扣信誉分
* - (极端情况: 虚拟机太卡，点击确定匹配没有反应，系统会扣信誉分)
* - 默认开局后挂机，适合完成每日任务、战令任务、**提高熟练度**,
* - 开启TOUCH模式，自动移动+平A，适合完成活动的**标准对战非挂机**对战要求
* 王者模拟战单人模式、组队模式
* - 刷信誉分专用, 每日上限+5分. 
* - 战令的每期任务: 20场娱乐模式, 可以用模拟战刷齐


## 相关项目

* 本脚本初期大量参考了[WZRY_AirtestIDE@XRSec](https://github.com/XRSec/WZRY_AirtestIDE)项目
* 本脚本的历史版本
* * [WZRY_AirtestIDE_XiaoMi11@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_XiaoMi11)
* * [WZRY_AirtestIDE_emulator@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_emulator)
* 同样基于[airtest-mobileauto](https://github.com/cndaqiang/airtest_mobileauto)的项目
* * [autotask_android](https://github.com/cndaqiang/autotask_android)基于安卓ADB的网站、APP签到

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=cndaqiang/WZRY&type=Date)](https://star-history.com/#cndaqiang/WZRY&Date)
