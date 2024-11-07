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
    if grab_game_data(21) == 0:
        update_game_data(21, point)
    else:
        if grab_game_data(21) < point:
            update_game_data(21, point)

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