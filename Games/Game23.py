import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import sys

# --- 初始化 Mediapipe ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

def calculate_ear(eye_landmarks):
    vertical1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    vertical2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

EAR_THRESHOLD = 0.25  # EAR 小於此值判定眨眼
CONSECUTIVE_FRAMES = 10 # 至少連續 N 幀滿足條件才判定為一次眨眼
frame_counter = 0
blink_triggered = False  # 用於觸發針插入

# --- 初始化 Pygame ---
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("木頭針插遊戲")

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

clock = pygame.time.Clock()
fps = 60

# --- 遊戲變數 ---
wood_width = screen_width / 20
wood_height = screen_height * 1.5
wood_pos = [screen_width / 6, -wood_height / 2]
wood_move_down = screen_height / 10

ball_radius = 20
ball_pos = [screen_width / 2, screen_height / 4]
ball_speed = random.uniform(2, 4)

needle_length = screen_width / 2
needles = []
needle_colors = ["red", "blue", "green"]

score = 0
max_score = 10
game_over = False

# --- 開啟攝影機 ---
cap = cv2.VideoCapture(0)

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

    # --- Pygame 遊戲邏輯 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    if blink_triggered and not game_over:
        needle_x = screen_width - 50
        needle_y = screen_height / 2
        needle_color = needle_colors[len(needles) % len(needle_colors)]
        needles.append([needle_x, needle_y, needle_color, False])
        blink_triggered = False

    ball_pos[1] += ball_speed
    if ball_pos[1] + ball_radius > screen_height / 2 + wood_move_down or ball_pos[1] - ball_radius < 0:
        ball_speed *= -1
        ball_speed += random.uniform(-0.2, 0.2)

    for needle in needles:
        if not needle[3]:
            if needle[0] > wood_pos[0] + wood_width + needle_length:
                needle[0] -= 10
            else:
                needle[0] = wood_pos[0] + wood_width + needle_length
                needle[3] = True
                wood_pos[1] += wood_move_down
                for n in needles:
                    if n[3]:
                        n[1] += wood_move_down
                score += 1
                if score >= max_score:
                    game_over = True

    screen.fill(white)
    pygame.draw.rect(screen, black, (wood_pos[0], wood_pos[1], wood_width, wood_height))
    pygame.draw.circle(screen, red, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    for needle in needles:
        pygame.draw.line(screen, needle[2], (needle[0], needle[1]), (needle[0] - needle_length, needle[1]), 10)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, black)
    screen.blit(score_text, (10, 10))

    if game_over:
        end_text = font.render("You Win!", True, black)
        screen.blit(end_text, (screen_width / 2 - 50, screen_height / 2))

    pygame.display.flip()
    clock.tick(fps)
