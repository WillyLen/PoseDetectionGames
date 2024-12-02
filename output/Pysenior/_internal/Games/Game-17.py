import cvzone
import tkinter as tk
from PIL import Image, ImageTk
from cvzone.HandTrackingModule import HandDetector
from collections import deque
import numpy as np
import os
import math
import sys
import pygame
import mediapipe as mp
import random
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv

root = tk.Tk()
root.withdraw()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

def start_screen():
    """顯示開始畫面並等待按下「Enter」鍵以開始遊戲。"""
    imgStart = cv2.imread("Resource/img/newgame/Background.png")
    imgStart = cv2.resize(imgStart, (screen_width, screen_height))
    if imgStart is None:
        print("Error: 無法載入開始畫面圖片。請檢查圖片路徑。")
        return

    while True:
        # 顯示開始畫面
        cv2.putText(imgStart, "Press 'Enter' to Start", (int(screen_width/4), int(screen_height/2)), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
        cv2.imshow("tabletennis", imgStart)
        key = cv2.waitKey(1)
        if key == 13:  # Enter鍵開始遊戲
            break
    cv2.destroyWindow("tabletennis")

start_screen()  # 首次顯示開始畫面

### 遊戲參數 ###
x = grab_game_data(9)
y = grab_game_data(10)

cap = cv2.VideoCapture(0)
cap.set(3, screen_width)#1280
cap.set(4, screen_height)#720

# 加載圖片
imgBackground = cv2.imread("Resource/img/newgame/Background.png")
imgGameOver = cv2.imread("Resource/img/newgame/gameOver.png")
imgBall = cv2.imread("Resource/img/newgame/Ball.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("Resource/img/newgame/bat1.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("Resource/img/newgame/bat2.png", cv2.IMREAD_UNCHANGED)
font_name = os.path.join("Resource/font.ttf")

# 手部偵測器
detector = HandDetector(detectionCon=0.8, maxHands=2)

# 遊戲變數
ballPos = [100, 100]
speedX = x
speedY = y
gameOver = False
score = [0, 0]

while True:

    _, img = cap.read()
    img = cv2.flip(img, 1)
    imgRaw = img.copy()

    # 偵測手部及其位置
    hands, img = detector.findHands(img, flipType=False)

    # 調整並融合背景
    imgBackground = cv2.resize(imgBackground, (img.shape[1], img.shape[0]))
    if len(img.shape) == 3 and len(imgBackground.shape) == 2:
        imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 2 and len(imgBackground.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = cv2.addWeighted(img, 0.2, imgBackground, 0.8, 0)

    speedX = np.clip(speedX, -15, 15)
    speedY = np.clip(speedY, -15, 15)

    # 偵測手部並疊加球拍
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            y1 = y - h1 // 2
            y1 = np.clip(y1, 20, screen_height-h1-20)

            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (int(screen_width*0.046875), y1))
                if screen_width*0.046875 < ballPos[0] < screen_width*0.046875 + w1 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] += 30
                    score[0] += 1

            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (int(screen_width*0.9336), y1))
                if screen_width*0.9336 - 50 < ballPos[0] < screen_width*0.9336 and y1 < ballPos[1] < y1 + h1:
                    speedX = -speedX
                    ballPos[0] -= 30
                    score[1] += 1

    # 遊戲結束條件
    if ballPos[0] < screen_width * 0.03125 or ballPos[0] > screen_width * 0.9375:
        gameOver = True

    if gameOver:
        img = imgGameOver
        cv2.putText(img, str(score[1] + score[0]).zfill(2), (585, 360), cv2.FONT_HERSHEY_COMPLEX, 2.5, (200, 0, 200), 5)
        cv2.putText(img, "Press 'Enter' to Restart", (300, 500), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)

    else:
        # 球移動
        if ballPos[1] >= screen_height * 0.7 or ballPos[1] <= 10:
            speedY = -speedY

        ballPos[0] += speedX
        ballPos[1] += speedY

        # 繪製球
        img = cvzone.overlayPNG(img, imgBall, ballPos)

        # 顯示分數
        cv2.putText(img, str(score[0]), (int(screen_width/4), 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, str(score[1]), (int(screen_width*3/4), 650), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        # 更新分數數據
        point = score[0]+score[1]
        if grab_upload_data(18) == 0 or grab_upload_data(18) < point:
            update_upload_data(18, point)

    cv2.imshow("tabletennis", img)
    key = cv2.waitKey(1)

    if key == 13 and gameOver:  # Enter鍵重新開始
        # 重設遊戲
        ballPos = [100, 100]
        speedX = x
        speedY = y
        gameOver = False
        score = [0, 0]
        imgGameOver = cv2.imread("Resource/img/newgame/gameOver.png")
        start_screen()  # 顯示開始畫面重新開始

    elif key == ord(' '):  # 空白鍵退出
        break

cap.release()
cv2.destroyAllWindows()