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

screen_width=root.winfo_screenwidth()
screen_height=root.winfo_screenheight()

cap = cv2.VideoCapture(0)
cap.set(3, screen_width)  # 设置摄像头的宽度为 screen_width
cap.set(4, screen_height)  # 设置摄像头的高度为 screen_height

detector = HandDetector(detectionCon=0.8, maxHands=1)

class SnakeGameClass:
    def __init__(self, pathFood, screen_width, screen_height):
        self.points = []  # 蛇的所有点
        self.lengths = []  # 每个点之间的距离
        self.currentLength = 0  # 蛇的总长度
        self.allowedLength = 150  # 总允许的长度
        self.previousHead = 0, 0  # 上一头点

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation(screen_width, screen_height)

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self, screen_width, screen_height):
        # 随机生成食物的位置，确保不会超出屏幕范围
        self.foodPoint = random.randint(100, screen_width - 100), random.randint(100, screen_height - 100)

    def update(self, imgMain, currentHead):

        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 400],
                                scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 550],
                                scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # 蛇身长度缩减
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # 检查蛇是否吃到食物
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation(screen_width, screen_height)
                self.allowedLength += 50
                self.score += 1

                # 数据保存
                if grab_upload_data(19) == 0:
                    update_upload_data(19, self.score)
                else:
                    if grab_upload_data(19) < self.score:
                        update_upload_data(19, self.score)

            # 绘制蛇
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)

            # 绘制食物
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                                scale=3, thickness=3, offset=10)

            # 检查碰撞
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= minDist <= 1:
                print("碰撞")
                self.gameOver = True
                self.points = []  # 重置蛇的所有点
                self.lengths = []  # 重置每个点之间的距离
                self.currentLength = 0  # 重置蛇的总长度
                self.allowedLength = 150  # 重置总允许的长度
                self.previousHead = 0, 0  # 重置上一头点
                self.randomFoodLocation(screen_width, screen_height)

        return imgMain

game = SnakeGameClass("Resource/img/newgame/Donut.png", screen_width, screen_height)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)

    cv2.imshow("Gluttonous Snack", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
    elif key == ord(' '):
        break
cap.release()
cv2.destroyAllWindows()