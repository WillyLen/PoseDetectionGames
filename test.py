import cv2
import mediapipe as mp
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 初始化 Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 開啟攝影機
cap = cv2.VideoCapture(0)

# 設定計時器
start_time = None
capture_duration = 5  # 倒數計時秒數

# 儲存節點位置與最大移動距離
keypoints_start = None
max_distance = 0

# 設定字體
font_path = "Resource/font.ttf"  # 替換為您的系統字體路徑
try:
    font = ImageFont.truetype(font_path, 32)
except IOError:
    print(f"無法加載字體：{font_path}")
    exit()

# 偵測狀態標記
detection_count = 0  # 偵測次數：0 表示第一次，1 表示第二次

def draw_chinese_text(img, text, position, font, color, bold=False):
    """在 OpenCV 圖像上繪製中文文字，支援模擬粗體"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    if bold:
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 模擬粗體偏移
        for offset in offsets:
            draw.text((position[0] + offset[0], position[1] + offset[1]), text, font=font, fill=color)
    draw.text(position, text, font=font, fill=color)  # 繪製文字
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("無法讀取攝影機影像")
        break

    # 影像轉換為 Mediapipe 需要的格式
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # 繪製關鍵點
    annotated_frame = frame.copy()
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(annotated_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # 偵測狀態管理
    if start_time is None:
        start_time = time.time()
        display_text = "倒數計時開始..."
    else:
        elapsed_time = time.time() - start_time
        remaining_time = capture_duration - int(elapsed_time)

        if remaining_time > 0:
            # 根據偵測次數顯示不同的提示文字
            if detection_count == 0:
                display_text = f"請保持姿勢: {remaining_time} 秒"
            else:
                display_text = f"請進行動作: {remaining_time} 秒"
        elif keypoints_start is None:  # 第一次倒數結束，記錄初始位置
            keypoints_start = [
                (lm.x, lm.y, lm.z)
                for lm in results.pose_landmarks.landmark
            ]
            detection_count += 1  # 偵測次數加 1
            display_text = "請進行動作"
            start_time = time.time()
        else:  # 偵測移動距離
            current_positions = [
                (lm.x, lm.y, lm.z)
                for lm in results.pose_landmarks.landmark
            ]
            distances = [
                np.linalg.norm(np.array(current) - np.array(start))
                for current, start in zip(current_positions, keypoints_start)
            ]
            max_distance = max(max_distance, max(distances))
            elapsed_time = time.time() - start_time

            if elapsed_time >= 5:
                display_text = f"偵測結束，最大移動距離: {max_distance:.2f}"
                annotated_frame = draw_chinese_text(annotated_frame, "按空白鍵離開", (50, 150), font, (0, 0, 255), bold=True)

    # 顯示文字
    annotated_frame = draw_chinese_text(annotated_frame, display_text, (50, 50), font, (255, 0, 0), bold=True)

    # 顯示影像
    cv2.imshow("動作捕捉", annotated_frame)

    # 按下空白鍵結束程式
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

# 釋放資源
cap.release()
cv2.destroyAllWindows()
