from PIL import Image, ImageDraw, ImageFont
import cv2
import mediapipe as mp
import numpy as np
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data, grab_upload_data_float

# 初始化 Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 全域變數
max_distance = 0
start_position = None
last_max_update_time = None  # 用於記錄最大距離最後一次更新的時間

# 計算兩點距離
def calculate_distance(point1, point2, mode):
    if mode == "horizontal":
        return abs(point1[0] - point2[0])
    elif mode == "vertical":
        return abs(point1[1] - point2[1])
    else:
        raise ValueError("模式必須是 'horizontal' 或 'vertical'")


# 在影像上繪製中文文字
def put_chinese_text(image, text, position, font_path="Resource/font.ttf", font_size=50, color=(0, 0, 255)):
    # 將 OpenCV 圖片轉換為 PIL 圖片
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    # 加載字型
    font = ImageFont.truetype(font_path, font_size)
    # 繪製文字
    draw.text(position, text, font=font, fill=color)
    # 將 PIL 圖片轉回 OpenCV 圖片
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# 主程式
def detect(target_node,ori_node_1, ori_node_2, Mode, save_num):
    global max_distance, start_position, last_max_update_time
    mode = Mode
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法啟動鏡頭")
        return

    # 設定全螢幕視窗
    cv2.namedWindow("偵測", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("偵測", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    phase = "countdown"  # 階段控制
    countdown = 5  # 倒數計時
    countdown_start = time.time()
    stable_duration = 3  # 最大距離穩定的持續時間（秒）
    last_max_update_time = time.time()  # 初始化最大距離的最後更新時間

    while True:
        ret, frame = cap.read()
        if not ret:
            print("無法讀取影像")
            break

        frame = cv2.flip(frame, 1)  # 水平翻轉畫面
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        # 繪製人體骨架
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        h, w, _ = frame.shape
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            # 計算原點節點中心
            ori_x = (landmarks[ori_node_1].x + landmarks[ori_node_2].x) / 2 * w
            ori_y = (landmarks[ori_node_1].y + landmarks[ori_node_2].y) / 2 * h
            ori_position = (ori_x, ori_y)

            # 目標節點位置
            target_x = landmarks[target_node].x * w
            target_y = landmarks[target_node].y * h
            target_position = (target_x, target_y)

            # 倒數階段
            if phase == "countdown":
                remaining_time = countdown - (time.time() - countdown_start)
                frame = put_chinese_text(frame, f"請就定位 {int(remaining_time)} 秒", (50, 50))
                if remaining_time <= 0:
                    start_position = ori_position
                    max_distance = 0  # 初始化最大距離
                    last_max_update_time = time.time()  # 重置時間
                    phase = "detect"

            
            # 偵測階段
            elif phase == "detect":
                frame = put_chinese_text(frame, "請開始動作", (50, 50))
                distance = calculate_distance(target_position, start_position, mode)

                # 判斷最大距離並更新
                if distance > max_distance:
                    max_distance = distance
                    last_max_update_time = time.time()  # 更新最後一次修改的時間
                frame = put_chinese_text(frame, f"最大距離: {int(max_distance)}", (50, 100))

                # 判斷是否穩定
                if time.time() - last_max_update_time >= stable_duration:
                    phase = "finished"
            
            # 偵測完成階段
            elif phase == "finished":
                frame = put_chinese_text(frame, f"最大距離: {int(max_distance)}", (50, 100))
                frame = put_chinese_text(frame, "偵測結束！", (50, 150))
                # DataSave
                if grab_upload_data(save_num) == 0:
                    update_upload_data(save_num, int(max_distance))
                else:
                    if grab_upload_data(save_num) > int(max_distance):
                        update_upload_data(save_num, int(max_distance))

        # 顯示畫面
        cv2.imshow("偵測", frame)

        # 按下空白鍵退出
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    cap.release()
    cv2.destroyAllWindows()
