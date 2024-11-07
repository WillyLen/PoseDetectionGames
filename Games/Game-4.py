import pygame                    # 用於遊戲的視覺效果和聲音
import random                    # 用於生成隨機位置的石頭和金幣
import cv2                       # 用於開啟攝像頭來捕捉玩家動作
import mediapipe as mp           # 用於肢體追蹤，偵測玩家的肩膀位置
import os                        # 用於文件操作（例如讀取/保存遊戲數據）
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import update_game_data, grab_game_data
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv

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
        self.rect.centerx = WIDTH * 5 / 6
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
                wolf.rect.centerx += WIDTH / 12
                print("Speed increased to:", speed)
            elif time_diff < 3:  # 如果間隔時間小於3秒，減速
                speed -= 1
                wolf.rect.centerx -= WIDTH / 12
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
        if grab_game_data(15) == 0:
            update_game_data(15, countdown)
        else:
            if grab_game_data(15) > countdown:
                update_game_data(15, countdown)
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