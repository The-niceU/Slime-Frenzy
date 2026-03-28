# 本文件实现了怪物的属性初始化、分裂/变身、绘制、移动、状态变化（如着火、冰冻、混乱）、碰撞箱同步等，是塔防游戏怪物行为的核心
import pygame, random, sys, math, os
from pygame.locals import *
 
pygame.init()

# 导入所需库并初始化 pygame

class Monster():
    """Class for all the enemies"""
    def __init__(self, rank, wave, camo, Images, mapName):

# 定义怪物类，初始化函数接收怪物类型、波数、是否隐身、图片资源、地图名
        #Setting up base variables
        self.rank = rank  # 怪物类型（决定颜色、速度、血量等）
        self.step = 0  # 当前走到第几个检查点
        speed = [1.5, 2, 2.5, 3, 3.5, 3, 2.5, 1.2, 2, 1.2]  # 各类型怪物基础速度
        self.speed = speed[self.rank-1] * (1 + (0.01*(int(wave/150)+1)*wave))  # 怪物速度随波数递增
        self.wave = wave  # 当前波数
        self.height, self.width = 30, 30  # 怪物宽高
        self.dead = False  # 是否死亡
        Colors = [(200, 0, 0), (0, 0, 200), (0, 200, 0), (255, 255, 0), (255,105,180), (0, 0, 0), (50, 50, 50), (128, 0, 128), (0, 100, 0), (150, 150, 150)]
        self.color = Colors[self.rank-1]  # 怪物颜色
        self.camo = camo  # 是否隐身
        self.hit = []  # 被击中记录
        self.fire = [False,0,0,0,0]  # 着火状态及参数
        self.speedModifier = [1,0]  # 速度修正（如冰冻）
        self.permaslow = False  # 是否永久减速
        self.confused = False  # 是否混乱（倒退）
        self.health = 1  # 血量
        if self.rank == 9:
            self.health = 3  # 特殊怪物血量更高
        elif self.rank == 10:
            self.health = 10
        self.addMonster = []  # 分裂出的新怪物
        self.map = mapName  # 地图名
        #All checkpoints on the map
        if mapName == "Default":
            self.checkpoints = [(6, 5), (6, 2), (3, 2), (3, 9), (13, 9), (13, 4), (17, 4)]  # 路径点
            self.x, self.y = -100, 200  # 起始坐标
        elif mapName == "Twisty":
            self.checkpoints = [(14, 9), (1, 9), (1, 1), (11, 1), (11, 6), (4, 6), (4, -1)]
            self.x, self.y = 560, -100
        self.duplicate = False  # 是否分裂
        self.cooldown = 0  # 行动冷却
        self.img = Images  # 图片资源

        #Setting up the hitbox
        self.image = pygame.Surface([self.width, self.height])  # 创建怪物表面
        self.rect = self.image.get_rect()  # 获取矩形碰撞箱
        self.rect.top = self.y
        self.rect.bottom = self.y + self.height
        self.rect.left = self.x
        self.rect.right = self.x + self.width


# 初始化怪物的各种属性，包括路径、起点、碰撞箱等
    def ReRank(self, new_Rank):
        """Changes the rank of the monster to any other rank"""

# 怪物变身/降级（如被火烧、分裂等）

        if self.rank == 8 and new_Rank != 8:
            self.addMonster.append(5)  # 紫色怪分裂出黑色怪
        elif self.rank == 10 and new_Rank != 10:
            for i in range(4):
                self.addMonster.append(9)  # Boss分裂出4个绿色怪
        if new_Rank <= 0:
            self.dead = True  # 变成0级则死亡
        else:
            self.rank = new_Rank  # 更新类型
            Colors = [(200, 0, 0), (0, 0, 200), (0, 200, 0), (255, 255, 0), (255,105,180), (0, 0, 0), (50, 50, 50), (128, 0, 128), (0, 100, 0), (150, 150, 150)]
            self.color = Colors[self.rank-1]  # 更新颜色
            speed = [1.5, 2, 2.5, 3, 3.5, 3, 2.5, 1.2, 2, 1.2]
            self.speed = speed[self.rank-1] * (1 + (0.01*(int(self.wave/50)+1)*self.wave))  # 更新速度
            if self.rank == 9:
                self.health = 3
            elif self.rank == 10:
                self.health = 50
        
        # 处理分裂、死亡、属性重置等

    def draw(self, gameDisplay):
        # 贴图显示，图片命名如 monster1.png、monster2.png ...，加载后 key 为 "monster1"、"monster2" ...
        key = f"monster{self.rank}"
        if key in self.img:
            img = pygame.transform.scale(self.img[key], (self.width, self.height))
            gameDisplay.blit(img, (self.x, self.y))
        else:
            # 如果没有图片，退回到原有矩形显示
            if self.rank != 10:
                pygame.draw.rect(gameDisplay, self.color, (self.x, self.y, self.width, self.height), 0)
            else:
                pygame.draw.rect(gameDisplay, self.color, (self.x - int(self.width/3), self.y - int(self.height/3), self.width*2, self.height*2), 0)


