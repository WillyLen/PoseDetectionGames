import cv2
import mediapipe as mp
import time

# Mediapipe 初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 定義基準高度
baseline_height = None
last_raise_time = None

# 啟動攝影機
cap = cv2.VideoCapture(0)

print("請將攝影機對準全身，按下 'q' 結束程式")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 翻轉影像（可選，讓使用者看起來正常）
    frame = cv2.flip(frame, 1)

    # 轉為 RGB 並偵測姿勢
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # 繪製姿勢關鍵點
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 提取腳踝和膝蓋的關鍵點座標
        left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
        left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]

        # 初始化基準高度為膝蓋高度（或手動設定固定值）
        if baseline_height is None:
            baseline_height = (left_knee.y + right_knee.y) / 2

        # 判斷腳踝是否抬起超過基準
        left_raised = left_ankle.y < baseline_height
        right_raised = right_ankle.y < baseline_height

        # 如果兩腳都抬起
        if left_raised and right_raised:
            current_time = time.time()
            if last_raise_time is not None:
                interval = current_time - last_raise_time
                print(f"兩腳抬起間隔: {interval:.2f} 秒")
            last_raise_time = current_time

    # 顯示影像
    cv2.imshow("Foot Raise Detection", frame)

    # 按 'q' 結束程式
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 清理資源
cap.release()
cv2.destroyAllWindows()
