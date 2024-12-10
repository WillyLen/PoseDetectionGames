from PIL import Image, ImageDraw, ImageFont
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data, grab_upload_data_float

GameInfo = [
        {"code": "1", "line_height": "-10", "text": "檢測雙肩是否有節點"},{"code": "2", "line_height": "-10", "text": "檢測雙肩是否有節點"},
        {"code": "3", "line_height": "432", "text": "檢測膝蓋節點蹲下後是否能碰到紅線"},{"code": "4", "line_height": "432", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "5", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "6", "line_height": "72", "text": "檢測雙手向上舉直後是否能超過紅線"},
        {"code": "7", "line_height": "432", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},{"code": "8", "line_height": "72", "text": "檢測雙手向上舉直後是否能超過紅線"},
        {"code": "9", "line_height": "72", "text": "檢測雙手向上舉直後是否能超過紅線"},{"code": "10", "line_height": "576", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "11", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "12", "line_height": "-10", "text": "檢測骨盆兩側是否有節點"},
        {"code": "13", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "14", "line_height": "432", "text": "檢測骨盆兩側是否有節點及膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "15", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "16", "line_height": "-10", "text": "檢測雙肩是否有節點"},
        {"code": "17", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "18", "line_height": "-10", "text": "檢測雙手是否有節點"},
        {"code": "19", "line_height": "-10", "text": "檢測雙眼是否有節點"},{"code": "20", "line_height": "-10", "text": "檢測雙眼是否有節點"},
    ]

def show_camera_with_pose(code, pos1, pos2):
    # 查找对应的 GameInfo 项
    game_info = next((item for item in GameInfo if item["code"] == code), None)

    if game_info:
        line_height = int(game_info["line_height"])
        text = game_info["text"]
    else:
        print("未找到對應之遊戲訊息")

    # 初始化 MediaPipe 姿态检测
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose()

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 设置中文字体路径
    font_path = "Resource/font.ttf"  # macOS 示例路径，请修改为 Windows 的中文字体路径
    font = ImageFont.truetype(font_path, 40)

    while True:
        success, img = cap.read()
        if not success:
            break

        # 翻转画面方便观看
        img = cv2.flip(img, 1)

        # 将颜色格式转换为 RGB，适合 MediaPipe 处理
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        if results.pose_landmarks:
            # 绘制检测到的姿态关键点和连接线
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # 获取图像的尺寸
            h, w, _ = img.shape
            pos1_coords, pos2_coords = None, None  # 初始化两个关键点的坐标

            for id, lm in enumerate(results.pose_landmarks.landmark):
                landmark_x, landmark_y = int(lm.x * w), int(lm.y * h)

                # 绘制每个关键点的红色小圆
                cv2.circle(img, (landmark_x, landmark_y), 10, (205, 0, 0), cv2.FILLED)

                # 在 pos1 和 pos2 关键点绘制较大的圆，并标注文字
                if id == pos1:
                    pos1_coords = (landmark_x, landmark_y)
                    cv2.circle(img, pos1_coords, 30, (0, 0, 255), cv2.FILLED)  # pos1 红色
                elif id == pos2:
                    pos2_coords = (landmark_x, landmark_y)
                    cv2.circle(img, pos2_coords, 30, (0, 255, 0), cv2.FILLED)  # pos2 绿色

            # 如果检测到 pos1 和 pos2，则在它们之间画线
            if pos1_coords and pos2_coords:
                cv2.line(img, pos1_coords, pos2_coords, (255, 255, 255), 3)

            # 在图像上添加中文提示
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)
            draw.text((0, 0), text, font=font, fill=(0,0,255))
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            cv2.line(img, (0,line_height), (1280,line_height), (0, 0, 255), 10)


        # 显示带有节点和文字的摄像头画面
        cv2.imshow("Camera with Pose Detection", img)

        # 按空格键退出
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

# 调用函数显示影像和姿态检测节点
# show_camera_with_pose()

