import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from PIL import Image, ImageDraw, ImageFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data, grab_upload_data_float

def squatting_detect():
    # 初始化 Mediapipe
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # 開啟攝影機
    cap = cv2.VideoCapture(0)

    # 記錄臀部節點的垂直位置變化
    hip_index = 23  # 左臀部節點
    y_positions = deque(maxlen=10)  # 儲存最近 10 個 y 坐標
    state = "countdown"  # 狀態：'countdown', 'ready', 'action', 'done'
    start_time = None
    squat_time = None
    y_start = None  # 原始高度

    # 倒數計時設定
    countdown_duration = 5  # 倒數秒數

    # 設定字體
    font_path = "Resource/font.ttf"  # 替換為您的字體檔案路徑
    try:
        font = ImageFont.truetype(font_path, 32)
    except IOError:
        print(f"無法加載字體：{font_path}")
        exit()

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

    # 設定全螢幕視窗
    cv2.namedWindow("動作捕捉", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("動作捕捉", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

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

            # 獲取臀部節點的 y 坐標
            hip_y = results.pose_landmarks.landmark[hip_index].y
            y_positions.append(hip_y)

            # 狀態判斷
            if state == "countdown":
                if start_time is None:
                    start_time = time.time()
                elapsed_time = time.time() - start_time
                remaining_time = countdown_duration - int(elapsed_time)

                if remaining_time > 0:
                    annotated_frame = draw_chinese_text(
                        annotated_frame,
                        f"請保持姿勢: {remaining_time} 秒",
                        (0, 0),
                        font,
                        (255, 255, 0),
                        bold=True,
                    )
                else:
                    y_start = hip_y  # 記錄原始高度
                    print(y_start)
                    state = "ready"
                    start_time = None
                    annotated_frame = draw_chinese_text(
                        annotated_frame,
                        "準備開始動作",
                        (0, 0),
                        font,
                        (0, 255, 0),
                        bold=True,
                    )

            elif state == "ready":
                annotated_frame = draw_chinese_text(
                    annotated_frame,
                    "請進行蹲下起來的動作",
                    (0, 0),
                    font,
                    (255, 255, 0),
                    bold=True,
                )
                if len(y_positions) >= 2 and y_positions[-1] > y_start + 0.1:  # 偵測超過原始高度
                    state = "action"
                    start_time = time.time()
                    print("動作開始")

            elif state == "action":
                if len(y_positions) >= 2 and y_positions[-1] <= y_start + 0.1 and time.time() - start_time > 1.5:  # 回到原始高度
                    squat_time = time.time() - start_time
                    state = "done"
                    print(f"動作完成，用時：{squat_time:.2f} 秒")
                    # DataSave
                    if grab_upload_data_float(23) == 0:
                        update_upload_data(23, round(squat_time,2))
                    else:
                        if grab_upload_data_float(23) > round(squat_time,2):
                            update_upload_data(23, round(squat_time,2))

            elif state == "done":
                annotated_frame = draw_chinese_text(
                    annotated_frame,
                    f"動作完成: {squat_time:.2f} 秒",
                    (0, 0),
                    font,
                    (0, 255, 0),
                    bold=True,
                )
                annotated_frame = draw_chinese_text(
                    annotated_frame,
                    "按空白鍵重置",
                    (0, 50),
                    font,
                    (0, 255, 255),
                    bold=True,
                )

        # 顯示影像
        cv2.imshow("動作捕捉", annotated_frame)

        # 按下空白鍵重置狀態
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # 釋放資源
    cap.release()
    cv2.destroyAllWindows()
# squatting_detect()