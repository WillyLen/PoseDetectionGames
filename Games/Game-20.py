import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import sys

# --- 初始化 Mediapipe ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

def calculate_ear(eye_landmarks):
    vertical1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    vertical2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

EAR_THRESHOLD = 0.25
CONSECUTIVE_FRAMES = 5
frame_counter = 0
blink_triggered = False

# --- 初始化 Pygame ---
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("木頭針插遊戲")

# --- 載入圖片 ---
wood_image_path = "Resource/img/newgame/wood.png"
needle1_image_path = "Resource/img/newgame/red_dart.png"
needle2_image_path = "Resource/img/newgame/green_dart.png"
ball_image_path = "Resource/img/newgame/Ball.png"

wood_image = pygame.image.load(wood_image_path)
wood_image = pygame.transform.scale(wood_image, (int(screen_width / 20), int(screen_height * 1.5)))

ball_image = pygame.image.load(ball_image_path)
ball_image = pygame.transform.scale(ball_image, (50, 50))

needle1_image = pygame.image.load(needle1_image_path)
needle1_image = pygame.transform.scale(needle1_image, (int(screen_width / 2), 50))

needle2_image = pygame.image.load(needle2_image_path)
needle2_image = pygame.transform.scale(needle2_image, (int(screen_width / 2), 50))

needle_images = [needle1_image, needle2_image]

# --- 遊戲變數 ---
white = (255, 255, 255)
red = (255, 0, 0)

wood_width = screen_width / 20
wood_height = screen_height * 1.5
wood_pos = [screen_width / 5, -wood_height / 2]
wood_move_down = screen_height / 10

ball_radius = 20
ball_pos = [screen_width / 2, screen_height / 4]
ball_speed = 10

needles = []
score = 0
max_score = 10
game_over = False
game_lost = False

# --- 開啟攝影機 ---
cap = cv2.VideoCapture(0)

# 碰撞檢測函數
def check_collision(ball_pos, ball_radius, needles):
    ball_rect = pygame.Rect(
        ball_pos[0] - ball_radius,
        ball_pos[1] - ball_radius,
        ball_radius * 2,
        ball_radius * 2
    )
    for needle in needles:
        needle_rect = pygame.Rect(
            needle[0] - needle[3].get_width(),
            needle[1],
            needle[3].get_width(),
            needle[3].get_height()
        )
        if ball_rect.colliderect(needle_rect):
            return True
    return False

# 遊戲主迴圈
while True:
    # Mediapipe 偵測臉部
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to access the camera.")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            h, w, _ = frame.shape

            left_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [362, 385, 387, 263, 373, 380]])
            right_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [33, 160, 158, 133, 153, 144]])
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0

            if ear < EAR_THRESHOLD:
                frame_counter += 1
            else:
                if frame_counter >= CONSECUTIVE_FRAMES:
                    blink_triggered = True
                frame_counter = 0

    # Pygame 遊戲邏輯
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    if not game_over and not game_lost:
        if blink_triggered:
            needle_x = screen_width - 50
            needle_y = screen_height / 2
            needle_image = needle_images[len(needles) % len(needle_images)]
            needles.append([needle_x, needle_y, False, needle_image])
            blink_triggered = False

        ball_pos[1] += ball_speed
        if ball_pos[1] + ball_radius >= screen_height / 2 + wood_move_down - 10 or ball_pos[1] - ball_radius <= 0:
            ball_speed *= -1
            ball_speed += random.uniform(-2, 2)

        for needle in needles:
            if not needle[2]:
                if needle[0] > wood_pos[0] + wood_width + needle[3].get_width():
                    needle[0] -= 50
                else:
                    needle[0] = wood_pos[0] + wood_width + needle[3].get_width()
                    needle[2] = True
                    wood_pos[1] += wood_move_down
                    for n in needles:
                        if n[2]:
                            n[1] += wood_move_down
                    score += 1
                    if score >= max_score:
                        game_over = True

        # 碰撞檢測
        if check_collision(ball_pos, ball_radius, needles):
            game_lost = True

    # 畫面繪製
    frame_resized = cv2.resize(rgb_frame, (screen_width, screen_height))
    frame_surface = pygame.surfarray.make_surface(frame_resized).convert()
    screen.blit(pygame.transform.rotate(frame_surface, -90), (0, 0))

    screen.blit(wood_image, (wood_pos[0], wood_pos[1]))
    for needle in needles:
        screen.blit(needle[3], (needle[0] - needle[3].get_width(), needle[1]))

    screen.blit(ball_image, (int(ball_pos[0] - ball_radius), int(ball_pos[1] - ball_radius)))

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, red)
    screen.blit(score_text, (10, 10))

    if game_over:
        end_text = font.render("You Win!", True, red)
        screen.blit(end_text, (screen_width / 2 - 50, screen_height / 2))
    elif game_lost:
        lost_text = font.render("Game Over!", True, red)
        screen.blit(lost_text, (screen_width / 2 - 50, screen_height / 2))

    pygame.display.flip()
    clock = pygame.time.Clock()
    clock.tick(60)
