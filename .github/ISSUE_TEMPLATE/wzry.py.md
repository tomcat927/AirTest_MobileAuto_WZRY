name: 为了快速解决你遇到的问题, 请使用此模板进行提问
description: 运行wzry.py过程遇到的各种问题
title: "[windows][雷电模拟器][问题描述]"
labels: ["安装配置","模拟器","对战","礼包","组队"]
body:
  - type: markdown
    attributes:
      value: |
        - 🥰请礼貌**友善**的提问.
        - ✨为本项目点个star, 我会更愉快的回答你的问题.
        - 📚快去阅读最新的[使用教程、问题收录、经验分享](https://wzry-doc.pages.dev/).
  - type: checkboxes
    attributes:
      label: "请在阅读完下面的内容后再进行提问:"
      description: "[使用文档WZRY.doc](https://wzry-doc.pages.dev/)每天都有更新, 提问题前先阅读这些内容."
      options:
        - label: "🌱已阅读[安装指南](https://wzry-doc.pages.dev/guide/install/)"
        - label: "🌱已阅读[配置文件的说明](https://wzry-doc.pages.dev/guide/config/)"
        - label: "🌱已阅读[控制文件的使用方法: 运行时间、礼包功能、对战模式、选择英雄等](https://wzry-doc.pages.dev/guide/file/)"
        - label: "🌱已阅读[常见问题](https://wzry-doc.pages.dev/qa/qa)"
    validations:
      required: false
  - type: dropdown
    id: version
    attributes:
      label: "请选择你在使用的程序及版本号"
      description: |
        - 请尽可能的使用最新的[stable版本](https://github.com/cndaqiang/WZRY/releases)
        - 请尽可能的升级airtest_mobileauto`python -m pip install airtest_mobileauto --upgrade`
        - 你遇到的问题, 可能在最新的版本中已经被修复了.
      options:
        - WZRY == 2.2.9-stable
        - WZRY == 2.2.8-stable
        - AutoWZRY >= 2.2.9a1
        - 其他
    validations:
      required: true
  - type: textarea
    id: other_version
    attributes:
      label: "如果选择了其他，请输入具体版本"
      value: |
        WZRY-2.2.8
        airtest-mobileauto 2.0.13
  - type: textarea
    attributes:
      label: "配置文件: config.win.yaml"
      description: "请在此处填写或上传你的配置文件, 亦可截图粘贴到此处"
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        # 例如
        mynode: 0
        totalnode: 2
        multiprocessing: True
        LINK_dict:
            0: Android:///127.0.0.1:5565
            1: Android:///127.0.0.1:5555
        prefix: wzry
        logfile:
            0: result.0.txt
            1: result.1.txt
    validations:
      required: true
  - type: textarea
    attributes:
      label: "控制文件: WZRY.0.运行模式.txt"
      description: "请在此处填写或上传你的控制文件"
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        # 例如
        self.对战时间=[1.0,23.9]
        self.限时组队时间=23.9
    validations:
      required: true
  - type: textarea
    attributes:
      label: "执行结果: result.0.txt"
      description: "请在此处填写或上传你的执行结果"
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        # 例如
        [11-17 05:00:02]wzry0>控制端(linux)
        [11-17 05:00:02]wzry0>客户端(lin_docker)
        [11-17 05:00:02]wzry0>ADB =(/home/cndaqiang/.local/lib/python3.10/site-packages/airtest/core/android/static/adb/linux/adb)
        [11-17 05:00:02]wzry0>LINK(Android:///127.0.0.1:5555)
        [11-17 05:00:02]wzry0>LINKhead(Android:///127.0.0.1)
    validations:
      required: true
  - type: textarea
    attributes:
      label: "运行目录截图"
      description: "请截图运行目录并粘贴到此处"
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        例如
        ![image](https://github.com/user-attachments/assets/a2eb219b-f485-44fe-bff2-a2a757f3999c)
  - type: textarea
    attributes:
      label: "模拟器设置截图"
      description: "如果问题不涉及模拟器, 可以不填写此输入框."
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        如果你涉及到连接不了模拟器，无法控制模拟器的问题，请在此处粘贴你的模拟器设置页面.
        需要确定你开启了ADB以及ADB的端口以及分辨率和dpi的设置.
        非`960x540`分辨率`dpi=160`的设备, 请自行解决.
        模拟器的安装路径, 多开页面截图等
        例如这个截图就非常充分
        ![image](https://github.com/user-attachments/assets/ce5ca8ce-c1a2-4ac0-a2e3-e1b3ad74f5e0)
  - type: textarea
    attributes:
      label: "游戏页面截图"
      description: "请截图游戏页面并粘贴到此处"
      value: |
        [此处支持: 填写文本、上传文件、粘贴截图]
        如果在游戏过程中遇到问题, 请在此处粘贴**出现问题的画面**
        比如, 无法进入对战时, 游戏内显示的什么画面