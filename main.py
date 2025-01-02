import cv2
import mediapipe as mp
import numpy as np
import time
import math
from PIL import ImageFont, ImageDraw, Image

# 初始化 MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 遊戲參數
SLOW_JOG_MIN_SPEED = 0.2  # 最小速度
SLOW_JOG_MAX_SPEED = 1.0  # 最大速度
ARM_SYNC_THRESHOLD = 20  # 手臂擺動的角度範圍

# 字體設定 (需要一個支持中文的字體檔案，例如 Noto Sans CJK)
FONT_PATH = "Resource/font.ttf"

# 計算兩個點之間的距離
def calculate_speed(prev_point, current_point, delta_time):
    if prev_point and current_point and delta_time > 0:
        distance = np.linalg.norm(np.array(prev_point) - np.array(current_point))
        speed = distance / delta_time
        return speed
    return 0

# 計算兩個點之間的角度
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ab = a - b
    cb = c - b
    dot_product = np.dot(ab, cb)
    magnitude = np.linalg.norm(ab) * np.linalg.norm(cb)
    if magnitude == 0:
        return 0
    angle = math.degrees(math.acos(dot_product / magnitude))
    return angle

# 在 OpenCV 圖像上繪製中文字
def draw_chinese_text(image, text, position, font_path, font_size, color):
    font = ImageFont.truetype(font_path, font_size)
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def main():
    cap = cv2.VideoCapture(0)  # 開啟鏡頭
    prev_ankle_point = None
    prev_time = time.time()
    score = 0
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 鏡頭反轉，便於玩家操作
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # 繪製身體關節點
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                landmarks = results.pose_landmarks.landmark

                # 提取腳踝位置
                left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
                ankle_point = (int(left_ankle.x * frame.shape[1]), int(left_ankle.y * frame.shape[0]))
                
                # 提取手臂位置
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
                left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
                
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]
                
                # 計算速度
                current_time = time.time()
                delta_time = current_time - prev_time
                speed = calculate_speed(prev_ankle_point, ankle_point, delta_time)
                
                # 計算手臂角度
                left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                # 顯示速度
                image = draw_chinese_text(image, f"速度: {speed:.2f} m/s", (50, 50), FONT_PATH, 24, (0, 255, 0))
                
                # 檢測速度
                if SLOW_JOG_MIN_SPEED <= speed <= SLOW_JOG_MAX_SPEED:
                    score += 1
                    image = draw_chinese_text(image, "步伐穩定！", (50, 100), FONT_PATH, 24, (0, 255, 0))
                else:
                    image = draw_chinese_text(image, "速度過快或過慢！", (50, 100), FONT_PATH, 24, (0, 0, 255))
                
                # 檢測手臂同步
                if abs(left_arm_angle - right_arm_angle) < ARM_SYNC_THRESHOLD:
                    score += 1
                    image = draw_chinese_text(image, "手臂擺動同步！", (50, 150), FONT_PATH, 24, (0, 255, 0))
                else:
                    image = draw_chinese_text(image, "手臂擺動不同步！", (50, 150), FONT_PATH, 24, (0, 0, 255))

                image = draw_chinese_text(image, f"分數: {score}", (50, 200), FONT_PATH, 24, (255, 255, 0))

                prev_ankle_point = ankle_point
                prev_time = current_time

            cv2.imshow('超慢跑挑戰 - 加強版', image)

            if cv2.waitKey(5) & 0xFF == 32:  # 空白鍵退出
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