# 普通怪物画小矩形，Boss画大矩形

        #Drawing camo bloons
        if self.camo:
            if self.rank != 6:
                # 多层不同深浅的矩形，表现隐身
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.8),int(self.color[1]*0.8),int(self.color[2]*0.8)), (self.x + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.5),int(self.color[1]*0.5),int(self.color[2]*0.5)), (self.x + int(self.width/3) + int(self.width/5), self.y + int(self.height/3) + int(self.height/5), int(self.width/3), int(self.height/3)), 0)    
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.75),int(self.color[1]*0.75),int(self.color[2]*0.5)), (self.x + int(self.width/5), self.y + int(self.height/3) + int(self.height/5), int(self.width/3), int(self.height/3)), 0) 
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.5),int(self.color[1]*0.5),int(self.color[2]*0.5)), (self.x + int(self.width/3) + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.3),int(self.color[1]*0.3),int(self.color[2]*0.3)), (self.x + int(self.width/3)*2 + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.5),int(self.color[1]*0.5),int(self.color[2]*0.5)), (self.x + int(self.width/3)*2 + int(self.width/5), self.y + int(self.height/5)+int(self.width/3)*2, int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]*0.75),int(self.color[1]*0.8),int(self.color[2]*0.75)), (self.x + int(self.width/5), self.y + int(self.height/5)+int(self.width/3)*2, int(self.width/3), int(self.height/3)), 0) 
            else:
                # 特殊颜色处理
                pygame.draw.rect(gameDisplay, (int(self.color[0]+50),int(self.color[1]+50),int(self.color[2]+50)), (self.x + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]+30),int(self.color[1]+30),int(self.color[2]+30)), (self.x + int(self.width/3) + int(self.width/5), self.y + int(self.height/3) + int(self.height/5), int(self.width/3), int(self.height/3)), 0)    
                pygame.draw.rect(gameDisplay, (int(self.color[0]+50),int(self.color[1]+50),int(self.color[2]+50)), (self.x + int(self.width/5), self.y + int(self.height/3) + int(self.height/5), int(self.width/3), int(self.height/3)), 0) 
                pygame.draw.rect(gameDisplay, (int(self.color[0]+50),int(self.color[1]+50),int(self.color[2]+50)), (self.x + int(self.width/3) + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]+70),int(self.color[1]+70),int(self.color[2]+70)), (self.x + int(self.width/3)*2 + int(self.width/5), self.y + int(self.height/5), int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]+50),int(self.color[1]+50),int(self.color[2]+50)), (self.x + int(self.width/3)*2 + int(self.width/5), self.y + int(self.height/5)+int(self.width/3)*2, int(self.width/3), int(self.height/3)), 0)
                pygame.draw.rect(gameDisplay, (int(self.color[0]+50),int(self.color[1]+50),int(self.color[2]+50)), (self.x + int(self.width/5), self.y + int(self.height/5)+int(self.width/3)*2, int(self.width/3), int(self.height/3)), 0) 

# 隐身怪物绘制多层不同深浅的矩形，表现隐身效果

        if self.fire[0]:
            colors = [(255,0,0), (255,165,0), (255,255,0)]
            for i in range(9):
                pygame.draw.rect(gameDisplay, colors[random.randint(0,2)], (self.x+random.randint(5, 20), self.y+random.randint(5, 20), random.randint(5, 20), random.randint(5, 20)), 0)
