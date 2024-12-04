import cv2
import mediapipe as mp
import time
import numpy as np

# 初始化 Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 初始化攝影機
cap = cv2.VideoCapture(0)

# 記錄初始位置
initial_positions = {}

# 將比例座標轉換為像素座標
def to_pixel_coordinates(landmark, width, height):
    return int(landmark.x * width), int(landmark.y * height)

# 記錄初始位置
def record_initial_positions(landmarks, width, height):
    return {
        "left_foot": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX], width, height),
        "right_foot": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX], width, height),
        "left_hand": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_INDEX], width, height),
        "right_hand": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX], width, height),
        "left_hip": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_HIP], width, height),
        "right_hip": to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_HIP], width, height),
    }

# 計算距離
def calculate_distance(pos1, pos2):
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

# 顯示倒數在畫面上，畫面保持更新
def countdown_on_screen(seconds, width, height):
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 翻轉影像，方便觀看
        frame = cv2.flip(frame, 1)

        # 計算剩餘時間
        remaining_time = seconds - int(time.time() - start_time)

        # 在畫面中央顯示倒數數字
        cv2.putText(frame, str(remaining_time), (width // 2 - 50, height // 2 + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10, cv2.LINE_AA)

        # 顯示倒數畫面
        cv2.imshow("倒數計時", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or remaining_time <= 0:
            break

# 根據參數執行指定的偵測
def detect_motion(detection_type, initial_positions, landmarks, start_time, width, height):
    result = None

    if detection_type == "left_step_distance":
        left_foot = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX], width, height)
        result = abs(left_foot[0] - initial_positions["left_foot"][0])

    elif detection_type == "right_step_distance":
        right_foot = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX], width, height)
        result = abs(right_foot[0] - initial_positions["right_foot"][0])

    elif detection_type == "squat_time":
        left_hip = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_HIP], width, height)
        right_hip = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_HIP], width, height)
        if left_hip[1] > initial_positions["left_hip"][1] and right_hip[1] > initial_positions["right_hip"][1]:
            result = time.time() - start_time

    elif detection_type == "highest_vertical_reach":
        left_hand = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_INDEX], width, height)
        right_hand = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX], width, height)
        result = min(left_hand[1], right_hand[1])

    elif detection_type == "widest_horizontal_reach":
        left_hand = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_INDEX], width, height)
        right_hand = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX], width, height)
        result = abs(left_hand[0] - right_hand[0])

    elif detection_type == "highest_leg_lift":
        left_foot = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX], width, height)
        right_foot = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX], width, height)
        result = min(left_foot[1], right_foot[1])

    elif detection_type == "hip_max_distance":
        left_hip = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.LEFT_HIP], width, height)
        right_hip = to_pixel_coordinates(landmarks[mp_pose.PoseLandmark.RIGHT_HIP], width, height)
        result = max(
            calculate_distance(left_hip, initial_positions["left_hip"]),
            calculate_distance(right_hip, initial_positions["right_hip"]),
        )

    return result

# 主要流程
def main(detection_type):
    global initial_positions

    print("請站定位，按 'q' 退出...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 翻轉影像，方便觀看
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)

        if result.pose_landmarks:
            # 繪製姿勢關鍵點
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # 紀錄初始位置
            landmarks = result.pose_landmarks.landmark
            initial_positions = record_initial_positions(landmarks, width, height)
            print("初始位置已記錄:", initial_positions)
            break

        cv2.imshow("站定位", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 倒數顯示在畫面上，畫面持續更新
    countdown_on_screen(5, width, height)

    # 開始追蹤動作
    start_time = time.time()
    print(f"開始進行 {detection_type} 偵測...")
    detected_value = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)

        if result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # 偵測指定的參數
            detected_value = detect_motion(detection_type, initial_positions, result.pose_landmarks.landmark, start_time, width, height)

        cv2.imshow(f"{detection_type} 偵測", frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    print(f"{detection_type} 偵測結果:", detected_value)

    cap.release()
    cv2.destroyAllWindows()

# 執行程式，傳入偵測項目
detection_type = "left_step_distance"
main(detection_type)