def leg_up_detect():
    # 初始化 Mediapipe Pose 模組
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # 用於記錄時間和動作狀態
    start_time = None
    left_foot_up = False
    right_foot_up = False
    best_time = float('inf')
    current_stage = "START"

    # 啟動攝像頭
    cap = cv2.VideoCapture(0)

    print("請完成抬放左腳和抬放右腳的動作，系統將記錄最短時間。")

    # 創建全螢幕窗口
    cv2.namedWindow("Foot Detection", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Foot Detection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    # 設定字型
    font_path = "Resource/font.ttf"  # 替換為您的中文字體檔案路徑
    try:
        font = ImageFont.truetype(font_path, 30)  # 字體大小可調整
    except IOError:
        print(f"無法加載字體：{font_path}")
        exit()

    # 在影像上繪製中文文字
    def draw_chinese_text(image, text, position, font, color):
        """在 OpenCV 圖像上繪製中文文字"""
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        draw.text(position, text, font=font, fill=color)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("無法讀取攝像頭影像。")
                break
            
            # 將影像轉為 RGB 格式
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            
            # 回到 BGR 格式以便 OpenCV 繪圖
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                # 獲取左腳踝與右腳踝的 y 坐標
                left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
                right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
                
                # 畫出關鍵點
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # 判斷腳是否抬起
                if left_ankle.visibility > 0.5 and left_ankle.y < 0.7:  # 假設 y < 0.4 表示抬起
                    if not left_foot_up:
                        left_foot_up = True
                        print("左腳抬起")
                        if current_stage == "START":
                            current_stage = "LEFT_UP"
                            start_time = time.time()
                
                if left_ankle.visibility > 0.5 and left_ankle.y >= 0.8:  # 假設 y >= 0.5 表示放下
                    if left_foot_up:
                        left_foot_up = False
                        print("左腳放下")
                        if current_stage == "LEFT_UP":
                            current_stage = "LEFT_DOWN"

                if right_ankle.visibility > 0.5 and right_ankle.y < 0.7:  # 假設 y < 0.4 表示抬起
                    if not right_foot_up:
                        right_foot_up = True
                        print("右腳抬起")
                        if current_stage == "LEFT_DOWN":
                            current_stage = "RIGHT_UP"

                if right_ankle.visibility > 0.5 and right_ankle.y >= 0.8:  # 假設 y >= 0.5 表示放下
                    if right_foot_up:
                        right_foot_up = False
                        print("右腳放下")
                        if current_stage == "RIGHT_UP":
                            end_time = time.time()
                            duration = end_time - start_time
                            print(f"完成一套動作，用時: {duration:.2f} 秒")
                            if duration < best_time:
                                best_time = duration
                                print(f"新的最短時間紀錄: {best_time:.2f} 秒")
                                # DataSave
                                if grab_upload_data_float(22) == 0:
                                    update_upload_data(22, round(best_time,2))
                                else:
                                    if grab_upload_data_float(22) > round(best_time,2):
                                        update_upload_data(22, round(best_time,2))
                            current_stage = "START"

            # 顯示中文文字
            image = draw_chinese_text(image, f"請抬起左腳後抬起右腳", (0, 0), font, (0, 0, 255))
            image = draw_chinese_text(image, f"最佳紀錄: {best_time:.2f} 秒", (0, 50), font, (0, 0, 255))
            cv2.imshow("Foot Detection", image)

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
# leg_up_detect()

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
                        (0, 0, 255),
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
                        (0, 0, 255),
                        bold=True,
                    )

            elif state == "ready":
                annotated_frame = draw_chinese_text(
                    annotated_frame,
                    "請進行蹲下起來的動作",
                    (0, 0),
                    font,
                    (0, 0, 255),
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
                    (255, 0, 0),
                    bold=True,
                )
                annotated_frame = draw_chinese_text(
                    annotated_frame,
                    "按空白鍵退出",
                    (0, 50),
                    font,
                    (255, 0, 0),
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