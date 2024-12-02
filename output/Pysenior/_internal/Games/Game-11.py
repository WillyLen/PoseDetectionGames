import pygame                    # 用於遊戲的視覺效果和聲音
import random                    # 用於生成隨機位置的石頭和金幣
import cv2                       # 用於開啟攝像頭來捕捉玩家動作
import mediapipe as mp           # 用於肢體追蹤，偵測玩家的肩膀位置
import os                        # 用於文件操作（例如讀取/保存遊戲數據）
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv

### 參數調整 ###

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
        self.size = 100 * (WIDTH / 1280)
        self.image = pygame.transform.scale(thumbtack_img, (self.size, self.size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 75 * (WIDTH / 1280)
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
        self.size = 125 * (WIDTH / 1280)
        self.image_ori = pygame.transform.scale(balloon_img, (self.size, self.size))
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = 100 * (WIDTH / 1280)
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