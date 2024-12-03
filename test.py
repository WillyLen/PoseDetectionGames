import cv2
import mediapipe as mp
import math
import time

# 初始化 Mediapipe Pose 模組
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 記錄結果
max_distances = {
    "left_step": 0,
    "right_step": 0,
    "hand_height": 0,
    "leg_height": 0,
    "hip_distance": 0,
    "arm_span": 0
}
squat_times = {"start": None, "end": None}

# 計算距離
def calculate_distance(point1, point2, axis="x"):
    if axis == "x":
        return abs(point1.x - point2.x)
    elif axis == "y":
        return abs(point1.y - point2.y)

# 偵測動作
def detect_action(image, landmarks, action_type):
    global max_distances, squat_times

    if action_type == "left_step":  # 左跨步最遠距離
        left_foot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
        max_distances["left_step"] = max(max_distances["left_step"], abs(left_foot.x - 0.5))  # 假設 0.5 是初始位置

    elif action_type == "right_step":  # 右跨步最遠距離
        right_foot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
        max_distances["right_step"] = max(max_distances["right_step"], abs(right_foot.x - 0.5))  # 假設 0.5 是初始位置

    elif action_type == "squat_time":  # 蹲下起來時間
        hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        if hip.y > 0.7:  # 假設 0.7 是蹲下閾值
            if squat_times["start"] is None:
                squat_times["start"] = time.time()
        else:
            if squat_times["start"] is not None and squat_times["end"] is None:
                squat_times["end"] = time.time()
                elapsed = squat_times["end"] - squat_times["start"]
                cv2.putText(image, f"Squat Time: {elapsed:.2f}s", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    elif action_type == "hand_height":  # 最高臂展
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = landmarks[mp_pose.PoseLandmark.NOSE]
        max_distances["hand_height"] = max(max_distances["hand_height"],
                                           calculate_distance(left_wrist, nose, axis="y"),
                                           calculate_distance(right_wrist, nose, axis="y"))

    elif action_type == "leg_height":  # 最高抬腳高度
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        max_distances["leg_height"] = max(max_distances["leg_height"],
                                          calculate_distance(left_ankle, left_hip, axis="y"))

    elif action_type == "hip_distance":  # 髖關節最遠移動距離
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        max_distances["hip_distance"] = max(max_distances["hip_distance"],
                                            calculate_distance(left_hip, left_hip, axis="x"))

    elif action_type == "arm_span":  # 水平最遠臂展
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        max_distances["arm_span"] = max(max_distances["arm_span"],
                                        calculate_distance(left_wrist, right_wrist, axis="x"))

# 開啟相機
cap = cv2.VideoCapture(0)

# 選擇動作類型
action_type = "left_step"  # 可更改為 "right_step", "squat_time", "hand_height", "leg_height", "hip_distance", "arm_span"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 將影像轉為 RGB 格式
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    # 偵測骨架
    results = pose.process(image)

    # 還原影像格式
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        # 繪製骨架
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 根據參數執行動作偵測
        detect_action(image, results.pose_landmarks.landmark, action_type)

    # 顯示影像
    cv2.imshow('Detection', image)

    # 按 'q' 鍵退出
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

# 釋放資源
cap.release()
cv2.destroyAllWindows()
