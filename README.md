# 前言

- 首先要感谢大佬 [UltramarineW](https://github.com/UltramarineW) 的 开源代码[RongYouXueTang-Automation-Script](https://github.com/UltramarineW/RongYouXueTang-Automation-Script)
- 本人在此基础上做了对于USTB学生的登陆使用适配
- 如果要适配其他学校，可自行修改代码里的学校代码，代码中罗列了学校和对应的代码

# 融优学堂自动化脚本

>   仅供学习交流

## Feature


-   适配需要学号登陆的用户
-   自动识别验证码 登录网页界面
-   自动识别未完成课程目录并开始学习未完成课程
-   自动识别课程视频，可以完成多视频的课程
-   自动跳过单元测试

## Usage

1.   因为使用selenium库中的Edge Driver, 所以需要安装Edge与相应版本的WebDriver并配置环境变量
WebDriver可以在 https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/ 中找到，注意要和自己Edge的版本相对应
下载完解压，将其中的exe放到python解释器目录下

2.   将repo clone到本地并安装依赖库

```bash
git clone https://github.com/study-233/RongYouXueTang-Automation-Script.git
cd RongYouXueTang-Automation-Script
pip install tqdm selenium ddddocr
```
    
3.  编辑`main.py` 更改其中的username、password、school_code

4. 在terminal中运行脚本

```bash
python main.py
```

    

    
