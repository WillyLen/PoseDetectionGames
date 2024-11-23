import pygame
import sys

# 初始化 pygame
pygame.init()

# 設定螢幕尺寸與顏色
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("水平射針遊戲")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# FPS 設定
clock = pygame.time.Clock()
FPS = 60

# 遊戲參數
ball_radius = 20
ball_speed = 5  # 球的初始垂直速度
ball_acceleration = -0.1  # 球反彈後速度的遞減量
wood_width = 50
wood_height = SCREEN_HEIGHT
wood_move_down = 20  # 木頭下降距離
max_score = 10  # 勝利條件

# 遊戲狀態變數
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]  # 球的初始位置
wood_pos = [SCREEN_WIDTH // 4, -SCREEN_HEIGHT // 4]  # 木頭位置
needles = []  # 儲存要射出的針[x, y, inserted,speed,color]
for i in range(10):
    if i % 3 == 1:
        needles.append([SCREEN_WIDTH,  SCREEN_HEIGHT * 0.4, False, 5,RED])
    elif i % 3 == 2:
        needles.append([SCREEN_WIDTH,  SCREEN_HEIGHT * 0.4, False, 5,BLUE])
    else:
        needles.append([SCREEN_WIDTH,  SCREEN_HEIGHT * 0.4, False, 5,GREEN])
print(needles)
score = 0
game_over = False
ball_direction = 1  # 球的運動方向，1為向下，-1為向上
current_ball_speed = ball_speed  # 當前球的速度

# 字體
font = pygame.font.Font(None, 50)

# 功能函式
def draw_ball():
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

def draw_wood():
    pygame.draw.rect(screen, YELLOW, (wood_pos[0], wood_pos[1], wood_width, wood_height))

def draw_needles():
    for needle in needles:
        pygame.draw.line(screen, needle[4], (needle[0], needle[1]), (needle[0] + 10, needle[1]), 5)


def check_collision(needle):
    """檢查針是否碰到球"""
    dist_x = abs(needle[0] - ball_pos[0])
    dist_y = abs(needle[1] - ball_pos[1])
    return dist_x ** 2 + dist_y ** 2 <= ball_radius ** 2

# 遊戲迴圈
while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
            # 在右邊新增針，與木頭一半高度對齊

    # 更新球的位置
    if not game_over:
        ball_pos[1] += current_ball_speed * ball_direction

        # 球碰撞範圍邊界時反彈
        if ball_pos[1] - ball_radius < 0:  # 碰到頂部
            ball_direction = 1  # 向下
            current_ball_speed += ball_acceleration  # 減速
        elif ball_pos[1] + ball_radius >  SCREEN_HEIGHT // 2:  # 碰到底部
            ball_direction = -1  # 向上
            current_ball_speed += ball_acceleration  # 減速

        # 檢查速度是否足夠繼續反彈，若否則球下墜
        if current_ball_speed <= 0:
            ball_direction = 1
            current_ball_speed = ball_speed  # 重設速度

        # 更新針的位置
        for needle in needles:
            needle[0] -= 10  # 從右向左移動
            if check_collision(needle):  # 如果針碰到球
                game_over = True

        # 檢查針是否插入木頭
        for needle in needles:
            if needle[0] < wood_pos[0] + wood_width:
                needle_speed = 0
                wood_pos[1] += wood_move_down  # 木頭下降
                for n in needles:
                    n[1] += wood_move_down  # 所有針一起下降
                score += 1
            if score >= max_score:  # 插入 10 根針即勝利
                game_over = True

    # 畫面繪製
    draw_ball()
    draw_wood()

    # 分數與遊戲結束
    if game_over:
        text = font.render("You Win!" if score >= max_score else "Game Over!", True, RED)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)
