import pygame                    # 用於遊戲的視覺效果和聲音
import random                    # 用於生成隨機位置的石頭和金幣
import cv2                       # 用於開啟攝像頭來捕捉玩家動作
import mediapipe as mp           # 用於肢體追蹤，偵測玩家的肩膀位置
import os                        # 用於文件操作（例如讀取/保存遊戲數據）
import sys                       # 提供對Python運行時環境的訪問

# 添加當前腳本所在目錄的上級目錄到系統路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 從自定義工具模組導入函數
from Utils import (
    update_game_data, grab_game_data, update_upload_data, grab_upload_data,
    update_verify_data, grab_verify_data, grab_verify_data_int,
    get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key,
    encrypt, encrypt_csv, decrypt, decrypt_csv
)

# 嘗試初始化 Mediapipe 的肢體偵測功能
try:
    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()
except Exception as e:
    print("Mediapipe 模組初始化失敗！請確認模組是否正確安裝。\n錯誤訊息:", str(e))
    sys.exit()

# 嘗試開啟攝像頭
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("無法讀取攝像頭！請檢查設備是否正確連接或被其他程序佔用。")
    sys.exit()

### 遊戲參數設置 ###
dropspeed = grab_game_data(2)   # 石頭掉落速度
quantity = grab_game_data(3)   # 石頭的數量
FPS = 60                       # 每秒幀數
countdown_start_time = 0       # 倒數計時初始時間

# 根據樣式參數設定背景圖片資料夾路徑
style = grab_game_data(1)
if style == 0 or style is None:
    custom = "Resource/img/普通"
elif style == 1:
    custom = "Resource/img/特別"
elif style == 2:
    custom = "Resource/img/草地"
elif style == 3:
    custom = "Resource/img/夜空"
elif style == 4:
    custom = "Resource/img/岩壁"
elif style == 5:
    custom = "Resource/img/海洋"

# 初始化遊戲，設置視窗大小和標題
pygame.init()
info = pygame.display.Info()
WIDTH = info.current_w               # 獲取螢幕寬度
HEIGHT = info.current_h              # 獲取螢幕高度
SCR = (WIDTH, HEIGHT * 0.95)         # 設定遊戲視窗大小
pygame.mixer.init()                  # 初始化音樂混音器
screen = pygame.display.set_mode(SCR)  # 創建遊戲視窗
pygame.display.set_caption("躲隕石")  # 設定視窗標題
clock = pygame.time.Clock()          # 初始化遊戲時鐘

# 確保背景圖片加載成功
try:
    background_img = pygame.image.load(os.path.join(custom, "Bg_1.jpg")).convert()
except Exception as e:
    print("背景圖片讀取失敗！請確認路徑是否正確。\n錯誤訊息:", str(e))
    sys.exit()

# 加載其他資源
pygame.mixer.music.load(os.path.join("Resource/sound", "Msc_1_1.ogg"))
pygame.mixer.music.set_volume(0.7)
player_img = pygame.image.load(os.path.join(custom, "Cha_1.png")).convert()
rock_img = pygame.image.load(os.path.join(custom, "Obj_1_1.png")).convert()
heart_img = pygame.image.load(os.path.join(custom, "Obj_1_2.png")).convert()
timeboard_img = pygame.image.load(os.path.join("Resource/img/普通", "timeboard.png")).convert()

# 圖片大小調整
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
timeboard_img = pygame.transform.scale(timeboard_img, (WIDTH / 5, HEIGHT / 6))
timeboard_img.set_colorkey((255, 255, 255))  # 設置透明背景
font_name = os.path.join("Resource/font.ttf")  # 字型檔案

# 更多遊戲邏輯...

# 程式結束時釋放資源
pygame.quit()
cap.release()  # 釋放攝像頭
cv2.destroyAllWindows()  # 關閉所有 OpenCV 視窗