# RongYouXueTang Automation Script
# Description: Automates course video watching on the RongYouXueTang platform
# Original author: UltramarineW from HIT
# Modified by: Andy Tao from USTB
# Last updated: 2025-5-6
# This script is for educational purposes only. Use at your own risk.

import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import time
import ddddocr

# 读取账号信息
username = "your_username"  # 请在此处输入你的账号
password = "your_password"  # 请在此处输入你的密码

debug = 0
already_learned_course = []

# setup driver
options = webdriver.EdgeOptions()
options.add_experimental_option("detach", True)
options.add_argument("--mute-audio")
driver = webdriver.Edge(options=options)
driver.maximize_window()


# 处理验证码 调用ddddocr的api
def handleCaptcha():
    try:
        operation = True
        counter = 0
        while operation:
            if counter > 5:
                operation = False
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'yzmmsg_xh'))
            )
            yzmmsg = driver.find_element(By.ID, 'yzmmsg_xh')
            # save captcha for classification
            try:
                yzmmsg.screenshot('./save.png')
            except Exception as e:
                print('验证码截图失败')
                counter += 1
                print(e)
                continue
            ocr = ddddocr.DdddOcr(show_ad=False)
            with open('./save.png', 'rb') as f:
                img_bytes = f.read()
                res = ocr.classification(img_bytes)
            f.close()
            print(f'验证码:{res}')
            driver.find_element(By.ID, 'xhYzm').send_keys(res)
            driver.find_element(By.ID, 'login_zsxh').click()
            counter = counter + 1
            sleep(1)
            operation = False

    except Exception as e:
        print('验证码处理失败')
        print(e)


def loginAccount():
    if username == '' or password == '':
        print('请编辑main.py文件并输入对应的账号和密码')
        exit(-1)
    sleep(1)
    
    # 点击"学号登录"按钮
    try:
        # 根据提供的HTML元素信息，使用XPath定位"学号登录"链接
        xh_login = driver.find_element(By.XPATH, "//a[contains(text(), '学号登录')]")
        xh_login.click()
        print("已点击'学号登录'按钮")
        sleep(1)  # 等待界面切换
    except Exception as e:
        print("未找到'学号登录'按钮:", e)
    
    
    # 选择学校：北京科技大学 (4111010008)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'bjssxy'))
    )
    # 使用Select类处理下拉菜单
    from selenium.webdriver.support.ui import Select
    school_select = Select(driver.find_element(By.ID, 'bjssxy'))
    school_select.select_by_value('4111010008')  # 北京科技大学的值
    print("已选择'北京科技大学'")
    
    sleep(1)  # 等待选择生效
    driver.find_element(By.ID, 'usercode_zsxh').send_keys(username)
    driver.find_element(By.ID, 'password_zsxh').send_keys(password)
    handleCaptcha()


def findCourse():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'styu-b-r'))
        )
        class_div = driver.find_element(By.CLASS_NAME, 'styu-b-r')
        # print(f'class_div {class_div}')
        class_div.find_element(By.XPATH, './a[1]').click()
    except Exception as e:
        print('查找<继续学习>失败')
        print(e)


def getContent():
    try:
        left_side = driver.find_element(By.XPATH, '/html/body/div[12]/div[2]/div/div[1]/div[1]')
        course_list = left_side.find_elements(By.TAG_NAME, 'dd')
        return course_list

    except Exception as e:
        print('获取目录失败')
        print(e)


