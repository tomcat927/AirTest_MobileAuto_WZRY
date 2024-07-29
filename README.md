## 王者荣耀脚本
基于[AirTest](https://airtest.netease.com/)和[airtest-mobileauto](https://github.com/cndaqiang/airtest_mobileauto)的王者荣耀日活脚本。

![GitHub forks](https://img.shields.io/github/forks/cndaqiang/AirTest_MobileAuto_WZRY?color=60c5ba&style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/cndaqiang/AirTest_MobileAuto_WZRY?color=ffd700&style=for-the-badge)

### 运行方式
更多细节见:[**Howto**](howtorun.md)

### 功能

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

* 本脚本大量参考了[WZRY_AirtestIDE@XRSec](https://github.com/XRSec/WZRY_AirtestIDE)项目, 是我学习AirTest脚本最早的资料.
* 本脚本的历史版本[WZRY_AirtestIDE_XiaoMi11@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_XiaoMi11), [WZRY_AirtestIDE_emulator@cndaqiang](https://github.com/cndaqiang/WZRY_AirtestIDE_emulator)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=cndaqiang/AirTest_MobileAuto_WZRY&type=Date)](https://star-history.com/#cndaqiang/AirTest_MobileAuto_WZRY&Date)
