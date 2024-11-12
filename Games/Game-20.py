import cvzone
from PIL import Image, ImageTk
from cvzone.HandTrackingModule import HandDetector
from collections import deque
import numpy as np
import os
import math
import tkinter as tk
import sys
import pygame
import mediapipe as mp
import random
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import update_game_data, grab_game_data
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv

root = tk.Tk()
root.withdraw()

quit = False
cap = cv2.VideoCapture(0)
screen_width=root.winfo_screenwidth()
screen_height=root.winfo_screenheight()
cap.set(3, screen_width)  # 设置摄像头的宽度为 screen_width
cap.set(4, screen_height)  # 设置摄像头的高度为 screen_height
# Blue Green Yellow
penColorHSV = [[86, 121, 205, 111, 245, 255],
                [46, 78, 204, 71, 255, 255],
                [22, 70, 214, 31, 255, 255]]

penColorBGR = [[255, 0, 0],
                [0, 255, 0],
                [0, 255, 255]]

# [x, y, colorId]
drawPoints = []

def findPen(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    for i in range(len(penColorHSV)):
        lower = np.array(penColorHSV[i][:3])
        upper = np.array(penColorHSV[i][3:6])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.resize(mask, (1280, 720))
        # result = cv2.bitwise_and(img, img, mask=mask)
        penx, peny = findContour(mask)
        cv2.circle(imgContour, (penx, peny), 10, penColorBGR[i], cv2.FILLED)
        if peny != -1:
            drawPoints.append([penx, peny, i])
    # cv2.imshow('result', result)

def findContour(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = -1, -1, -1, -1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            peri = cv2.arcLength(cnt, True)
            vertices = cv2.approxPolyDP(cnt, peri * 0.02, True)
            x, y, w, h = cv2.boundingRect(vertices)

    return 1280 - (x + w // 2), y

def draw(drawpoints):
    for point in drawpoints:
        cv2.circle(imgContour, (point[0], point[1]), 30, penColorBGR[point[2]], cv2.FILLED)

while True:
    ret, frame = cap.read()
    if ret:
        imgContour = frame.copy()
        imgContour = cv2.flip(imgContour, 1)
        imgContour = cv2.resize(imgContour, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        # cv2.imshow('video', frame)
        findPen(frame)
        draw(drawPoints)
        cv2.imshow('虛擬筆', imgContour)
    else:
        break
    if cv2.waitKey(1) == ord(' '):
        quit = True
        break
cap.release()
cv2.destroyAllWindows()