def playVideo(course):
    try:
        print()
        print('Current learning ', course.text.replace('\n', ' '))
        tag = course.find_element(By.TAG_NAME, 'a')
        tag.click()
        sleep(2)

        iframe_node = driver.find_element(By.NAME, 'zwshow')
        driver.switch_to.frame(iframe_node)
        if debug:
            print('success switch to the frame')

        # 获取该课程中所有视频的数量
        video_count = 0
        video_index = 1
        
        # 先检查有多少个视频
        while True:
            try:
                # 检查是否存在下一个视频索引
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, f'sp_index_{video_index}'))
                )
                video_count += 1
                video_index += 1
            except:
                break
        
        print(f"本节课共有 {video_count} 个视频")
        
        # 处理所有视频
        for video_index in range(1, video_count + 1):
            # 检查此视频是否已完成
            tag = driver.find_element(By.ID, f'sp_index_{video_index}')
            if tag.text == '已完成':
                print(f'视频 {video_index}/{video_count} 已完成，跳过')
                continue
                
            print(f'开始播放视频 {video_index}/{video_count}')
            
            # 点击视频封面中的开始图片
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, f"myVideoImg_{video_index}"))
            )
            
            # 尝试多种方法点击视频播放按钮
            try:
                # 方法1：通过onclick属性查找播放按钮
                play_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"#myVideoImg_{video_index} a[onclick*='videoclick']"))
                )
                print(f"找到视频 {video_index} 播放按钮(通过onclick属性)")
                driver.execute_script("arguments[0].click();", play_button)
            except Exception as e1:
                print(f"方法1查找视频 {video_index} 播放按钮失败:", e1)
                try:
                    # 方法2：通过ID和子元素定位
                    video_img = driver.find_element(By.ID, f'myVideoImg_{video_index}')
                    play_button = video_img.find_element(By.TAG_NAME, 'a')
                    print(f"找到视频 {video_index} 播放按钮(通过myVideoImg_{video_index})")
                    driver.execute_script("arguments[0].click();", play_button)
                except Exception as e2:
                    print(f"方法2查找视频 {video_index} 播放按钮失败:", e2)
                    # 方法3：尝试获取spdm值并调用videoclick函数
                    try:
                        # 尝试从spdm属性获取视频ID
                        spdm_element = driver.find_element(By.CSS_SELECTOR, f"div[videoid='myVideo_{video_index}']")
                        spdm_value = spdm_element.get_attribute("spdm")
                        print(f"尝试使用JavaScript直接调用videoclick函数，spdm={spdm_value}")
                        driver.execute_script(f"videoclick(null, '{spdm_value}')")
                    except Exception as e3:
                        print(f"所有方法尝试失败，无法播放视频 {video_index}:", e3)
                        continue
            
            print(f"视频 {video_index} 开始播放")

            # 找到视频元素
            WebDriverWait(driver, 10).until((
                EC.presence_of_element_located((By.ID, f"myVideo_{video_index}"))
            ))
            video = driver.find_element(By.ID, f"myVideo_{video_index}")
            url = driver.execute_script("return arguments[0].currentSrc;", video)
            print(f"视频 {video_index} URL: {url}")

            # 获取播放视频的时间
            duration_time = driver.execute_script("return arguments[0].duration", video)
            current_time = driver.execute_script("return arguments[0].currentTime", video)
            print(f'视频 {video_index}: current_time: {current_time}, duration_time: {duration_time}')

            # tqdm进度条
            pbar = tqdm.tqdm(total=duration_time)
            while current_time < duration_time - 0.5:  # 允许0.5秒误差
                last_time = current_time
                current_time = driver.execute_script("return arguments[0].currentTime", video)
                sleep(1)
                pbar.update(current_time - last_time)
            pbar.close()

            # 验证视频是否已完成
            tag = driver.find_element(By.ID, f'sp_index_{video_index}')
            print(f"视频 {video_index} 完成状态: {tag.text}")
            
        # 检查是否所有视频都已完成
        all_completed = True
        for video_index in range(1, video_count + 1):
            tag = driver.find_element(By.ID, f'sp_index_{video_index}')
            if tag.text != '已完成':
                all_completed = False
                break
        
        if all_completed:
            print('本节课所有视频已学完')
            already_learned_course.append(course.text)
            return True
        else:
            print('本节课还有未完成的视频')
            return False

    except Exception as e:
        print("播放视频失败")
        print(e)
        return False


def judgeExist(element, by, value):
    try:
        element.find_element(by=by, value=value)

    except Exception as e:
        return False
    return True


def chooseCourse(course_list):
    already_learned = []
    not_learned = []
    learning = []
    skipped_tests = 0  # 记录跳过的测试数量

    for course in course_list:
        # 检查是否是单元测试
        is_test = False
        try:
            # 方法1：通过文本内容检查
            course_text = course.text.lower()
            if "单元测试" in course_text or "测试" in course_text:
                is_test = True
            
        except:
            pass
        
        # 如果是测试，跳过它
        if is_test:
            if debug:
                print('T (跳过测试)')
            skipped_tests += 1
            continue
            
        # 处理非测试课程，按原逻辑分类
        if judgeExist(course, By.ID, 'a'):
            already_learned.append(course)
            if debug:
                print('*')
        elif judgeExist(course, By.ID, 'r'):
            if course.text in already_learned_course:
                already_learned.append(course)
                continue
            not_learned.append(course)
            if debug:
                print('o')
        else:
            learning.append(course)
            if debug:
                print('-')
    
    print(f'共有{len(not_learned)}门还未学习的课程, 共有{len(already_learned)}门已经学习的课程, 跳过了{skipped_tests}个测试')
    return not_learned


def startPlay():
    try:
        while True:
            course_list = getContent()
            not_learned = chooseCourse(course_list)
            course_name = not_learned[0].text
            if len(not_learned) == 0:
                break
            played = playVideo(not_learned[0])
            if debug:
                print(already_learned_course)
            if debug:
                print('hit')
            if played:
                already_learned_course.append(course_name)
            driver.refresh()

    except Exception as e:
        print('播放失败')
        print(e)

def closeLoginPopup():
    """关闭登录成功后的弹窗"""
    try:
        # 等待弹窗出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'popup-main-xq'))
        )
        # 找到并点击关闭按钮
        close_button = driver.find_element(By.CLASS_NAME, 'popup-main-xq')
        close_button.click()
        print("已关闭登录成功弹窗")
        sleep(1)  # 给页面一些时间响应点击操作
    except Exception as e:
        print("关闭弹窗失败或弹窗不存在:", e)
        
if __name__ == '__main__':
    # Login into account
    driver.get('https://cumtb.livedu.com.cn/ispace4.0/moocMainIndex/mainIndex.do')
    login_time_start = time.time()
    driver.find_element(By.CLASS_NAME, 'header-dengl').click()
    loginAccount()
    login_time_end = time.time()
    print('成功登录')
    print(f'Login time:{login_time_end - login_time_start}s')

    # 关闭登录成功后弹出的弹窗
    closeLoginPopup()
    
    # Find course
    findCourse()

    # Start learning course
    startPlay()
