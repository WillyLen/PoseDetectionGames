import cv2
import mediapipe as mp
import time

# 初始化 Mediapipe Pose 模型
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# 狀態變數
is_squatting = False  # 當前是否在蹲下狀態
squat_count = 0       # 蹲下次數
start_time = None     # 計時器起始時間
duration = 15         # 計時器持續時間（秒）

# 判斷蹲下的閾值
HIP_KNEE_THRESHOLD = 50  # 髖部和膝蓋之間的 y 軸距離閾值

# 啟動視訊捕捉
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 翻轉畫面，方便用戶觀看
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # 設定開始時間
        if start_time is None:
            start_time = time.time()

        # 檢測人體關鍵點
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
            shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            # 計算髖部與膝蓋的 y 軸差異
            hip_y = hip.y * frame.shape[0]
            knee_y = knee.y * frame.shape[0]
            shoulder_y = shoulder.y * frame.shape[0]

            if (hip_y - knee_y) < HIP_KNEE_THRESHOLD and not is_squatting:
                is_squatting = True  # 檢測到蹲下
            elif (hip_y - knee_y) > HIP_KNEE_THRESHOLD and is_squatting:
                is_squatting = False
                squat_count += 1  # 完成一次蹲下

        # 顯示蹲下次數與剩餘時間
        elapsed_time = time.time() - start_time
        remaining_time = max(duration - elapsed_time, 0)
        cv2.putText(frame, f"Squats: {squat_count}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Time: {int(remaining_time)}s", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # 畫出關鍵點
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 顯示視訊畫面
        cv2.imshow('Squat Counter', frame)

        # 時間到，結束計數
        if elapsed_time >= duration:
            print(f"15秒內蹲下次數：{squat_count}")
            break

        # 按 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

cap.release()
cv2.destroyAllWindows()
