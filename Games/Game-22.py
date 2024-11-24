import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 遊戲窗口尺寸
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("木頭針插遊戲")

# 顏色定義
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# 遊戲變數
clock = pygame.time.Clock()
fps = 60

# 木頭
wood_width = screen_width / 20
wood_height = screen_height * 1.5
wood_pos = [screen_width / 6,  - wood_height / 2]  # 固定在左側
wood_move_down = screen_height / 10  # 每次下降的距離

# 球
ball_radius = 20
ball_pos = [screen_width / 2, screen_height / 4]
ball_speed = random.uniform(2, 4)  # 初始速度

# 針
needle_length = screen_width / 2
needles = []  # 保存針的資料 [x, y, 顏色, 是否已插入]

# 遊戲狀態變數
score = 0
max_score = 10  # 插入 10 根針即可獲勝
game_over = False

# 定義顏色循環 (紅、藍、綠)
needle_colors = ["red", "blue", "green"]

# 遊戲主迴圈
while True:
    screen.fill(white)  # 清屏

    # 檢查遊戲事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 按下空白鍵插入針
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
            # 初始化針的資料
            needle_x = screen_width - 50  # 從右側發射
            needle_y = screen_height / 2  # 每次針都從中間發射
            needle_color = needle_colors[len(needles) % len(needle_colors)]  # 循環顏色
            needles.append([needle_x, needle_y, needle_color, False])  # 加入針並設置未插入

    # 更新球的位置
    ball_pos[1] += ball_speed

    # 檢查球是否超出邊界，並反彈
    if ball_pos[1] + ball_radius > screen_height / 2 + wood_move_down or ball_pos[1] - ball_radius < 0:
        ball_speed *= -1  # 反彈
        ball_speed += random.uniform(-0.2, 0.2)  # 控制隨機速度變化範圍，避免過小的變化

    # 更新針的位置
    for needle in needles:
        if not needle[3]:  # 如果針未插入
            if needle[0] > wood_pos[0] + wood_width + needle_length:  # 如果針未到達木頭
                needle[0] -= 10  # 水平左移
            else:  # 當針碰到木頭時
                needle[0] = wood_pos[0] + wood_width + needle_length  # 確保針固定在木頭右邊緣
                needle[3] = True  # 標記針已插入
                # 木頭和所有插入的針一起下降
                wood_pos[1] += wood_move_down
                for n in needles:
                    if n[3]:  # 僅讓已插入的針下降
                        n[1] += wood_move_down
                score += 1  # 更新分數
                if score >= max_score:  # 插入 10 根針即勝利
                    game_over = True

    # 繪製木頭
    pygame.draw.rect(screen, black, (wood_pos[0], wood_pos[1], wood_width, wood_height))

    # 繪製球
    pygame.draw.circle(screen, red, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # 繪製針
    for needle in needles:
        pygame.draw.line(screen, needle[2], (needle[0], needle[1]), (needle[0] - needle_length, needle[1]), 10)

    # 繪製分數
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, black)
    screen.blit(score_text, (10, 10))

    # 檢查遊戲結束
    if game_over:
        end_text = font.render("You Win!", True, black)
        screen.blit(end_text, (screen_width / 2 - 50, screen_height / 2))

    # 更新屏幕
    pygame.display.flip()
    clock.tick(fps)

