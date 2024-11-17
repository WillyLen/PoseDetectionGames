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