import cv2
import mediapipe as mp
import time

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
                        current_stage = "START"

        # 顯示影像
        cv2.putText(image, f"Best Time: {best_time:.2f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Foot Detection", image)

        # 按 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
