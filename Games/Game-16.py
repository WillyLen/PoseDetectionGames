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