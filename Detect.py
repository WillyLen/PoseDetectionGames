import cv2
import sys
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np

GameInfo = [
        {"code": "1", "line_height": "-10", "text": "檢測雙肩是否有節點"},{"code": "2", "line_height": "-10", "text": "檢測雙肩是否有節點"},
        {"code": "3", "line_height": "432", "text": "檢測膝蓋節點蹲下後是否能碰到紅線"},{"code": "4", "line_height": "432", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "5", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "6", "line_height": "144", "text": "檢測雙手向上舉直後是否能超過紅線"},
        {"code": "7", "line_height": "432", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},{"code": "8", "line_height": "114", "text": "檢測雙手向上舉直後是否能超過紅線"},
        {"code": "9", "line_height": "144", "text": "檢測雙手向上舉直後是否能超過紅線"},{"code": "10", "line_height": "576", "text": "檢測膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "11", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "12", "line_height": "-10", "text": "檢測骨盆兩側是否有節點"},
        {"code": "13", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "14", "line_height": "432", "text": "檢測骨盆兩側是否有節點及膝蓋節點在抬腳及放下時，是否在線的上下方"},
        {"code": "15", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "16", "line_height": "-10", "text": "檢測雙肩是否有節點"},
        {"code": "17", "line_height": "-10", "text": "檢測雙手是否有節點"},{"code": "18", "line_height": "-10", "text": "檢測雙手是否有節點"},
        {"code": "19", "line_height": "-10", "text": "檢測雙眼是否有節點"},{"code": "20", "line_height": "-10", "text": "檢測雙手是否有節點"},
    ]

code = sys.argv[1] # game-code
pos1 = int(sys.argv[2])  # 第一个点的 ID，例如左肩
pos2 = int(sys.argv[3])  # 第二个点的 ID，例如右肩

# 查找对应的 GameInfo 项
game_info = next((item for item in GameInfo if item["code"] == code), None)

if game_info:
    line_height = int(game_info["line_height"])
    text = game_info["text"]
else:
    print("未找到對應之遊戲訊息")

def show_camera_with_pose():
    # 初始化 MediaPipe 姿态检测
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose()

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 设置中文字体路径
    font_path = "/System/Library/Fonts/STHeiti Medium.ttc"  # macOS 示例路径，请修改为 Windows 的中文字体路径
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
            draw.text((0, 50), text, font=font, fill=(255, 0, 0))  # 红色文字
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
show_camera_with_pose()
