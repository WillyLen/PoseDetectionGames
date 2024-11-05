import cv2
import sys
import mediapipe as mp

pos1 = int(sys.argv[1])
pos2 = int(sys.argv[2])

def show_camera_with_pose():

    # 初始化MediaPipe姿态检测
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose()

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # 设置宽度
    cap.set(4, 720)   # 设置高度

    while True:
        # 读取摄像头画面
        success, img = cap.read()
        if not success:
            break

        # 翻转画面（方便用户观看）
        img = cv2.flip(img, 1)

        # 转换颜色格式为RGB，以符合MediaPipe输入要求
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        # 检测到姿势则绘制关节点
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                lmlist = []
                bx, by = int(lm.x * w), int(lm.y * h)
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 10, (205, 0, 0), cv2.FILLED)
                lmlist.append([id, cx, cy])

                # Left_Shoulder
                if lmlist[0][0] == pos1:
                    cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                    x1 = lmlist[0][1]
                    y1 = lmlist[0][2]
                # Right_Shoulder
                elif lmlist[0][0] == pos2:
                    cv2.circle(img, (bx, by), 15, (0, 255, 0), cv2.FILLED)
                    x2 = lmlist[0][1]
                    y2 = lmlist[0][2]

        # 显示带有节点的摄像头画面
        cv2.imshow("Camera with Pose Detection", img)

        # 按空格键退出
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

# 调用函数显示影像和姿态检测节点
show_camera_with_pose()