# 着火特效，绘制多块红橙黄矩形
        # if self.rank != 10:
        #     pygame.draw.rect(gameDisplay, (100, 100, 100), (self.x + int(self.width/5), self.y + int(self.height/5), self.width, self.height), 2)
        # else:
    
        #     pygame.draw.rect(gameDisplay, (100, 100, 100), (self.x - int(self.width/3), self.y - int(self.height/3), self.width*2, self.height*2), 2)
# 绘制怪物边框
    def movement(self, Lives, speed):


    # 怪物移动逻辑：Checking to see whether the monster is in range of the next checkpoint
        if not self.confused:
            if (self.checkpoints[self.step][0]*40-self.speed <= self.x <= self.checkpoints[self.step][0]*40+self.speed and
                self.checkpoints[self.step][1]*40-self.speed <= self.y <= self.checkpoints[self.step][1]*40+self.speed):
                self.x, self.y = self.checkpoints[self.step][0]*40, self.checkpoints[self.step][1]*40
                self.step += 1
                if self.step == len(self.checkpoints):
                    modifier = 1
                    if self.rank == 10:
                        modifier = 4
                    self.dead = True
                    Lives -= self.rank*modifier
            else:
                #Else move it towards it's next checkpoint
                if self.x < self.checkpoints[self.step][0]*40:
                    self.x += int(self.speed*speed*self.speedModifier[0])
                elif self.x > self.checkpoints[self.step][0]*40:
                    self.x -= int(self.speed*speed*self.speedModifier[0])
                elif self.y > self.checkpoints[self.step][1]*40:
                    self.y -= int(self.speed*speed*self.speedModifier[0])
                elif self.y < self.checkpoints[self.step][1]*40:
                    self.y += int(self.speed*speed*self.speedModifier[0])
        # 正常前进：到达下一个检查点则 step+1，否则朝目标点移动
        else:
            Checks = {"Default": (-10000, self.y), "Twisty": (self.x, -10000)}
            if self.step == 0:
                xCheck, yCheck = Checks[self.map]
            else:
                xCheck, yCheck = self.checkpoints[self.step-1][0]*40, self.checkpoints[self.step-1][1]*40
            if (xCheck-self.speed <= self.x <= xCheck+self.speed and
                yCheck-self.speed <= self.y <= yCheck+self.speed):
                self.x, self.y = xCheck, yCheck
                self.step -= 1
                if self.step == -1:
                    self.dead = True
                    print("Woah, slow down buddy\nThat's too many Smoke Bombs for 1 man to handle")
            else:
                #Else move it towards it's next checkpoint
                if self.x < xCheck:
                    self.x += int(self.speed*speed*self.speedModifier[0])
                elif self.x > xCheck:
                    self.x -= int(self.speed*speed*self.speedModifier[0])
                elif self.y > yCheck:
                    self.y -= int(self.speed*speed*self.speedModifier[0])
                elif self.y < yCheck:
                    self.y += int(self.speed*speed*self.speedModifier[0])
# 混乱状态：倒退回上一个检查点
        if self.fire[0] == True:
            self.fire[1] -= 1
            self.fire[3] -= 1
            if self.fire[1] <= 0:
                self.fire[1] = self.fire[2] + 0
                if self.rank >= 6 and self.rank - self.fire[4] < 6:
                    self.duplicate = True
                self.ReRank(self.rank - self.fire[4])
                

            if self.fire[3] <= 0:
                self.fire[0] = False

# 着火处理：定时掉血/降级/分裂，火焰时间结束后熄灭
        if self.speedModifier[1] <= 0:  
            if not self.permaslow:
                self.speedModifier[0] = 1
            else:
                self.speedModifier[0] = 0.75
        else:
            self.speedModifier[1] -= 1
# 冰冻/减速处理
        self.confused = False

        return Lives
# 每次移动后重置混乱状态，返回剩余生命值
    def update(self, Lives, speed, gameDisplay):
        self.draw(gameDisplay)
        if speed != 0:
            if self.cooldown <= 0:
                Lives = self.movement(Lives, speed)
            else:
                self.cooldown -= 1

        #Updating hitbox
        self.rect.top = self.y
        self.rect.bottom = self.y + self.height
        self.rect.left = self.x
        self.rect.right = self.x + self.width
# 每帧调用，绘制怪物，处理移动和状态变化，更新碰撞箱，返回剩余生命值
        
        return Lives
