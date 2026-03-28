import sys, main, os  # 导入标准库 sys（用于退出程序）、os（用于文件和路径操作），以及 main（主游戏逻辑模块）

import pygame
from pygame.locals import *  # 导入 pygame 游戏库及其常量（如 QUIT）

pygame.init()  # 初始化 pygame，准备使用其功能

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SAVES_DIR = os.path.join(DATA_DIR, "saves")
#  窗口参数设置
fps = 60  # 设置帧率为 60
fpsClock = pygame.time.Clock()  # 创建时钟对象用于控制主循环速度

pygame.mixer.music.load(os.path.join(AUDIO_DIR, "bgmusic.mp3"))  # 或 "Images/bgm.mp3"
pygame.mixer.music.set_volume(0.5)  # 音量0~1
pygame.mixer.music.play(-1)         # -1表示循环播放
width, height = 840, 580  # 设置窗口大小为 840x580
gameDisplay = pygame.display.set_mode((width, height))  # 创建主显示窗口
font_20 = pygame.font.Font(os.path.join(FONTS_DIR, "IBMPlexSans-Regular.ttf"), 20)  # 加载 20 号字体
font_30 = pygame.font.Font(os.path.join(FONTS_DIR, "IBMPlexSans-Regular.ttf"), 30)  # 加载 30 号字体
font_60 = pygame.font.Font(os.path.join(FONTS_DIR, "IBMPlexSans-Regular.ttf"), 60)  # 加载 60 号字体

# 加载所有Png图片
def load_images(path_to_directory):
    """Loads all images"""
    images = {}
    for dirpath, dirnames, filenames in os.walk(path_to_directory):  # 遍历目录
        for name in filenames:
            if name.endswith('.png'):  # 只加载 png 图片
                key = name[:-4]  # 去掉 .png 后缀作为 key
                img = pygame.image.load(os.path.join(dirpath, name)).convert_alpha()  # 加载图片并保留透明度
                images[key] = img  # 存入字典
    return images  # 返回所有图片对象

