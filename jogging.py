import cv2
import mediapipe as mp
import time

# 初始化 Mediapipe Pose 模型
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 遊戲參數
GAME_DURATION = 30  # 遊戲時間 (秒)
SPEED_THRESHOLD = 0.5  # 速度閾值 (越小越慢)

# 計時器和分數
start_time = time.time()
score = 0
last_position = None

# 啟動攝像頭
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 水平翻轉以鏡像顯示
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 偵測姿勢
    results = pose.process(rgb_frame)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # 取得腳踝座標 (作為判斷依據)
        left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
        current_position = (left_ankle.y + right_ankle.y) / 2
        
        # 計算速度
        if last_position is not None:
            speed = abs(current_position - last_position) / (time.time() - last_time)
            if speed < SPEED_THRESHOLD:
                score += 1  # 合格，加分
            else:
                score -= 1  # 太快，扣分
        
        last_position = current_position
        last_time = time.time()
    
    # 顯示分數和時間
    elapsed_time = time.time() - start_time
    cv2.putText(frame, f'Score: {score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Time: {int(GAME_DURATION - elapsed_time)}s', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Slow Run Game', frame)
    
    # 遊戲時間結束
    if elapsed_time >= GAME_DURATION:
        print(f'Game Over! Your final score is: {score}')
        break
    
    if cv2.waitKey(5) & 0xFF == ord(' '):
        break

cap.release()
cv2.destroyAllWindows()
