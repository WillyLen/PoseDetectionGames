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