#  设置——开始界面
def MainMenu():

    Images = load_images(IMAGES_DIR)  # 加载 Images 文件夹下所有图片资源
    game_run = True  # 主循环标志
    screen = "Main"  # 当前界面，初始为主菜单
    step = 0  # 地图选择步进
    cooldown = False  # 鼠标冷却，防止连点
    Names = [["Classic", "Twisty Towers"]]  # 地图名称
    SaveNames = ["Default", "Twisty"]  # 存档名称
    Diff = ["Easy", "Medium", "Hard"]  # 难度名称
    file = open(os.path.join(SAVES_DIR, "saveFile.txt"), "r")  # 打开存档文件
    data = file.readline().split("#")  # 读取存档数据
    if len(data) != 4:  # 如果存档格式不对，使用默认值
        data = ["0", "Medium", "0", "Medium"]
    
    while game_run:  # 主循环
        # gameDisplay.fill((0, 150, 0))  # 填充绿色背景
        gameDisplay.blit(pygame.transform.scale(Images["MenuBG"], (width, height)), (0, 0)) # 绘制背景图片
        pos, pressed = pygame.mouse.get_pos(), pygame.mouse.get_pressed()  # 获取鼠标位置和按键状态

        for event in pygame.event.get():  # 处理事件队列
            if event.type == QUIT:
              pygame.quit()
              sys.exit()

        if screen == "Main":  # 主菜单界面
           
            gameDisplay.blit(pygame.transform.scale(Images["StartBtn"], (180, 270)), (335, 230)) # 绘制“Play”按钮图片
            if 335 <= pos[0] <= 515 and 230 <= pos[1] <= 500 and pressed[0] == 1:  # 检查是否点击了“Play”
                screen = "Map Select"  # 切换到地图选择界面
                cooldown = True  # 设置冷却，防止连点

        elif screen == "Map Select":  # 地图选择界面

            if step == 0:
                gameDisplay.blit(pygame.transform.scale(Images["Meadows"], (200, 150)), (100, 100))  # 显示第一张地图缩略图
                gameDisplay.blit(pygame.transform.scale(Images["TwistyTowers"], (200, 150)), (350, 100))  # 显示第二张地图缩略图
                if 100 <= pos[0] <= 300 and 100 <= pos[1] <= 250 and pressed[0] == 1 and not cooldown:
                    screen = "Dif Select"  # 选择第一张地图后进入难度选择
                    Map = "Classic"
                    MapName = "Default"
                if 350 <= pos[0] <= 550 and 100 <= pos[1] <= 250 and pressed[0] == 1 and not cooldown:
                    screen = "Dif Select"  # 选择第二张地图后进入难度选择
                    Map = "Twisty Towers"
                    MapName = "Twisty"
                    
            for i in range(2):
                pygame.draw.rect(gameDisplay, (100, 100, 100), (100+250*i, 100, 200, 150), 2)  # 绘制地图选择框
                # 用贴图显示地图名称
                # gameDisplay.blit(font_20.render(Names[step][i], True, (0, 0, 0)), (200+250*i-int(font_20.size(Names[step][i])[0]/2), 70))  
                if i == 0:
                    gameDisplay.blit(
                        pygame.transform.scale(Images["classic"], (120, 40)),
                        (135, 255)
                    )
                elif i == 1:
                    gameDisplay.blit(
                        pygame.transform.scale(Images["twisty"], (160, 40)),
                        (370, 255)
                    )
                
            if pressed[0] == 0:
                cooldown = False  # 鼠标松开时，重置冷却

            # pygame.draw.rect(gameDisplay, (100, 0, 0), (10, 10, 100, 75), 0)  # 绘制“Back”按钮底色
            # pygame.draw.rect(gameDisplay, (200, 0, 0), (10, 10, 100, 75), 3)  # 绘制“Back”按钮边框
            # gameDisplay.blit(font_30.render("Back", True, (0, 0, 0)), (25, 20))  # 显示“Back”字样
            gameDisplay.blit(pygame.transform.scale(Images["BackBtn"], (90, 120)), (10, 2)) # 绘制“Back”按钮图片
            if 10 <= pos[0] <= 110 and 2 <= pos[1] <= 122 and pressed[0] == 1 and not cooldown:
                screen = "Main"  # 点击“Back”返回主菜单
                cooldown = True

        elif screen == "Dif Select":  # 难度选择界面
            # gameDisplay.blit(font_60.render(Map, True, (0, 0, 0)), (400-int(font_60.size(Map)[0]/2), 20))  # 显示当前地图名
            if Map == "Classic":
                gameDisplay.blit(pygame.transform.scale(Images["classic"], (300, 60)), (270, 80))
            elif Map == "Twisty Towers":
                gameDisplay.blit(pygame.transform.scale(Images["twisty"], (300, 60)), (270, 80))
            #Different Difficulty Buttons
            for i in range(3):
                # 设置不同难度的底色
                if i == 0:
                    color = (0, 180, 0)      # Easy 绿色
                elif i == 1:
                    color = (220, 220, 0)    # Medium 黄色
                else:
                    color = (200, 50, 50)    # Hard 红色

                pygame.draw.rect(gameDisplay, color, (50+250*i, 400, 200, 150), 0)  # 绘制难度按钮底色
                pygame.draw.rect(gameDisplay, (0, 0, 0), (50+250*i, 400, 200, 150), 3)  # 绘制难度按钮边框
                gameDisplay.blit(font_30.render(Diff[i], True, (0, 0, 0)), (150+250*i-int(font_30.size(Diff[i])[0]/2), 440))  # 显示难度名称

                if 50+250*i <= pos[0] <= 50+250*i+200 and 400 <= pos[1] <= 550 and pressed[0] == 1 and not cooldown:
                    main.game_loop(False, MapName, Diff[i])  # 点击难度按钮，进入主游戏循环

            #The Continue Button
            pygame.draw.rect(gameDisplay, (100, 100, 100), (50, 290, 120, 95), 0)  # 绘制“Continue”按钮底色
            pygame.draw.rect(gameDisplay, (0, 0, 0), (50, 290, 120, 95), 3)  # 绘制“Continue”按钮边框
            gameDisplay.blit(font_20.render("Continue", True, (0, 0, 0)), (60, 330))  # 显示“Continue”字样

            #Displays wave and difficulty of your continue
            gameDisplay.blit(font_20.render("Wave: " + str(data[SaveNames.index(MapName)*2]), True, (0, 0, 0)), (60, 310))  # 显示存档波数
            if data[SaveNames.index(MapName)*2+1] != "0":
                gameDisplay.blit(font_20.render(str(data[SaveNames.index(MapName)*2+1]), True, (0, 0, 0)), (60, 290))  # 显示存档难度
            else:
                gameDisplay.blit(font_20.render("Medium", True, (0, 0, 0)), (60, 290))  # 默认显示 Medium

            if 50 <= pos[0] <= 170 and 290 <= pos[1] <= 385 and pressed[0] == 1 and not cooldown:
                main.game_loop(True, MapName)  # 点击“Continue”按钮，读取存档进入主游戏
            
            #The Back Button
            # pygame.draw.rect(gameDisplay, (100, 0, 0), (10, 10, 100, 75), 0)  # 绘制“Back”按钮底色
            # pygame.draw.rect(gameDisplay, (200, 0, 0), (10, 10, 100, 75), 3)  # 绘制“Back”按钮边框
            # gameDisplay.blit(font_30.render("Back", True, (0, 0, 0)), (25, 20))  # 显示“Back”字样
            
            gameDisplay.blit(pygame.transform.scale(Images["BackBtn"], (90, 120)), (10, 2)) # 绘制“Back”按钮图片
            if 10 <= pos[0] <= 110 and 2 <= pos[1] <= 122 and pressed[0] == 1 and not cooldown:
                screen = "Map Select"  # 点击“Back”返回地图选择界面
                cooldown = True

            if pressed[0] == 0:
                cooldown = False  # 鼠标松开时，重置冷却

        pygame.display.flip()  # 刷新屏幕
        fpsClock.tick(fps)  # 保持帧率

if __name__ == "__main__":
    MainMenu()  # 如果直接运行本文件，则启动主菜单
