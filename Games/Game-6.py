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