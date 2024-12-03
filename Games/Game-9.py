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