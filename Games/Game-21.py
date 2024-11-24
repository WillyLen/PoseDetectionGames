import cv2
import mediapipe as mp
import numpy as np

# 初始化 Mediapipe 的 Face Mesh 模組
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# 計算眼睛縱橫比（EAR）
def calculate_ear(eye_landmarks):
    # 根據眼睛的 6 個特定點計算 EAR
    vertical1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    vertical2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

# 閾值與眨眼計數相關變數
EAR_THRESHOLD = 0.25  # EAR 小於此值判定眨眼
CONSECUTIVE_FRAMES = 2  # 至少連續 N 幀滿足條件才判定為一次眨眼
blink_count = 0
frame_counter = 0

# 開啟攝影機
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame capture failed.")
        break

    # 翻轉影像並轉換為 RGB 格式
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 偵測臉部特徵
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            h, w, _ = frame.shape

            # 提取左眼和右眼的座標點
            left_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [362, 385, 387, 263, 373, 380]])
            right_eye = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in [33, 160, 158, 133, 153, 144]])

            # 計算 EAR
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0

            # 判斷是否眨眼
            if ear < EAR_THRESHOLD:
                frame_counter += 1
            else:
                if frame_counter >= CONSECUTIVE_FRAMES:
                    blink_count += 1
                frame_counter = 0

            # 繪製眼睛特徵點
            cv2.polylines(frame, [left_eye.astype(np.int32)], True, (255, 0, 0), 1)
            cv2.polylines(frame, [right_eye.astype(np.int32)], True, (255, 0, 0), 1)

    # 顯示眨眼次數
    cv2.putText(frame, f"Blinks: {blink_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # 顯示結果
    cv2.imshow('Blink Detection', frame)

    # 按下 'q' 鍵退出
    if cv2.waitKey(1) & 0xFF in (ord(' '), ord('q')):
        break

cap.release()
cv2.destroyAllWindows()
