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
        self.size = WIDTH / 10
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
    if grab_game_data(25) == 0:
        update_game_data(25, score)
    else:
        if grab_game_data(25) < score:
            update_game_data(25, score)

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