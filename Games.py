import pygame                    # 用於遊戲的視覺效果和聲音
import random                    # 用於生成隨機位置的石頭和金幣
import cv2                       # 用於開啟攝像頭來捕捉玩家動作
import mediapipe as mp           # 用於肢體追蹤，偵測玩家的肩膀位置
import os                        # 用於文件操作（例如讀取/保存遊戲數據）
import sys
import cvzone
import tkinter as tk
from PIL import Image, ImageTk
from cvzone.HandTrackingModule import HandDetector
from collections import deque
import numpy as np
import time
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv

def start_game_1():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 石頭速度
    dropspeed = grab_game_data(2)

    # 石頭數量
    quantity = grab_game_data(3)

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "躲隕石"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_1_1.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_1.jpg")).convert()
    player_img = pygame.image.load(os.path.join(custom, "Cha_1.png")).convert()
    rock_img = pygame.image.load(os.path.join(custom, "Obj_1_1.png")).convert()
    heart_img = pygame.image.load(os.path.join(custom, "Obj_1_2.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_rock():
        r = Rock()
        all_sprites.add(r)
        rocks.add(r)

    def draw_health(surf, hp, x, y):
        if hp < 0:
            hp = 0
        heart_img.set_colorkey(BLACK)
        heart1 = pygame.transform.scale(heart_img, (WIDTH/10, WIDTH/10))
        heart2 = pygame.transform.scale(heart_img, (WIDTH/10, WIDTH/10))
        heart3 = pygame.transform.scale(heart_img, (WIDTH/10, WIDTH/10))
        if hp == 3:
            screen.blit(heart1, (10, 10))
            screen.blit(heart2, (10+WIDTH/10, 10))
            screen.blit(heart3, (10+WIDTH/5, 10))
        elif hp == 2:
            screen.blit(heart1, (10, 10))
            screen.blit(heart2, (10+WIDTH/10, 10))
        elif hp == 1:
            screen.blit(heart1, (10, 10))
        pygame.display.update()

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '躲隕石', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：身體控制人物左右，躲避隕石', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            width = 300 * (WIDTH / 1280) * cha_size
            height = 180 * (HEIGHT / 800) * cha_size
            self.image = pygame.transform.scale(player_img, (width, height))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 40  * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - height/2
            self.speedx = 8
            self.health = 3

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Rock(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = random.randrange(60, 100) / cha_size
            self.image_ori = pygame.transform.scale(rock_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 3 / cha_size)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-180, -100)
            self.speedy = dropspeed

        def update(self):
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = random.randrange(8, 13)

    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for i in range(quantity):
        new_rock()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Shoulder
                if lmlist[0][0] == 11:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Shoulder
                elif lmlist[0][0] == 12:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    player.rect.x = centerx
        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            rocks = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for i in range(quantity):
                new_rock()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_rock()
            player.health -= 1
            if player.health <= 0:
                game_over = True
                show_init = True

        # DataSave
        if grab_upload_data(2) == 0:
            update_upload_data(2, 60-countdown)
        else:
            if grab_upload_data(2) < 60-countdown:
                update_upload_data(2, 60-countdown)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_health(screen, player.health, 5, 15)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit() 
    cap.release()  # 釋放攝像頭
    cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗

def start_game_2():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 金幣速度
    dropspeed = grab_game_data(4)

    # 金幣數量
    quantity = grab_game_data(5)

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "接金幣"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_2.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_2.jpg")).convert()
    player_img = pygame.image.load(os.path.join(custom, "Cha_2.png")).convert()
    little_coin_img = pygame.image.load(os.path.join(custom, "Obj_2_1.png")).convert()
    silver_coin_img = pygame.image.load(os.path.join(custom, "Obj_2_2.png")).convert()
    big_coin_img = pygame.image.load(os.path.join(custom, "Obj_2_3.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    scoreboard_img = pygame.transform.scale(scoreboard_img,(WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_little_coin():
        c_little = Little_Coin()
        all_sprites.add(c_little)
        little_coins.add(c_little)

    def new_silver_coin():
        c_silver = Silver_Coin()
        all_sprites.add(c_silver)
        silver_coins.add(c_silver)

    def new_big_coin():
        c_big = Big_Coin()
        all_sprites.add(c_big)
        big_coins.add(c_big)


    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '接金幣', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：身體控制人物左右', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            width = 300 * (WIDTH / 1280) * cha_size
            height = 180 * (HEIGHT / 800) * cha_size
            self.image = pygame.transform.scale(player_img, (width, height))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 40  * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - height/2
            self.score = 0


        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Little_Coin(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 80 * (WIDTH / 1280) / cha_size
            self.image_ori = pygame.transform.scale(little_coin_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 4 / cha_size)
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-180, -100)
            self.speedy = dropspeed

        def update(self):
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = dropspeed

    class Silver_Coin(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 90 * (WIDTH / 1280) / cha_size
            self.image_ori = pygame.transform.scale(silver_coin_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 4 / cha_size)
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-180, -100)
            self.speedy = dropspeed

        def update(self):
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = dropspeed

    class Big_Coin(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 100 * (WIDTH / 1280) / cha_size
            self.image_ori = pygame.transform.scale(big_coin_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 4 / cha_size)
            self.rect.x = random.randrange(0, WIDTH-self.rect.width)
            self.rect.y = random.randrange(-180, -100)
            self.speedy = dropspeed

        def update(self):
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = dropspeed

    all_sprites = pygame.sprite.Group()
    little_coins = pygame.sprite.Group()
    silver_coins = pygame.sprite.Group()
    big_coins = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for i in range(quantity):
        new_little_coin()
        new_silver_coin()
        new_big_coin()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Shoulder
                if lmlist[0][0] == 11:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Shoulder
                elif lmlist[0][0] == 12:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    player.rect.x = centerx
        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            little_coins = pygame.sprite.Group()
            silver_coins = pygame.sprite.Group()
            big_coins = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for i in range(quantity):
                new_little_coin()
                new_silver_coin()
                new_big_coin()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(player, little_coins, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_little_coin()
            player.score += 1

        hits = pygame.sprite.spritecollide(player, silver_coins, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_silver_coin()
            player.score += 2

        hits = pygame.sprite.spritecollide(player, big_coins, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_big_coin()
            player.score += 3

        # DataSave
        if grab_upload_data(3) == 0:
            update_upload_data(3, player.score)
        else:
            if grab_upload_data(3) < player.score:
                update_upload_data(3, player.score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        big_coin_img = pygame.transform.scale(big_coin_img,(50,50))
        big_coin_img.set_colorkey(WHITE)
        screen.blit(scoreboard_img, (10, 10))
        draw_text(screen, str(player.score), 90, (10 + WIDTH/10), HEIGHT/25)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()  # 釋放攝像頭
    cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗

def start_game_3():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "挖蘿蔔"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_3.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_3.jpg")).convert()
    radish_img = pygame.image.load(os.path.join(custom, "Obj_3_3.png")).convert()
    shovel_down_img = pygame.image.load(os.path.join(custom, "Cha_3_1.png")).convert()
    empty_hole_img = pygame.image.load(os.path.join(custom, "Obj_3_1.png")).convert()
    full_hole_img = pygame.image.load(os.path.join(custom, "Obj_3_2.png")).convert()
    shovel_up_img = pygame.image.load(os.path.join("Resource/img/普通", "Cha_3_2.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()

    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    empty_hole_img = pygame.transform.scale(empty_hole_img, (WIDTH/6, HEIGHT/6))
    empty_hole_img.set_colorkey(BLACK)
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_full_hole():
        fh = Full_hole()
        all_sprites.add(fh)
        full_hole.add(fh)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '挖蘿蔔', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：身體控制人物左右，蹲下挖蘿蔔', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Shovel(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.width = 150 * (WIDTH / 1280) * cha_size
            self.height = 80 * (HEIGHT / 800) * cha_size
            self.image = pygame.transform.scale(shovel_down_img, (self.width, self.height))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 40 * (WIDTH / 1280) * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            self.score = 0

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Full_hole(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 170
            self.empty = pygame.transform.scale(empty_hole_img, (self.size, self.size))
            self.image = pygame.transform.scale(full_hole_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 2)
            space_between_holes = (WIDTH - (self.size * 4)) / 5
            global hole_1_x, hole_2_x, hole_3_x, hole_4_x
            hole_1_x = space_between_holes
            hole_2_x = hole_1_x + self.size + space_between_holes
            hole_3_x = hole_2_x + self.size + space_between_holes
            hole_4_x = hole_3_x + self.size + space_between_holes
            self.rect.x = random.choice([hole_1_x, hole_2_x, hole_3_x, hole_4_x])
            global chosen
            chosen = self.rect.x
            self.rect.y = HEIGHT * 3 / 5

    class Radish(pygame.sprite.Sprite):
        def __init__(self, center):
            pygame.sprite.Sprite.__init__(self)
            self.size = 65
            self.image = pygame.transform.scale(radish_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.speedy = 20

        def update(self):
            self.rect.y -= self.speedy
            if self.rect.y <= 325:
                self.kill()

    all_sprites = pygame.sprite.Group()
    full_hole = pygame.sprite.Group()
    shovel = Shovel()
    all_sprites.add(shovel)
    new_full_hole()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Shoulder
                if lmlist[0][0] == 11:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Shoulder
                elif lmlist[0][0] == 12:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    shovel.rect.x = centerx
                    shovel.rect.y = centery
        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            full_hole = pygame.sprite.Group()
            shovel = Shovel()
            all_sprites.add(shovel)
            new_full_hole()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(shovel, full_hole, True, pygame.sprite.collide_circle)
        for hit in hits:
            rd = Radish(hit.rect.center)
            all_sprites.add(rd)
            shovel.score += 1
            new_full_hole()

        # DataSave
        if grab_upload_data(4) == 0:
            update_upload_data(4, shovel.score)
        else:
            if grab_upload_data(4) < shovel.score:
                update_upload_data(4, shovel.score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        screen.blit(scoreboard_img, (10, 10))
        draw_text(screen, str(shovel.score), 90, (10 + WIDTH/10), HEIGHT/25)
        # pygame.draw.line(screen, RED, (0, 275), (700, 275),10)
        if chosen == hole_1_x:
            screen.blit(empty_hole_img, (hole_2_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_3_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_4_x, HEIGHT * 3 / 5))
        elif chosen == hole_2_x:
            screen.blit(empty_hole_img, (hole_1_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_3_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_4_x, HEIGHT * 3 / 5))
        elif chosen == hole_3_x:
            screen.blit(empty_hole_img, (hole_2_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_1_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_4_x, HEIGHT * 3 / 5))
        elif chosen == hole_4_x:
            screen.blit(empty_hole_img, (hole_2_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_3_x, HEIGHT * 3 / 5))
            screen.blit(empty_hole_img, (hole_1_x, HEIGHT * 3 / 5))
        pygame.display.update()

    pygame.quit()
    cap.release()  # 釋放攝像頭
    cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗

def start_game_4():
    ### 參數調整 ###
    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    global speed
    speed = 10
    left_leg_raised_time = None
    right_leg_raised_time = None
    left_leg_raised = False  # 記錄左腿是否抬起
    right_leg_raised = False  # 記錄右腿是否抬起

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "追趕跳碰"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_4.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_4.jpg")).convert()
    player_imgs = []
    for i in range(4):
        player_img = pygame.image.load(os.path.join(custom, f"Cha_4_1_{i}.png")).convert()
        player_img.set_colorkey(BLACK)
        player_imgs.append(pygame.transform.scale(player_img, (WIDTH / 5, WIDTH / 5)))
    wolf_imgs = []
    for i in range(4):
        wolf_img = pygame.image.load(os.path.join(custom, f"Cha_4_2_{i}.png")).convert()
        wolf_img.set_colorkey(BLACK)
        wolf_imgs.append(pygame.transform.scale(wolf_img, (WIDTH / 5, WIDTH / 5)))
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '追趕跳碰', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：雙腳保持頻率抬高，與野狼距離越遠', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = player_imgs[0]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH / 6
            self.rect.bottom = HEIGHT * 9 / 10
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 50

        def update(self):
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.frame += 1
                if self.frame == len(player_imgs):
                    self.frame = 0
                else:
                    self.image = player_imgs[self.frame]
                    center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = center

    class Wolf(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = wolf_imgs[0]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH * 4 / 6
            self.rect.bottom = HEIGHT * 9 / 10
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 70

        def update(self):
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.frame += 1
                if self.frame == len(wolf_imgs):
                    self.frame = 0
                else:
                    self.image = wolf_imgs[self.frame]
                    center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = center

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    wolf = Wolf()
    all_sprites.add(wolf)
    speed = 10
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    turn = False
    left_leg_raised_time = None
    right_leg_raised_time = None
    speed = 10
    left_leg_raised = False
    right_leg_raised = False

    try:
        while running:
            countdown_time = pygame.time.get_ticks() - countdown_start_time
            countdown = (60 - int(countdown_time / 1000))

            success, img = cap.read()
            img = cv2.resize(img, (WIDTH, HEIGHT))
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(imgRGB)

            if results.pose_landmarks:
                mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
                
                # 確保 lmlist 在每次迴圈中都被初始化
                lmlist = []
                
                for id, lm in enumerate(results.pose_landmarks.landmark):
                    h, w, c = img.shape
                    bx, by = int(lm.x * w), int(lm.y * h)
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmlist.append([id, cx, cy])  # 收集關鍵點數據
                    
                    # 左膝抬起判斷
                    if id == 25:  # 左膝
                        cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                        y1 = lm.y * h
                        if y1 <= HEIGHT * 3 / 5:  # 假設 y1 <= HEIGHT * 3 / 5 表示抬起
                            if not left_leg_raised:  # 如果左腿之前未抬起
                                left_leg_raised = True
                                left_leg_raised_time = pygame.time.get_ticks()  # 記錄當前時間
                                # print("Left_Knee : ", left_leg_raised_time / 1000)
                        else:
                            left_leg_raised = False  # 如果腳放下，重置狀態
                    
                    # 右膝抬起判斷
                    elif id == 26:  # 右膝
                        cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                        y2 = lm.y * h
                        if y2 <= HEIGHT * 3 / 5:  # 假設 y2 <= HEIGHT * 3 / 5 表示抬起
                            if not right_leg_raised:  # 如果右腿之前未抬起
                                right_leg_raised = True
                                right_leg_raised_time = pygame.time.get_ticks()  # 記錄當前時間
                                # print("Right_Knee : ", right_leg_raised_time / 1000)
                        else:
                            right_leg_raised = False  # 如果腳放下，重置狀態

            cv2.waitKey(1)
            
            if show_init:
                draw_init()
                show_init = False
                game_over = False
                turn = False
                all_sprites = pygame.sprite.Group()
                player = Player()
                all_sprites.add(player)
                wolf = Wolf()
                all_sprites.add(wolf)
                countdown_start_time = pygame.time.get_ticks()

            clock.tick(FPS)

            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # root.mainloop()
            # 更新遊戲
            all_sprites.update()
            if not game_over:
                if countdown <= 0:
                    game_over = True
                    show_init = True
                    # 重置遊戲狀態
                    left_leg_raised_time = None
                    right_leg_raised_time = None
                    left_leg_raised = False
                    right_leg_raised = False
                    speed = 10


            if left_leg_raised_time is not None and right_leg_raised_time is not None:
                time_diff = abs(right_leg_raised_time - left_leg_raised_time) / 1000  # 轉換為秒

                if 3 <= time_diff <= 7:  # 如果時間差在3到7秒之間
                    speed += 1
                    wolf.rect.centerx -= WIDTH / 12
                    print("Speed increased to:", speed)
                elif time_diff < 3:  # 如果間隔時間小於3秒，減速
                    speed -= 1
                    wolf.rect.centerx += WIDTH / 12
                    print("Speed decreased to:", speed)

                # 重置時間記錄，避免重複計算
                left_leg_raised_time = None
                right_leg_raised_time = None

            # 檢查速度範圍
            if speed >= 15 or speed <= 5:
                game_over = True
                show_init = True
                left_leg_raised_time = None
                right_leg_raised_time = None
                left_leg_raised = False
                right_leg_raised = False
                speed = 10

            # DataSave
            if grab_upload_data(5) == 0:
                update_upload_data(5, countdown)
            else:
                if grab_upload_data(5) > countdown:
                    update_upload_data(5, countdown)
            # 畫面顯示
            screen.fill(BLACK)
            screen.blit(background_img, (0, 0))
            all_sprites.draw(screen)
            # draw_text(screen, str(speed), 70, 130, 50)
            screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
            draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
            pygame.display.update()
    finally:
        pygame.quit()
        cap.release()  # 釋放攝像頭
        cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗

def start_game_5():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 蝴蝶數量
    quantity = grab_game_data(6)

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "抓蝴蝶"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_5.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_5.jpg")).convert()
    butterfly_img = pygame.image.load(os.path.join(custom, "Obj_5_3.png")).convert()
    net_1_img = pygame.image.load(os.path.join(custom, "Cha_5_1.png")).convert()
    net_2_img = pygame.image.load(os.path.join(custom, "Cha_5_2.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_butterfly():
        btf = Butterfly()
        all_sprites.add(btf)
        butterflys.add(btf)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '抓蝴蝶', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：左右手控制網子，雙手皆碰觸到蝴蝶即抓到', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Net_1(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(net_1_img, (WIDTH/5* cha_size, WIDTH/7* cha_size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 75 * (WIDTH / 1280) * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Net_2(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(net_2_img, (WIDTH/5* cha_size, WIDTH/7* cha_size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 75 * (WIDTH / 1280) * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Butterfly(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 125 * (WIDTH / 1280) * cha_size
            self.image_ori = pygame.transform.scale(butterfly_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = 125 * (WIDTH / 1280) * cha_size
            self.rect.x = random.randrange(WIDTH * 2 / 8, WIDTH * 6 / 8)
            self.rect.y = random.randrange(HEIGHT * 2 / 8, HEIGHT * 6 / 8)
            self.last = pygame.time.get_ticks()

        def update(self):
            self.now = pygame.time.get_ticks()
            if self.now - self.last > 5000:
                self.kill()
                new_butterfly()

    all_sprites = pygame.sprite.Group()
    butterflys = pygame.sprite.Group()
    net_1 = Net_1()
    all_sprites.add(net_1)
    net_2 = Net_2()
    all_sprites.add(net_2)
    for i in range(quantity):
        new_butterfly()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 17:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 18:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    net_1.rect.x = x1
                    net_1.rect.y = y1

                    net_2.rect.x = x2
                    net_2.rect.y = y2

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            butterflys = pygame.sprite.Group()
            net_1 = Net_1()
            all_sprites.add(net_1)
            net_2 = Net_2()
            all_sprites.add(net_2)
            for i in range(quantity):
                new_butterfly()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(net_1, butterflys, False, pygame.sprite.collide_circle)
        for hit in hits:
            hits = pygame.sprite.spritecollide(net_2, butterflys, True, pygame.sprite.collide_circle)
            for hit in hits:
                score += 1
                global hit_time
                new_butterfly()

        # DataSave
        if grab_upload_data(6) == 0:
            update_upload_data(6, score)
        else:
            if grab_upload_data(6) < score:
                update_upload_data(6, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(scoreboard_img, (10, 10))
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_6():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    ### 參數調整 ###

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    score = 0
    count = 0
    record = 0
    cycle_out = 0
    cycle_in = 0
    up_time = 0
    down_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "鬆土"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_6.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_6.jpg")).convert()
    crop_img = pygame.image.load(os.path.join(custom, "Obj_6_1.png")).convert()
    farmer_0_0_img = pygame.image.load(os.path.join(custom, "Cha_6_0_0.png")).convert()
    farmer_0_1_img = pygame.image.load(os.path.join(custom, "Cha_6_0_1.png")).convert()
    farmer_1_0_img = pygame.image.load(os.path.join(custom, "Cha_6_1_1.png")).convert()
    farmer_1_1_img = pygame.image.load(os.path.join(custom, "Cha_6_1_0.png")).convert()
    farmer_2_0_img = pygame.image.load(os.path.join(custom, "Cha_6_2_0.png")).convert()
    farmer_2_1_img = pygame.image.load(os.path.join(custom, "Cha_6_2_1.png")).convert()
    dirt_img = pygame.image.load(os.path.join(custom, "Obj_6_2.png")).convert()

    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    crop_img = pygame.transform.scale(crop_img, (WIDTH/10, WIDTH/10))
    crop_img.set_colorkey(BLACK)
    farm_imgs = []
    farmer_0_0_img = pygame.transform.scale(farmer_0_0_img, (WIDTH/5, WIDTH/5))
    farmer_0_0_img.set_colorkey(BLACK)
    farmer_0_1_img = pygame.transform.scale(farmer_0_1_img, (WIDTH/5, WIDTH/5))
    farmer_0_1_img.set_colorkey(BLACK)
    farmer_1_0_img = pygame.transform.scale(farmer_1_0_img, (WIDTH/5, WIDTH/5))
    farmer_1_0_img.set_colorkey(BLACK)
    farmer_1_1_img = pygame.transform.scale(farmer_1_1_img, (WIDTH/5, WIDTH/5))
    farmer_1_1_img.set_colorkey(BLACK)
    farmer_2_0_img = pygame.transform.scale(farmer_2_0_img, (WIDTH/5, WIDTH/5))
    farmer_2_0_img.set_colorkey(BLACK)
    farmer_2_1_img = pygame.transform.scale(farmer_2_1_img, (WIDTH/5, WIDTH/5))
    farmer_2_1_img.set_colorkey(BLACK)
    dirt_img = pygame.transform.scale(dirt_img, (WIDTH/10, WIDTH/10))
    dirt_img.set_colorkey(BLACK)
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    farm_imgs.append(farmer_0_1_img)
    farm_imgs.append(farmer_1_1_img)
    farm_imgs.append(farmer_2_1_img)

    farm_pic = {}
    farm_pic['x'] = [WIDTH/10, WIDTH*4/10, WIDTH*7/10]
    farm_pic['y'] = [HEIGHT/15, HEIGHT*5/15, HEIGHT*10/15]

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_crop():
        if count == 0:
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 1:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 2:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 3:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 4:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 5:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 6:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(crop_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 7:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))
        elif count == 8:
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.75, HEIGHT*2/4))
            screen.blit(dirt_img, (WIDTH*0.15, HEIGHT*3/4))
            screen.blit(dirt_img, (WIDTH*0.45, HEIGHT*3/4))
            screen.blit(crop_img, (WIDTH*0.75, HEIGHT*3/4))

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '鬆土', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：重複雙手舉起', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Farmer(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH/5 * cha_size
            self.image = pygame.transform.scale(farm_imgs[cycle_out], (self.size, self.size))
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH/10  # [WIDTH/10, WIDTH*4/10, WIDTH*7/10]
            self.rect.y = HEIGHT/15  # [HEIGHT/15, HEIGHT*5/15, HEIGHT*10/15]
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 50

        def update(self):
            if count == 0:
                self.image = farm_imgs[cycle_out]
                self.rect.x = WIDTH/10
                self.rect.y = HEIGHT/15
            else:
                if count == 1:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*4/10
                    self.rect.y = HEIGHT/15
                    self.frame += 1
                elif count == 2:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*7/10
                    self.rect.y = HEIGHT/15
                    self.frame += 1
                elif count == 3:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH/10
                    self.rect.y = HEIGHT*5/15
                    self.frame += 1
                elif count == 4:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*4/10
                    self.rect.y = HEIGHT*5/15
                    self.frame += 1
                elif count == 5:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*7/10
                    self.rect.y = HEIGHT*5/15
                    self.frame += 1
                elif count == 6:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH/10
                    self.rect.y = HEIGHT*10/15
                    self.frame += 1
                elif count == 7:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*4/10
                    self.rect.y = HEIGHT*10/15
                    self.frame += 1
                elif count == 8:
                    self.image = farm_imgs[cycle_out]
                    self.rect.x = WIDTH*7/10
                    self.rect.y = HEIGHT*10/15
                    self.frame = -1

    all_sprites = pygame.sprite.Group()
    farmer = Farmer()
    all_sprites.add(farmer)
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.line(img, (0, 50), (700, 50), RED, 3)
        cv2.line(img, (0, 250), (700, 250), GREEN, 3)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 15:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 16:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    if y1 < HEIGHT/10 and y2 < HEIGHT/10:
                        if up_time < down_time or up_time == down_time:
                            up_time = pygame.time.get_ticks()
                            if 500 - y1 > record:
                                record = 500 - y1
                            if count < 8:
                                count += 1
                                score += 1
                            elif count == 8:
                                cycle_out += 1
                                count = 0
                                score += 1
                    elif y1 > HEIGHT/2 and y2 > HEIGHT/2 or up_time == down_time:
                        if up_time > down_time:
                            down_time = pygame.time.get_ticks()

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            farmer = Farmer()
            all_sprites.add(farmer)
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        if cycle_out == 2 and count == 8:
            game_over = True
            show_init = True

        # DataSave
        if grab_upload_data(7) == 0:
            update_upload_data(7, score)
        else:
            if grab_upload_data(7) < score:
                update_upload_data(7, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(scoreboard_img, (10, 10))
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        all_sprites.draw(screen)
        new_crop()
        draw_text(screen, str(record), 90, WIDTH / 2, HEIGHT/25)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_7():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    right_time = 0
    left_time = 0
    score = 0
    count = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "踩水車"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_7.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_7.jpg")).convert()
    player_imgs = []
    for i in range(4):
        player_img = pygame.image.load(os.path.join(custom, f"Cha_7_{i}.png")).convert()
        player_img.set_colorkey(BLACK)
        player_size = 350 * cha_size
        player_imgs.append(pygame.transform.scale(player_img, (player_size, player_size)))
    waterwheel_imgs = []
    for i in range(4):
        waterwheel_img = pygame.image.load(os.path.join(custom, f"Obj_7_{i}.png")).convert()
        waterwheel_img.set_colorkey(BLACK)
        waterwheel_size = 300 * cha_size
        waterwheel_imgs.append(pygame.transform.scale(waterwheel_img, (cha_size, cha_size)))
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '踩水車', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：雙腳按照指令踩動，水車就會運作', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = player_imgs[0]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH*0.7
            self.rect.y = HEIGHT/4
            self.last_update = pygame.time.get_ticks()

        def update(self):
            self.image = player_imgs[count]

    class Waterwheel(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = waterwheel_imgs[0]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH/4
            self.rect.y = HEIGHT*0.35
            self.last_update = pygame.time.get_ticks()

        def update(self):
            self.image = waterwheel_imgs[count]

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    waterwheel = Waterwheel()
    all_sprites.add(waterwheel)
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        cv2.line(img, (0, 400), (700, 400), RED, 5)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Knee
                if lmlist[0][0] == 25:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]

                # Right_Knee
                elif lmlist[0][0] == 26:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    if y1 < HEIGHT * 3/5:
                        if left_time < right_time or left_time == right_time:
                            left_time = pygame.time.get_ticks()
                            score += 1
                            if count < 3:
                                count += 1
                            elif count == 3:
                                count = 0
                    elif y2 < HEIGHT * 3/5:
                        if right_time < left_time or left_time == right_time:
                            right_time = pygame.time.get_ticks()
                            score += 1
                            if count < 3:
                                count += 1
                            elif count == 3:
                                count = 0

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            waterwheel = Waterwheel()
            all_sprites.add(waterwheel)
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()

        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        # DataSave
        if grab_upload_data(8) == 0:
            update_upload_data(8, score)
        else:
            if grab_upload_data(8) < score:
                update_upload_data(8, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        screen.blit(scoreboard_img, (10, 10))
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_8():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2
    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    score = 0
    count = 0
    record = 0
    up_time = 0
    down_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "施肥"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_8.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_8.jpg")).convert()
    crop_imgs = []
    for i in range(4):
        crop_img = pygame.image.load(os.path.join(custom, f"Obj_8_{i}.png")).convert()
        crop_img.set_colorkey(BLACK)
        crop_imgs.append(pygame.transform.scale(crop_img, (WIDTH*0.15*cha_size, HEIGHT/4*cha_size)))
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    farm_imgs = []
    for i in range(6):
        farm_img = pygame.image.load(os.path.join("Resource/img/普通", f"Cha_8_{i}.png")).convert()
        farm_img.set_colorkey(BLACK)
        farm_imgs.append(pygame.transform.scale(farm_img, (WIDTH*0.22*cha_size, HEIGHT*0.4*cha_size)))
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '施肥', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：重複雙手舉起', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    def new_crop():
        if count == -1:
            screen.blit(crop_imgs[0], (WIDTH*0.15, HEIGHT*0.2))
        elif count == 2:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
        elif count == 3:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
        elif count == 4:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.2))
        elif count == 5:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.4))
        elif count == 6:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.4))
        elif count == 7:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.4))
        elif count == 8:
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.2))
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.35, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.55, HEIGHT*0.4))
            screen.blit(crop_imgs[3], (WIDTH*0.15, HEIGHT*0.6))

    class Farmer(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.i = 0
            self.frame = 0
            self.image = farm_imgs[self.frame]
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.7
            self.rect.y = HEIGHT * 0.2
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 50

        def update(self):
            if count < self.i:
                self.i = -1
                if count > self.i:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(farm_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = farm_imgs[self.frame]
                            self.rect.x = WIDTH * 0.7
                            self.rect.y = HEIGHT * 0.2
            else:
                if count > self.i:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(farm_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = farm_imgs[self.frame]
                            self.rect.x = WIDTH * 0.7
                            self.rect.y = HEIGHT * 0.2

    class Crop(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.i = 0
            self.frame = 0
            self.image = crop_imgs[0]
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.15
            self.rect.y = HEIGHT * 0.2
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 80

        def update(self):
            if count > self.i:
                if count == 0:
                    self.image = crop_imgs[0]
                    self.rect.x = WIDTH * 0.15
                    self.rect.y = HEIGHT * 0.2
                elif count == 1:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.15
                            self.rect.y = HEIGHT * 0.2
                elif count == 2:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.35
                            self.rect.y = HEIGHT * 0.2
                elif count == 3:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.55
                            self.rect.y = HEIGHT * 0.2
                elif count == 4:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.15
                            self.rect.y = HEIGHT * 0.4
                elif count == 5:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.35
                            self.rect.y = HEIGHT * 0.4
                elif count == 6:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.55
                            self.rect.y = HEIGHT * 0.4
                elif count == 7:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.15
                            self.rect.y = HEIGHT * 0.6
                elif count == 8:
                    now = pygame.time.get_ticks()
                    if now - self.last_update > self.frame_rate:
                        self.last_update = now
                        self.frame += 1
                        if self.frame == len(crop_imgs):
                            self.i += 1
                            self.frame = 0
                        else:
                            self.image = crop_imgs[self.frame]
                            self.rect.x = WIDTH * 0.35
                            self.rect.y = HEIGHT * 0.6
                elif count == 9:
                    self.image = crop_imgs[0]
                    self.rect.x = WIDTH * 0.55
                    self.rect.y = HEIGHT * 0.6
                    crop.i = 0

    all_sprites = pygame.sprite.Group()
    farmer = Farmer()
    all_sprites.add(farmer)
    crop = Crop()
    all_sprites.add(crop)
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.line(img, (0, 50), (700, 50), RED, 3)
        cv2.line(img, (0, 250), (700, 250), GREEN, 3)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 15:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 16:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    if y1 < HEIGHT/10 and y2 < HEIGHT/10:
                        if up_time < down_time or up_time == down_time:
                            up_time = pygame.time.get_ticks()
                            if HEIGHT*9/10 - y1 > record:
                                record = HEIGHT*9/10 - y1
                            if count < 9:
                                count += 1
                                score += 1
                    elif y1 > HEIGHT/2 and y2 > HEIGHT/2 or up_time == down_time:
                        if up_time > down_time:
                            down_time = pygame.time.get_ticks()

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            farmer = Farmer()
            all_sprites.add(farmer)
            crop = Crop()
            all_sprites.add(crop)
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        if count == 9:
            count = 0

        # DataSave
        if grab_upload_data(9) == 0:
            update_upload_data(9, score)
        else:
            if grab_upload_data(9) < score:
                update_upload_data(9, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        draw_text(screen, str(score), 90, WIDTH*0.1, HEIGHT/25)
        all_sprites.draw(screen)
        draw_text(screen, str(record), 90, WIDTH*0.45, HEIGHT/25)
        new_crop()
        draw_text(screen, str(countdown), 90, WIDTH*0.9, HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_9():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    score = 0
    count = 0
    record = 0
    up_time = 0
    down_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "收割"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_9.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_9.jpg")).convert()
    crop_img = pygame.image.load(os.path.join(custom, "Obj_9_0.png")).convert()
    cow_img = pygame.image.load(os.path.join(custom, "Obj_9_1.png")).convert()
    ###
    cow_img = pygame.transform.scale(cow_img, (WIDTH/4*cha_size, HEIGHT/4*cha_size))
    cow_img.set_colorkey(BLACK)
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    crop_img = pygame.transform.scale(crop_img, (WIDTH * 0.15*cha_size, HEIGHT * 3 / 11*cha_size))
    crop_img.set_colorkey(BLACK)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_crop():
        if count == 0:
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 1:
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 2:
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 3 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 3:
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 4:
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 5:
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 5 / 11))
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 6:
            screen.blit(crop_img, (WIDTH*0.2, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 7:
            screen.blit(crop_img, (WIDTH*0.4, HEIGHT * 7 / 11))
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))
        elif count == 8:
            screen.blit(crop_img, (WIDTH*0.6, HEIGHT * 7 / 11))

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '收割', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：重複雙手舉起', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    all_sprites = pygame.sprite.Group()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.line(img, (0, 50), (700, 50), RED, 3)
        cv2.line(img, (0, 250), (700, 250), GREEN, 3)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 15:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 16:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    if y1 < HEIGHT/10 and y2 < HEIGHT/10:
                        if up_time < down_time or up_time == down_time:
                            up_time = pygame.time.get_ticks()
                            if 500 - y1 > record:
                                record = 500 - y1
                            if count < 8:
                                count += 1
                                score += 1
                            elif count == 8:
                                count = 0
                                score += 1
                    elif y1 > HEIGHT/2 and y2 > HEIGHT/2 or up_time == down_time:
                        if up_time > down_time:
                            down_time = pygame.time.get_ticks()

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        # DataSave
        if grab_upload_data(10) == 0:
            update_upload_data(10, score)
        else:
            if grab_upload_data(10) < score:
                update_upload_data(10, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(cow_img, (30, 120))
        draw_text(screen, str(score), 90, WIDTH*0.1, HEIGHT/25)
        draw_text(screen, str(countdown), 90, WIDTH*0.9, HEIGHT/25)
        all_sprites.draw(screen)
        new_crop()
        draw_text(screen, str(record), 90, WIDTH*0.45, HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_10():
    ### 參數調整 ###

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    point = 0


    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "椿米"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_10.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_10.jpg")).convert()
    rice_img = pygame.image.load(os.path.join(custom, "Obj_10_1.png")).convert()
    player_left_img = pygame.image.load(os.path.join(custom, "Cha_10_0.png")).convert()
    player_right_img = pygame.image.load(os.path.join(custom, "Cha_10_1.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    rice_img = pygame.transform.scale(rice_img, (WIDTH*0.075, WIDTH*0.075))
    rice_img.set_colorkey(BLACK)
    player_left_img = pygame.transform.scale(player_left_img, (WIDTH/10, WIDTH/10))
    player_left_img.set_colorkey(BLACK)
    player_right_img = pygame.transform.scale(player_right_img, (WIDTH/10, WIDTH/10))
    player_right_img.set_colorkey(BLACK)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '椿米', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：將腿部抬高再放下', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    def new_rice_left():
        rice = Left_rice()
        all_sprites.add(rice)
        left_rice.add(rice)

    def new_rice_right():
        rice = Right_rice()
        all_sprites.add(rice)
        right_rice.add(rice)

    class Player_left(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = player_left_img
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.15
            self.rect.y = HEIGHT * 0.35

        def update(self):
            if self.rect.y > HEIGHT:
                self.rect.y = HEIGHT
            elif self.rect.y < 0:
                self.rect.y = 0

    class Player_right(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = player_right_img
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.775
            self.rect.y = HEIGHT * 0.35

        def update(self):
            if self.rect.y > HEIGHT:
                self.rect.y = HEIGHT
            elif self.rect.y < 0:
                self.rect.y = 0

    class Left_rice(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = rice_img
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.15
            self.rect.y = HEIGHT * 0.7
            self.last_update = pygame.time.get_ticks()

        def update(self):
            self.now = pygame.time.get_ticks()

    class Right_rice(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = rice_img
            self.rect = self.image.get_rect()
            self.rect.x = WIDTH * 0.8
            self.rect.y = HEIGHT * 0.7
            self.last_update = pygame.time.get_ticks()

        def update(self):
            self.now = pygame.time.get_ticks()

    all_sprites = pygame.sprite.Group()
    player_left = Player_left()
    all_sprites.add(player_left)
    player_right = Player_right()
    all_sprites.add(player_right)
    right_rice = pygame.sprite.Group()
    left_rice = pygame.sprite.Group()
    pygame.mixer.music.play(-1)
    new_rice_right()
    new_rice_left()
    score = 0

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))

        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        cv2.line(img, (0, 400), (700, 400), RED, 5)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Knee
                if lmlist[0][0] == 25:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]

                # Right_Knee
                elif lmlist[0][0] == 26:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    if y2 < HEIGHT * 4 / 5:
                        player_left.rect.y += 10
                    elif y1 < HEIGHT * 4 / 5:
                        player_right.rect.y += 10

                    # player_right.rect.y = HEIGHT - y1
                    # player_left.rect.y = HEIGHT - y2

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            player_left = Player_left()
            all_sprites.add(player_left)
            player_right = Player_right()
            all_sprites.add(player_right)
            right_rice = pygame.sprite.Group()
            left_rice = pygame.sprite.Group()
            new_rice_right()
            new_rice_left()
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()

        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        # now_time = pygame.time.get_ticks()

        hits = pygame.sprite.spritecollide(player_left, left_rice, True, pygame.sprite.collide_circle)
        for hit in hits:
            point += 1
            player_left.rect.y = HEIGHT * 0.35
            new_rice_right()
            player_right.rect.y = HEIGHT * 0.35

        hits = pygame.sprite.spritecollide(player_right, right_rice, True, pygame.sprite.collide_circle)
        for hit in hits:
            point += 1
            player_right.rect.y = HEIGHT * 0.35
            new_rice_left()
            player_left.rect.y = HEIGHT * 0.35

        # DataSave
        if grab_upload_data(11) == 0:
            update_upload_data(11, point)
        else:
            if grab_upload_data(11) < point:
                update_upload_data(11, point)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, str(point), 90, WIDTH*0.15, HEIGHT/25)
        draw_text(screen, str(countdown), 90, WIDTH*0.9, HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_11():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    score = 0
    t = 0
    puncturetime = grab_game_data(7) * 1000

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "刺氣球"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_11.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_11.jpg")).convert()
    thumbtack_img = pygame.image.load(os.path.join(custom, "Cha_11.png")).convert()
    balloon_img = pygame.image.load(os.path.join(custom, "Obj_11.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_sec(surf, sec, x, y):
        BAR_LENGTH = WIDTH/2
        BAR_HEIGHT = 50
        fill = ((puncturetime - sec) / puncturetime) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surf, GREEN, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

    def new_balloon():
        bln = Balloon()
        all_sprites.add(bln)
        balloons.add(bln)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '刺氣球', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：用雙手刺向氣球，維持三秒即可刺破', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Thumbtack(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 100 * (WIDTH / 1280) * cha_size
            self.image = pygame.transform.scale(thumbtack_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = 75 * (WIDTH / 1280) * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Balloon(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = 125 * (WIDTH / 1280) * cha_size
            self.image_ori = pygame.transform.scale(balloon_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = 100 * (WIDTH / 1280) * cha_size
            self.rect.x = random.randrange(100, WIDTH - 100)
            self.rect.y = random.randrange(150, HEIGHT*3/4)
            self.last = pygame.time.get_ticks()

        def update(self):
            self.now = pygame.time.get_ticks()
            if self.now - self.last > 15000:
                self.kill()
                new_balloon()

    all_sprites = pygame.sprite.Group()
    thumbtack = Thumbtack()
    all_sprites.add(thumbtack)
    balloons = pygame.sprite.Group()
    new_balloon()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        now = pygame.time.get_ticks()
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 17:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 18:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    thumbtack.rect.centerx = x1
                    thumbtack.rect.centery = y1

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            thumbtack = Thumbtack()
            all_sprites.add(thumbtack)
            balloons = pygame.sprite.Group()
            new_balloon()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        hits = pygame.sprite.spritecollide(thumbtack, balloons, False, pygame.sprite.collide_circle)
        for hit in hits:
            hit_time = pygame.time.get_ticks()
            m = hit_time - now
            t += m
            print(t)
            if t > puncturetime:
                hits = pygame.sprite.spritecollide(thumbtack, balloons, True, pygame.sprite.collide_circle)
                for hit in hits:
                    t = 0
                    score += 1
                    new_balloon()

        # DataSave
        if grab_upload_data(12) == 0:
            update_upload_data(12, score)
        else:
            if grab_upload_data(12) < score:
                update_upload_data(12, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(scoreboard_img, (10, 10))
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        all_sprites.draw(screen)
        draw_sec(screen, t, WIDTH/4, 50)
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_12():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "接雞蛋"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_12.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_12.jpg")).convert()
    player_img = pygame.image.load(os.path.join(custom, "Cha_12.png")).convert()
    egg_img = pygame.image.load(os.path.join(custom, "Obj_12.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_egg():
        e = Egg()
        all_sprites.add(e)
        eggs.add(e)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '接雞蛋', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：骨盆控制人物左右', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH/5 * cha_size
            self.image = pygame.transform.scale(player_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH/40 * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT / 2 + 100

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Egg(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH/10 * cha_size
            self.image_ori = pygame.transform.scale(egg_img, (self.size, self.size))
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 2 * cha_size)
            self.rect.centerx = random.choice([WIDTH/6, WIDTH*2/6, WIDTH*3/6, WIDTH*4/6, WIDTH*5/6])
            self.rect.centery = HEIGHT / 2 + 100

        def update(self):
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.choice([WIDTH/6, WIDTH*2/6, WIDTH*3/6, WIDTH*4/6, WIDTH*5/6])
                self.rect.y = HEIGHT / 2 + 100

    all_sprites = pygame.sprite.Group()
    eggs = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    new_egg()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Hip
                if lmlist[0][0] == 23:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Hip
                elif lmlist[0][0] == 24:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    player.rect.x = WIDTH/3 + ((centerx - WIDTH/3) * 5)

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            eggs = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            new_egg()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(player, eggs, True, pygame.sprite.collide_circle)
        for hit in hits:
            score += 1
            new_egg()

        # DataSave
        if grab_upload_data(13) == 0:
            update_upload_data(13, score)
        else:
            if grab_upload_data(13) < score:
                update_upload_data(13, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(scoreboard_img, (10, 10))
        all_sprites.draw(screen)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_13():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 果子速度
    dropspeed = grab_game_data(8)

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    count = 0
    score = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "接果子"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_13.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_13.jpg")).convert()
    fruit_imgs = []
    for i in range(5):
        fruit_img = pygame.image.load(os.path.join(custom, f"Obj_13_{i}.png"))
        fruit_img.set_colorkey(BLACK)
        fruit_imgs.append(fruit_img)
    player_img = pygame.image.load(os.path.join(custom, "Cha_13.png")).convert()
    greendot_img = pygame.image.load(os.path.join("Resource/img/普通", "Greendot.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '接果子', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：身體站橫向，手臂伸縮控制籃子', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop(),
                elif event.type == pygame.KEYUP:
                    waiting = False

    def new_fruit():
        f = Fruit()
        all_sprites.add(f)
        fruits.add(f)

    def greendot():
        g = Greendot()
        all_sprites.add(g)
        greendots.add(g)

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH/4 * cha_size
            self.image = pygame.transform.scale(player_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 20 * cha_size
            self.rect.x = WIDTH / 2
            self.rect.y = HEIGHT * 0.6

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Fruit(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH / 10 * cha_size
            self.i = random.randrange(0, 5)
            self.image = pygame.transform.scale(fruit_imgs[self.i], (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 20 * cha_size
            self.rect.x = WIDTH * 0.85
            self.rect.y = 50
            self.speedy = dropspeed

        def update(self):
            self.rect.y += self.speedy
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.kill()
                new_fruit()

    class Greendot(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH / 10
            self.image = pygame.transform.scale(greendot_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 50
            self.rect.x = WIDTH / 7
            self.rect.y = HEIGHT * 0.75

    all_sprites = pygame.sprite.Group()
    fruits = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    greendots = pygame.sprite.Group()
    greendot()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 17:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 18:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    player.rect.x = centerx
        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            fruits = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            greendots = pygame.sprite.Group()
            greendot()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        hits = pygame.sprite.spritecollide(player, fruits, True, pygame.sprite.collide_circle)
        for hit in hits:
            if count % 2 == 1:
                count += 1
                score += 1

        hits = pygame.sprite.spritecollide(player, greendots, False, pygame.sprite.collide_circle)
        for hit in hits:
            if count % 2 == 0:
                count += 1
                new_fruit()

        # DataSave
        if grab_upload_data(14) == 0:
            update_upload_data(14, score)
        else:
            if grab_upload_data(14) < score:
                update_upload_data(14, score)
        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(scoreboard_img, (10, 10))
        all_sprites.draw(screen)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_14():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    right_time = 0
    left_time = 0
    score = 0
    count = 0
    b = 0

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "踩氣球"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    p = [WIDTH * 0.6, WIDTH * 0.4]

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_7.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_14.jpg")).convert()
    balloon_img = pygame.image.load(os.path.join(custom, f"Obj_14.png")).convert()
    player_imgs = []
    for i in range(4):
        player_img = pygame.image.load(os.path.join(custom, f"Cha_14_{i}.png")).convert()
        player_img.set_colorkey(BLACK)
        player_imgs.append(pygame.transform.scale(player_img, (WIDTH * 0.4, HEIGHT * 0.6)))
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_balloon():
        b = Balloon()
        all_sprites.add(b)
        balloons.add(b)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '踩氣球', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：抬起氣球所在的腳，若身體傾斜幅度過大，人物傾斜', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = player_imgs[count]
            self.rect = self.image.get_rect()
            self.rect.centerx = WIDTH / 2
            self.rect.y = WIDTH / 10
            self.last_update = pygame.time.get_ticks()

        def update(self):
            self.image = player_imgs[count]

    class Balloon(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH / 10 * cha_size
            self.image = balloon_img
            self.image = pygame.transform.scale(balloon_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.centerx = p[b]
            self.rect.y = HEIGHT * 8 / 11
            self.last_update = pygame.time.get_ticks()

        def update(self):
            if y1 < HEIGHT * 3/5 or y2 < HEIGHT * 3/5:
                self.kill()
                new_balloon()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    balloons = pygame.sprite.Group()
    balloon = Balloon()
    new_balloon()
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        cv2.line(img, (0, 400), (700, 400), RED, 5)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Knee
                if lmlist[0][0] == 25:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]

                # Right_Knee
                elif lmlist[0][0] == 26:
                    cv2.circle(img, (bx, by), 15, WHITE, cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                #  Left_Shoulder
                elif lmlist[0][0] == 11:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x3 = lmlist[0][1]
                    y3 = lmlist[0][2]

                # Right_Shoulder
                elif lmlist[0][0] == 12:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x4 = lmlist[0][1]
                    y4 = lmlist[0][2]

                # Left_Hip
                elif lmlist[0][0] == 23:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x5 = lmlist[0][1]
                    y5 = lmlist[0][2]

                # Right_Hip
                elif lmlist[0][0] == 24:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x6 = lmlist[0][1]
                    y6 = lmlist[0][2]

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            balloons = pygame.sprite.Group()
            balloon = Balloon()
            new_balloon()
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()

        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True
        if y2 <  HEIGHT * 3/5:
            if left_time < right_time or left_time == right_time:
                left_time = pygame.time.get_ticks()
                if b == 0:
                    b = 1
                else:
                    b = 0
                if (x4 - x6) < 50:
                    if count < 1:
                        count = 1
                        score += 1
                    else:
                        count = 0
                        score += 1
                else:
                    count = 2
        elif y1 <  HEIGHT * 3/5:
            if right_time < left_time or left_time == right_time:
                right_time = pygame.time.get_ticks()
                if b == 0:
                    b = 1
                else:
                    b = 0
                if (x5 - x3) < 50:
                    if count < 1:
                        count = 1
                        score += 1
                    else:
                        count = 0
                        score += 1
                else:
                    count = 3

        # DataSave
        if grab_upload_data(15) == 0:
            update_upload_data(15, score)
        else:
            if grab_upload_data(15) < score:
                update_upload_data(15, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        screen.blit(scoreboard_img, (10, 10))
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_15():
    ### 參數調整 ###

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    score = 0
    chosen = random.choice([0, 1, 2, 3, 4, 5, 6, 7])

    # 圖片更換
    style = grab_game_data(1)
    if style == 0 or style == None:
        custom = "Resource/img/普通"
    elif style == 1:
        custom = "Resource/img/特別"
    elif style == 2:
        custom = "Resource/img/草地"
    elif style == 3:
        custom = "Resource/img/夜空"
    elif style == 4:
        custom = "Resource/img/岩壁"
    elif style == 5:
        custom = "Resource/img/海洋"

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "跳舞機"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 讀取樣式
    # 載入音樂
    pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_15.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join(custom, "Bg_15.jpg")).convert()
    footprint_img = pygame.image.load(os.path.join(custom, "Cha_15.png")).convert()
    blue_arrows = []
    for i in range(8):
        blue_img = pygame.image.load(os.path.join(custom, f"Obj_15_0_{i}.png")).convert()
        blue_img.set_colorkey(BLACK)
        blue_arrows.append(pygame.transform.scale(blue_img, (WIDTH* 0.125, WIDTH* 0.125)))
    red_arrows = []
    for i in range(8):
        red_img = pygame.image.load(os.path.join(custom, f"Obj_15_1_{i}.png")).convert()
        red_img.set_colorkey(BLACK)
        red_arrows.append(pygame.transform.scale(red_img, (WIDTH* 0.125, WIDTH* 0.125)))
    ###
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    greendot_img = pygame.image.load(os.path.join("Resource/img/普通", "Greendot.png")).convert()
    scoreboard_img = pygame.image.load(os.path.join("Resource/img/普通", "scoreboard.png")).convert()
    scoreboard_img = pygame.transform.scale(scoreboard_img, (WIDTH/5, HEIGHT/6))
    scoreboard_img.set_colorkey(WHITE)
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)
    font_name = os.path.join("Resource/font.ttf")

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, RED)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_arrow_0():
        a = Arrow_0()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_1():
        a = Arrow_1()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_2():
        a = Arrow_2()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_3():
        a = Arrow_3()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_4():
        a = Arrow_4()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_5():
        a = Arrow_5()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_6():
        a = Arrow_6()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_arrow_7():
        a = Arrow_7()
        all_sprites.add(a)
        arrow_0.add(a)

    def new_Center():
        c = Center()
        all_sprites.add(c)
        center.add(c)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '跳舞機', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：雙手指向紅色箭頭方向，再回到中心點，會出現下一個', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Hand(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH * 0.15
            self.image = pygame.transform.scale(footprint_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = self.size / 5
            self.rect.x = WIDTH / 2
            self.rect.y = HEIGHT / 2

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

    class Center(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.size = WIDTH * 0.125
            self.image = pygame.transform.scale(greendot_img, (self.size, self.size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = self.size / 5
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT / 2

    class Arrow_0(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[0], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 20
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT * 1 / 5
        # def update(self):

    class Arrow_1(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[1], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 20
            self.rect.centerx = WIDTH * 3 / 4
            self.rect.centery = HEIGHT * 1 / 5
        # def update(self):

    class Arrow_2(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[2], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH / 20
            self.rect.centerx = WIDTH * 3 / 4
            self.rect.centery = HEIGHT * 0.5
        # def update(self):

    class Arrow_3(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[3], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = HEIGHT  / 2
            self.rect.centerx = WIDTH * 3 / 4
            self.rect.centery = HEIGHT * 4 / 5
        # def update(self):

    class Arrow_4(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[4], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = HEIGHT  / 2
            self.rect.centerx = WIDTH / 2
            self.rect.centery = HEIGHT * 4 / 5
        # def update(self):

    class Arrow_5(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[5], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = HEIGHT  / 2
            self.rect.centerx = WIDTH / 4
            self.rect.centery = HEIGHT * 4 / 5
        # def update(self):

    class Arrow_6(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(blue_arrows[6], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = HEIGHT  / 2
            self.rect.centerx = WIDTH / 4
            self.rect.centery = HEIGHT * 0.5
        # def update(self):

    class Arrow_7(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.num = 7
            self.image = pygame.transform.scale(blue_arrows[7], (WIDTH * 0.125, WIDTH * 0.125))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = HEIGHT  / 2
            self.rect.centerx = WIDTH / 4
            self.rect.centery = HEIGHT * 1 / 5
        # def update(self):

    all_sprites = pygame.sprite.Group()
    hand = Hand()
    all_sprites.add(hand)
    center = pygame.sprite.Group()
    new_Center()
    arrow_0 = Arrow_0()
    all_sprites.add(arrow_0)
    arrow_1 = Arrow_1()
    all_sprites.add(arrow_1)
    arrow_2 = Arrow_2()
    all_sprites.add(arrow_2)
    arrow_3 = Arrow_3()
    all_sprites.add(arrow_3)
    arrow_4 = Arrow_4()
    all_sprites.add(arrow_4)
    arrow_5 = Arrow_5()
    all_sprites.add(arrow_5)
    arrow_6 = Arrow_6()
    all_sprites.add(arrow_6)
    arrow_7 = Arrow_7()
    all_sprites.add(arrow_7)
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))

        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        # cv2.line(img, (0, 225), (1280, 225), RED, 3)
        # cv2.line(img, (0, 475), (1280, 475), RED, 3)
        # cv2.line(img, (360, 0), (360, 700), RED, 3)
        # cv2.line(img, (840, 0), (840, 700), RED, 3)
        # cv2.circle(img, (110, 160), 50, GREEN, 3)
        # cv2.circle(img, (110, 380), 50, GREEN, 3)
        # cv2.circle(img, (110, 600), 50, GREEN, 3)
        # cv2.circle(img, (640, 130), 50, GREEN, 3)
        # cv2.circle(img, (640, 380), 50, GREEN, 3)
        # cv2.circle(img, (640, 600), 50, GREEN, 3)
        # cv2.circle(img, (1170, 160), 50, GREEN, 3)
        # cv2.circle(img, (1170, 380), 50, GREEN, 3)
        # cv2.circle(img, (1170, 600), 50, GREEN, 3)

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Wrist
                if lmlist[0][0] == 17:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Wrist
                elif lmlist[0][0] == 18:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

                    hand.rect.x = x1
                    hand.rect.y = y1

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            hand = Hand()
            all_sprites.add(hand)
            center = pygame.sprite.Group()
            new_Center()
            arrow_0 = Arrow_0()
            all_sprites.add(arrow_0)
            arrow_1 = Arrow_1()
            all_sprites.add(arrow_1)
            arrow_2 = Arrow_2()
            all_sprites.add(arrow_2)
            arrow_3 = Arrow_3()
            all_sprites.add(arrow_3)
            arrow_4 = Arrow_4()
            all_sprites.add(arrow_4)
            arrow_5 = Arrow_5()
            all_sprites.add(arrow_5)
            arrow_6 = Arrow_6()
            all_sprites.add(arrow_6)
            arrow_7 = Arrow_7()
            all_sprites.add(arrow_7)
            countdown_start_time = pygame.time.get_ticks()
        clock.tick(FPS)

        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        if chosen == 0:
            arrow_0.image = red_arrows[0]
        elif chosen == 1:
            arrow_1.image = red_arrows[1]
        elif chosen == 2:
            arrow_2.image = red_arrows[2]
        elif chosen == 3:
            arrow_3.image = red_arrows[3]
        elif chosen == 4:
            arrow_4.image = red_arrows[4]
        elif chosen == 5:
            arrow_5.image = red_arrows[5]
        elif chosen == 6:
            arrow_6.image = red_arrows[6]
        elif chosen == 7:
            arrow_7.image = red_arrows[7]

        if hand.rect.x < WIDTH * 0.35:
            if hand.rect.y < HEIGHT * 0.3:
                if chosen == 7:
                    arrow_7.image = blue_arrows[7]
                    score += 1
                    chosen = 8
            elif hand.rect.y > HEIGHT * 0.3 and hand.rect.y < HEIGHT * 0.7:
                if chosen == 6:
                    arrow_6.image = blue_arrows[6]
                    score += 1
                    chosen = 8
            elif hand.rect.y > HEIGHT * 0.7:
                if chosen == 5:
                    arrow_5.image = blue_arrows[5]
                    score += 1
                    chosen = 8
        elif hand.rect.x > WIDTH * 0.35 and hand.rect.x < WIDTH * 0.65:
            if hand.rect.y < HEIGHT * 0.3:
                if chosen == 0:
                    arrow_0.image = blue_arrows[0]
                    score += 1
                    chosen = 8
            elif hand.rect.y > HEIGHT * 0.7:
                if chosen == 4:
                    arrow_4.image = blue_arrows[4]
                    score += 1
                    chosen = 8
        elif hand.rect.x > WIDTH * 0.65:
            if hand.rect.y < HEIGHT * 0.3:
                if chosen == 1:
                    arrow_1.image = blue_arrows[1]
                    score += 1
                    chosen = 8
            elif hand.rect.y > HEIGHT * 0.3 and hand.rect.y < HEIGHT * 0.7:
                if chosen == 2:
                    arrow_2.image = blue_arrows[2]
                    score += 1
                    chosen = 8
            elif hand.rect.y > HEIGHT * 0.7:
                if chosen == 3:
                    arrow_3.image = blue_arrows[3]
                    score += 1
                    chosen = 8

        hits = pygame.sprite.spritecollide(hand, center, False, pygame.sprite.collide_circle)
        for hit in hits:
            if chosen == 8:
                chosen = random.choice([0, 1, 2, 3, 4, 5, 6, 7])

        # DataSave
        if grab_upload_data(16) == 0:
            update_upload_data(16, score)
        else:
            if grab_upload_data(16) < score:
                update_upload_data(16, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        screen.blit(scoreboard_img, (10, 10))
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_16():
    ### 參數調整 ###
    # 人物大小
    cha_size = grab_game_data(12) / 2

    # 基礎參數設定
    FPS = 60
    countdown_start_time = 0
    count = 0
    score = 0

    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()

    cap = cv2.VideoCapture(0)

    GameName = "戰鬥機"

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)

    # 遊戲初始化＆視窗大小設定
    pygame.init()
    info = pygame.display.Info()
    WIDTH = info.current_w
    HEIGHT = info.current_h
    SCR = (WIDTH, HEIGHT*0.95)
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCR)
    pygame.display.set_caption(GameName)
    clock = pygame.time.Clock()

    # 載入音樂
    shoot_sound = pygame.mixer.Sound(os.path.join("Resource/sound", "shoot.wav"))
    expl_sounds = [
        pygame.mixer.Sound(os.path.join("Resource/sound", "expl0.wav")),
        pygame.mixer.Sound(os.path.join("Resource/sound", "expl1.wav"))
    ]
    pygame.mixer.music.load(os.path.join("Resource/sound", "background.ogg"))
    pygame.mixer.music.set_volume(0.7)

    # 載入圖片
    background_img = pygame.image.load(os.path.join("Resource/img/普通", "background.png")).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    # background_img = pygame.image.load(os.path.join(custom, "1-1.jpg")).convert()
    player_img = pygame.image.load(os.path.join("Resource/img/普通", "player.png")).convert()
    bullet_img = pygame.image.load(os.path.join("Resource/img/普通", "bullet.png")).convert()
    rock_imgs = []
    for i in range(7):
        rock_imgs.append(pygame.image.load(os.path.join("Resource/img/普通", f"rock{i}.png")).convert())
    font_name = os.path.join("Resource/font.ttf")
    expl_anim = {}
    expl_anim['lg'] = []
    expl_anim['sm'] = []
    for i in range(9):
        expl_img = pygame.image.load(os.path.join("Resource/img/普通", f"expl{i}.png")).convert()
        expl_img.set_colorkey(BLACK)
        expl_anim['lg'].append(pygame.transform.scale(expl_img, (WIDTH * 0.15, WIDTH * 0.15)))
        expl_anim['sm'].append(pygame.transform.scale(expl_img, (WIDTH * 0.08, WIDTH * 0.08)))
    timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()
    timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH/5, HEIGHT/6))
    timeboard_img.set_colorkey(WHITE)

    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        surf.blit(text_surface, text_rect)

    def new_rock():
        r = Rock()
        all_sprites.add(r)
        rocks.add(r)

    def draw_health(surf, hp, x, y):
        if hp < 0:
            hp = 0
        BAR_LENGTH = 300
        BAR_HEIGHT = 30
        fill = (hp / 100) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surf, GREEN, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

    def draw_init():
        screen.blit(background_img, (0, 0))
        draw_text(screen, '戰鬥機', 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, '操作說明：身體控制飛船，舉手發射子彈', 22, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, '按Enter鍵開始遊戲', 22, WIDTH / 2, HEIGHT * 3 / 4)
        pygame.display.update()
        waiting = True
        while waiting:
            clock.tick(FPS)
            # 取得輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # root.mainloop()
                elif event.type == pygame.KEYUP:
                    waiting = False

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.transform.scale(player_img, (WIDTH * 0.1 * cha_size, HEIGHT * 0.15 * cha_size))
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.radius = WIDTH*0.02 * cha_size
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 100
            self.speedx = 8
            self.health = 100
            self.last_shot = pygame.time.get_ticks()  # 記錄上一次射擊的時間
            self.shoot_delay = 500  # 設定射擊延遲（以毫秒為單位）

        def update(self):
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0

        def shoot(self):
            # 檢查是否已經過了射擊延遲時間
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()


    class Rock(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image_ori = random.choice(rock_imgs)
            self.image_ori.set_colorkey(BLACK)
            self.image = self.image_ori.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * 0.85 / 2)
            # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-180, -100)
            self.speedy = random.randrange(8, 13)
            self.speedx = random.randrange(-3, 3)
            self.total_degree = 0
            self.rot_degree = random.randrange(-3, 3)

        def rotate(self):
            self.total_degree += self.rot_degree
            self.total_degree = self.total_degree % 360
            self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        def update(self):
            self.rotate()
            self.rect.y += self.speedy
            self.rect.x += self.speedx
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.rect.x = random.randrange(0, WIDTH - self.rect.width)
                self.rect.y = random.randrange(-100, -40)
                self.speedy = random.randrange(8, 13)
                self.speedx = random.randrange(-3, 3)

    class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.image = bullet_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.bottom = y
            self.speedy = -10

        def update(self):
            self.rect.y += self.speedy
            if self.rect.bottom < 0:
                self.kill()

    class Explosion(pygame.sprite.Sprite):
        def __init__(self, center, size):
            pygame.sprite.Sprite.__init__(self)
            self.size = size
            self.image = expl_anim[self.size][0]
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.frame = 0
            self.last_update = pygame.time.get_ticks()
            self.frame_rate = 30

        def update(self):
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.frame += 1
                if self.frame == len(expl_anim[self.size]):
                    self.kill()
                else:
                    self.image = expl_anim[self.size][self.frame]
                    center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = center

    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for i in range(10):
        new_rock()
    score = 0
    pygame.mixer.music.play(-1)

    # 遊戲迴圈
    show_init = True
    running = True
    game_over = False
    while running:
        countdown_time = pygame.time.get_ticks() - countdown_start_time
        countdown = (60 - int(countdown_time / 1000))
        success, img = cap.read()
        img = cv2.resize(img, (WIDTH, HEIGHT))
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Shoulder
                if lmlist[0][0] == 11:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Shoulder
                elif lmlist[0][0] == 12:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]
                # Left_Thumb
                elif lmlist[0][0] == 21:
                    cv2.circle(img, (bx, by), 15, (255, 255, 0), cv2.FILLED)
                    x3 = lmlist[0][1]
                    y3 = lmlist[0][2]
                # Right_Thumb
                elif lmlist[0][0] == 22:
                    cv2.circle(img, (bx, by), 15, (255, 255, 0), cv2.FILLED)
                    x4 = lmlist[0][1]
                    y4 = lmlist[0][2]

                    centerx = int((x1 + x2) / 2)
                    centery = int((y1 + y2) / 2)
                    cv2.circle(img, (centerx, centery), 15, (0, 255, 255), cv2.FILLED)
                    # print(centerx, centery)
                    player.rect.x = centerx
                    if y3 < centery or y4 < centery:
                        up_time = pygame.time.get_ticks()
                        player.shoot()

        # cv2.imshow("webcam", img)
        cv2.waitKey(1)
        if show_init:
            draw_init()
            show_init = False
            game_over = False
            all_sprites = pygame.sprite.Group()
            rocks = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for i in range(8):
                new_rock()
            score = 0
            countdown_start_time = pygame.time.get_ticks()

        clock.tick(FPS)
        # 取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # root.mainloop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()
        # 更新遊戲
        all_sprites.update()
        if not game_over:
            # 檢查倒數是否結束
            if countdown <= 0:
                game_over = True  # 標記遊戲結束
                show_init = True

        hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
        for hit in hits:
            random.choice(expl_sounds).play()
            score += hit.radius
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            new_rock()

        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            new_rock()
            player.health -= hit.radius
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            if player.health <= 0:
                game_over = True
                show_init = True

        # DataSave
        if grab_upload_data(17) == 0:
            update_upload_data(17, score)
        else:
            if grab_upload_data(17) < score:
                update_upload_data(17, score)

        # 畫面顯示
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        screen.blit(timeboard_img, (WIDTH - (10 + WIDTH/5), 10))
        all_sprites.draw(screen)
        draw_text(screen, str(countdown), 90, WIDTH - (10 + WIDTH/10), HEIGHT/25)
        draw_text(screen, str(score), 90, (10 + WIDTH/10), HEIGHT/25)
        draw_health(screen, player.health, WIDTH/2-150, 35)
        pygame.display.update()

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

def start_game_17():
    root = tk.Tk()
    root.withdraw()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    def start_screen():
        """顯示開始畫面並等待按下「Enter」鍵以開始遊戲。"""
        imgStart = cv2.imread("Resource/img/newgame/Background.png")
        imgStart = cv2.resize(imgStart, (screen_width, screen_height))
        if imgStart is None:
            print("Error: 無法載入開始畫面圖片。請檢查圖片路徑。")
            return

        while True:
            # 顯示開始畫面
            cv2.putText(imgStart, "Press 'Enter' to Start", (int(screen_width/4), int(screen_height/2)), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
            cv2.imshow("tabletennis", imgStart)
            key = cv2.waitKey(1)
            if key == 13:  # Enter鍵開始遊戲
                break
        cv2.destroyWindow("tabletennis")

    start_screen()  # 首次顯示開始畫面

    ### 遊戲參數 ###
    x = grab_game_data(9)
    y = grab_game_data(10)

    cap = cv2.VideoCapture(0)
    cap.set(3, screen_width)#1280
    cap.set(4, screen_height)#720

    # 加載圖片
    imgBackground = cv2.imread("Resource/img/newgame/Background.png")
    imgGameOver = cv2.imread("Resource/img/newgame/gameOver.png")
    imgBall = cv2.imread("Resource/img/newgame/Ball.png", cv2.IMREAD_UNCHANGED)
    bat1_height = 300
    bat2_height = 300
    imgBat1 = cv2.resize(cv2.imread("Resource/img/newgame/bat1.png", cv2.IMREAD_UNCHANGED), (50, bat1_height))
    imgBat2 = cv2.resize(cv2.imread("Resource/img/newgame/bat2.png", cv2.IMREAD_UNCHANGED), (50, bat2_height))

    font_name = os.path.join("Resource/font.ttf")

    # 手部偵測器
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    # 遊戲變數
    ballPos = [100, 100]
    speedX = x
    speedY = y
    gameOver = False
    score = [0, 0]

    while True:

        _, img = cap.read()
        img = cv2.flip(img, 1)
        imgRaw = img.copy()

        # 偵測手部及其位置
        hands, img = detector.findHands(img, flipType=False)

        # 調整並融合背景
        imgBackground = cv2.resize(imgBackground, (img.shape[1], img.shape[0]))
        if len(img.shape) == 3 and len(imgBackground.shape) == 2:
            imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_GRAY2BGR)
        elif len(img.shape) == 2 and len(imgBackground.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

        speedX = np.clip(speedX, -15, 15)
        speedY = np.clip(speedY, -15, 15)

        # 偵測手部並疊加球拍
        if hands:
            for hand in hands:
                x, y, w, h = hand['bbox']
                h1, w1, _ = imgBat1.shape
                y1 = y - bat1_height // 2
                y1 = np.clip(y1, 20, screen_height - bat1_height - 20)

                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgBat1, (int(screen_width * 0.046875), y1))
                    if screen_width * 0.046875 < ballPos[0] < screen_width * 0.046875 + 50 and y1 < ballPos[1] < y1 + bat1_height:
                        speedX = -speedX
                        ballPos[0] += 30
                        score[0] += 1

                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgBat2, (int(screen_width * 0.9336), y1))
                    if screen_width * 0.9336 - 50 < ballPos[0] < screen_width * 0.9336 and y1 < ballPos[1] < y1 + bat2_height:
                        speedX = -speedX
                        ballPos[0] -= 30
                        score[1] += 1


        # 遊戲結束條件
        if ballPos[0] < screen_width * 0.03125 or ballPos[0] > screen_width * 0.9375:
            gameOver = True

        if gameOver:
            img = imgGameOver
            cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)
            cv2.putText(img, "Press 'Enter' to Restart", (300, 500), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)

        else:
            # 球移動
            if ballPos[1] >= screen_height * 0.7 or ballPos[1] <= 10:
                speedY = -speedY

            ballPos[0] += speedX
            ballPos[1] += speedY

            # 繪製球
            img = cvzone.overlayPNG(img, imgBall, ballPos)

            # 顯示分數
            cv2.putText(img, str(score[0]), (int(screen_width/4), 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
            cv2.putText(img, str(score[1]), (int(screen_width*3/4), 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

            # 更新分數數據
            point = score[0]+score[1]
            if grab_upload_data(18) == 0 or grab_upload_data(18) < point:
                update_upload_data(18, point)

        cv2.imshow("tabletennis", img)
        key = cv2.waitKey(1)

        if key == 13 and gameOver:  # Enter鍵重新開始
            # 重設遊戲
            ballPos = [100, 100]
            speedX = x
            speedY = y
            gameOver = False
            score = [0, 0]
            imgGameOver = cv2.imread("Resource/img/newgame/gameOver.png")
            start_screen()  # 顯示開始畫面重新開始

        elif key == ord(' '):  # 空白鍵退出
            break

    cap.release()
    cv2.destroyAllWindows()

def start_game_18():
    root = tk.Tk()
    root.withdraw()

    screen_width=root.winfo_screenwidth()
    screen_height=root.winfo_screenheight()

    cap = cv2.VideoCapture(0)
    cap.set(3, screen_width)  # 设置摄像头的宽度为 screen_width
    cap.set(4, screen_height)  # 设置摄像头的高度为 screen_height

    detector = HandDetector(detectionCon=0.8, maxHands=1)

    class SnakeGameClass:
        def __init__(self, pathFood, screen_width, screen_height):
            self.points = []  # 蛇的所有点
            self.lengths = []  # 每个点之间的距离
            self.currentLength = 0  # 蛇的总长度
            self.allowedLength = 150  # 总允许的长度
            self.previousHead = 0, 0  # 上一头点

            self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
            self.hFood, self.wFood, _ = self.imgFood.shape
            self.foodPoint = 0, 0
            self.randomFoodLocation(screen_width, screen_height)

            self.score = 0
            self.gameOver = False

        def randomFoodLocation(self, screen_width, screen_height):
            # 随机生成食物的位置，确保不会超出屏幕范围
            self.foodPoint = random.randint(100, screen_width - 100), random.randint(100, screen_height - 100)

        def update(self, imgMain, currentHead):

            if self.gameOver:
                cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                                    scale=7, thickness=5, offset=20)
                cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                                    scale=7, thickness=5, offset=20)
            else:
                px, py = self.previousHead
                cx, cy = currentHead

                self.points.append([cx, cy])
                distance = math.hypot(cx - px, cy - py)
                self.lengths.append(distance)
                self.currentLength += distance
                self.previousHead = cx, cy

                # 蛇身长度缩减
                if self.currentLength > self.allowedLength:
                    for i, length in enumerate(self.lengths):
                        self.currentLength -= length
                        self.lengths.pop(i)
                        self.points.pop(i)
                        if self.currentLength < self.allowedLength:
                            break

                # 检查蛇是否吃到食物
                rx, ry = self.foodPoint
                if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                        ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                    self.randomFoodLocation(screen_width, screen_height)
                    self.allowedLength += 50
                    self.score += 1

                    # 数据保存
                    if grab_upload_data(19) == 0:
                        update_upload_data(19, self.score)
                    else:
                        if grab_upload_data(19) < self.score:
                            update_upload_data(19, self.score)

                # 绘制蛇
                if self.points:
                    for i, point in enumerate(self.points):
                        if i != 0:
                            cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                    cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)

                # 绘制食物
                imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                            (rx - self.wFood // 2, ry - self.hFood // 2))

                cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                                    scale=3, thickness=3, offset=10)

                # 检查碰撞
                pts = np.array(self.points[:-2], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
                minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

                if -1 <= minDist <= 1:
                    print("碰撞")
                    self.gameOver = True
                    self.points = []  # 重置蛇的所有点
                    self.lengths = []  # 重置每个点之间的距离
                    self.currentLength = 0  # 重置蛇的总长度
                    self.allowedLength = 150  # 重置总允许的长度
                    self.previousHead = 0, 0  # 重置上一头点
                    self.randomFoodLocation(screen_width, screen_height)

            return imgMain

    game = SnakeGameClass("Resource/img/newgame/Donut.png", screen_width, screen_height)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        if hands:
            lmList = hands[0]['lmList']
            pointIndex = lmList[8][0:2]
            img = game.update(img, pointIndex)

        cv2.imshow("Gluttonous Snack", img)
        key = cv2.waitKey(1)
        if key == ord('r'):
            game.gameOver = False
        elif key == ord(' '):
            break
    cap.release()
    cv2.destroyAllWindows()

def start_game_19():
    root = tk.Tk()
    root.withdraw()

    # 參數調整
    time_between_pipe_spawn = grab_game_data(11)

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    pygame.init()

    # Initialize required elements/environment
    VID_CAP = cv2.VideoCapture(0)
    screen_width=root.winfo_screenwidth()
    screen_height=root.winfo_screenheight()
    VID_CAP.set(3, screen_width)  # 设置摄像头的宽度为 screen_width
    VID_CAP.set(4, screen_height)  # 设置摄像头的高度为 screen_height
    window_size = (screen_width, screen_height)  # width by height
    screen = pygame.display.set_mode(window_size)

    # Bird and pipe init
    bird_img = pygame.image.load("Resource/img/newgame/bird_sprite.png")
    bird_img = pygame.transform.scale(bird_img, (bird_img.get_width() / 6, bird_img.get_height() / 6))
    bird_frame = bird_img.get_rect()
    bird_frame.center = (window_size[0] // 6, window_size[1] // 2)
    pipe_frames = deque()
    pipe_img = pygame.image.load("Resource/img/newgame/pipe_sprite_single.png")

    pipe_starting_template = pipe_img.get_rect()
    space_between_pipes = 300

    # Game loop
    game_clock = time.time()
    stage = 1
    pipeSpawnTimer = 0
    dist_between_pipes = 300
    pipe_velocity = lambda: dist_between_pipes / time_between_pipe_spawn
    level = 0
    score = 0
    didUpdateScore = False
    game_is_running = True

    with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:
        while True:
            # Check if game is running
            if not game_is_running:
                text = pygame.font.SysFont("Helvetica Bold.ttf", 64).render('Game over!', True, (99, 245, 255))
                tr = text.get_rect()
                tr.center = (window_size[0] / 2, window_size[1] / 2)
                screen.blit(text, tr)
                pygame.display.update()
                pygame.time.wait(2000)
                VID_CAP.release()
                cv2.destroyAllWindows()
                pygame.quit()

            # Check if user quit window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    VID_CAP.release()
                    cv2.destroyAllWindows()

            # Get frame
            ret, frame = VID_CAP.read()
            if not ret:
                print("Empty frame, continuing...")
                continue

            # Clear screen
            screen.fill((125, 220, 232))

            # Face mesh
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame)
            frame.flags.writeable = True

            # Draw mesh
            if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
                # 94 = Tip of nose
                marker = results.multi_face_landmarks[0].landmark[94].y
                bird_frame.centery = (marker - 0.5) * 1.5 * window_size[1] + window_size[1] / 2
                if bird_frame.top < 0: bird_frame.y = 0
                if bird_frame.bottom > window_size[1]: bird_frame.y = window_size[1] - bird_frame.height

            # Mirror frame, swap axes because opencv != pygame
            frame = cv2.flip(frame, 1).swapaxes(0, 1)

            # Update pipe positions
            for pf in pipe_frames:
                pf[0].x -= pipe_velocity()
                pf[1].x -= pipe_velocity()

            if len(pipe_frames) > 0 and pipe_frames[0][0].right < 0:
                pipe_frames.popleft()

            # Update screen
            pygame.surfarray.blit_array(screen, frame)
            screen.blit(bird_img, bird_frame)
            checker = True
            for pf in pipe_frames:
                # Check if bird went through to update score
                if pf[0].left <= bird_frame.x <= pf[0].right:
                    checker = False
                    if not didUpdateScore:
                        score += 1
                        didUpdateScore = True
                # Update screen
                screen.blit(pipe_img, pf[1])
                screen.blit(pygame.transform.flip(pipe_img, 0, 1), pf[0])
            if checker: didUpdateScore = False

            # Stage, score text
            text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Stage {stage}', True, (99, 245, 255))
            tr = text.get_rect()
            tr.center = (100, 50)
            screen.blit(text, tr)
            text = pygame.font.SysFont("Helvetica Bold.ttf", 50).render(f'Score: {score}', True, (99, 245, 255))
            tr = text.get_rect()
            tr.center = (100, 100)
            screen.blit(text, tr)

            # Update screen
            pygame.display.flip()

            # Check if bird is touching a pipe
            if any([bird_frame.colliderect(pf[0]) or bird_frame.colliderect(pf[1]) for pf in pipe_frames]):
                game_is_running = False

            # Time to add new pipes
            if pipeSpawnTimer == 0:
                top = pipe_starting_template.copy()
                top.x, top.y = window_size[0], random.randint(-950, -300)
                bottom = pipe_starting_template.copy()
                bottom.x, bottom.y = window_size[0], top.y + 1100 + space_between_pipes
                pipe_frames.append([top, bottom])

            # Update pipe spawn timer - make it cyclical
            pipeSpawnTimer += 1
            if pipeSpawnTimer >= time_between_pipe_spawn * 1.5: pipeSpawnTimer = 0

            # Update stage
            if time.time() - game_clock >= 10:
                time_between_pipe_spawn *= 5 / 6
                stage += 1
                game_clock = time.time()

                # DataSave
                if grab_upload_data(20) == 0:
                    update_upload_data(20, score)
                else:
                    if grab_upload_data(20) < score:
                        update_upload_data(20, score)

def start_game_20():
    # --- 初始化 Mediapipe ---
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
    mp_drawing = mp.solutions.drawing_utils

    def calculate_ear(eye_landmarks):
        vertical1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        vertical2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (vertical1 + vertical2) / (2.0 * horizontal)

    EAR_THRESHOLD = 0.25
    CONSECUTIVE_FRAMES = 5
    frame_counter = 0
    blink_triggered = False

    # --- 初始化 Pygame ---
    pygame.init()
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("木頭針插遊戲")

    # --- 載入圖片 ---
    wood_image_path = "Resource/img/newgame/wood.png"
    needle1_image_path = "Resource/img/newgame/red_dart.png"
    needle2_image_path = "Resource/img/newgame/green_dart.png"
    ball_image_path = "Resource/img/newgame/Ball.png"

    wood_image = pygame.image.load(wood_image_path)
    wood_image = pygame.transform.scale(wood_image, (int(screen_width / 20), int(screen_height * 1.5)))

    ball_image = pygame.image.load(ball_image_path)
    ball_image = pygame.transform.scale(ball_image, (50, 50))

    needle1_image = pygame.image.load(needle1_image_path)
    needle1_image = pygame.transform.scale(needle1_image, (int(screen_width / 2), 50))

    needle2_image = pygame.image.load(needle2_image_path)
    needle2_image = pygame.transform.scale(needle2_image, (int(screen_width / 2), 50))

    needle_images = [needle1_image, needle2_image]

    # --- 遊戲變數 ---
    white = (255, 255, 255)
    red = (255, 0, 0)

    wood_width = screen_width / 20
    wood_height = screen_height * 1.5
    wood_pos = [screen_width / 5, -wood_height / 2]
    wood_move_down = screen_height / 10

    ball_radius = 20
    ball_pos = [screen_width / 2, screen_height / 4]
    ball_speed = 10

    needles = []
    score = 0
    max_score = 10
    game_over = False
    game_lost = False

    # --- 開啟攝影機 ---
    cap = cv2.VideoCapture(0)

    # 碰撞檢測函數
    def check_collision(ball_pos, ball_radius, needles):
        ball_rect = pygame.Rect(
            ball_pos[0] - ball_radius,
            ball_pos[1] - ball_radius,
            ball_radius * 2,
            ball_radius * 2
        )
        for needle in needles:
            needle_rect = pygame.Rect(
                needle[0] - needle[3].get_width(),
                needle[1],
                needle[3].get_width(),
                needle[3].get_height()
            )
            if ball_rect.colliderect(needle_rect):
                return True
        return False

    # 遊戲主迴圈
    while True:
        # Mediapipe 偵測臉部
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to access the camera.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                h, w, _ = frame.shape

                left_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [362, 385, 387, 263, 373, 380]])
                right_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [33, 160, 158, 133, 153, 144]])
                left_ear = calculate_ear(left_eye)
                right_ear = calculate_ear(right_eye)
                ear = (left_ear + right_ear) / 2.0

                if ear < EAR_THRESHOLD:
                    frame_counter += 1
                else:
                    if frame_counter >= CONSECUTIVE_FRAMES:
                        blink_triggered = True
                    frame_counter = 0

        # Pygame 遊戲邏輯
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # 按下空白鍵
                    if game_over or game_lost:  # 如果遊戲結束或失敗
                        cap.release()
                        pygame.quit()
                        sys.exit()

        if not game_over and not game_lost:
            if blink_triggered:
                needle_x = screen_width - 50
                needle_y = screen_height / 2
                needle_image = needle_images[len(needles) % len(needle_images)]
                needles.append([needle_x, needle_y, False, needle_image])
                blink_triggered = False

            ball_pos[1] += ball_speed
            if ball_pos[1] + ball_radius >= screen_height / 2 + wood_move_down - 10 or ball_pos[1] - ball_radius <= 0:
                ball_speed *= -1
                ball_speed += random.uniform(-2, 2)

            for needle in needles:
                if not needle[2]:
                    if needle[0] > wood_pos[0] + wood_width + needle[3].get_width():
                        needle[0] -= 50
                    else:
                        needle[0] = wood_pos[0] + wood_width + needle[3].get_width()
                        needle[2] = True
                        wood_pos[1] += wood_move_down
                        for n in needles:
                            if n[2]:
                                n[1] += wood_move_down
                        score += 1
                        if score >= max_score:
                            game_over = True

            # 碰撞檢測
            if check_collision(ball_pos, ball_radius, needles):
                game_lost = True

        # 畫面繪製
        frame_resized = cv2.resize(rgb_frame, (screen_width, screen_height))
        frame_surface = pygame.surfarray.make_surface(frame_resized).convert()
        screen.blit(pygame.transform.rotate(frame_surface, -90), (0, 0))

        screen.blit(wood_image, (wood_pos[0], wood_pos[1]))
        for needle in needles:
            screen.blit(needle[3], (needle[0] - needle[3].get_width(), needle[1]))

        screen.blit(ball_image, (int(ball_pos[0] - ball_radius), int(ball_pos[1] - ball_radius)))

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, red)
        screen.blit(score_text, (10, 10))

        if game_over:
            end_text = font.render("You Win! Press SPACE to exit", True, red)
            screen.blit(end_text, (screen_width / 2 - 150, screen_height / 2))
            # DataSave
            if grab_upload_data(21) == 0:
                update_upload_data(21, score)
            else:
                if grab_upload_data(21) > score:
                    update_upload_data(21, score)
        elif game_lost:
            lost_text = font.render("Game Over! Press SPACE to exit", True, red)
            screen.blit(lost_text, (screen_width / 2 - 150, screen_height / 2))

        pygame.display.flip()
        clock = pygame.time.Clock()
        clock.tick(60)
