import tkinter as tk
from tkinter import Label, Button
import cvzone
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
import time
import csv
import hashlib
import uuid
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils import update_game_data, grab_game_data, update_upload_data, grab_upload_data, grab_upload_data_float
from Utils import update_verify_data, grab_verify_data, grab_verify_data_int
from Utils import get_mac, hash_mac, hash_str, generate_key, hash_x, hash_key 
from Utils import encrypt, encrypt_csv, decrypt, decrypt_csv
from Upload import upload_data
from Games import start_game_1,start_game_2,start_game_3,start_game_4,start_game_5,start_game_6,start_game_7,start_game_8,start_game_9,start_game_10
from Games import start_game_11,start_game_12,start_game_13,start_game_14,start_game_15,start_game_16,start_game_17,start_game_18,start_game_19,start_game_20
from new_detect import detect
from Detect import leg_up_detect, squatting_detect, show_camera_with_pose

ENCRYPTKEY = "032118800"

MAGIC_HEADER = b'ENCRYPTEDFILE'

global RELOADING
RELOADING = False

games = [
    {"code": "1", "record_code": "2", "name": "躲隕石", "scene_image": "Game_1_1.png", "intro_image": "Act_1_1.png", "intro_text": "移動身體來操控人物躲避物品，時間過越久分數越高","detect_code": "24" ,"detect_text": "右跨步距離: "},
    {"code": "2", "record_code": "3", "name": "接金幣", "scene_image": "Game_1_2.png", "intro_image": "Act_1_2.png", "intro_text": "移動身體來操控人物接金幣，時間到接越多顆分數越高","detect_code": "25" ,"detect_text": "左跨步距離: "},
    {"code": "3", "record_code": "4", "name": "挖蘿蔔", "scene_image": "Game_1_3.png", "intro_image": "Act_1_3.png", "intro_text": "身體來回蹲下操控鏟子挖出蘿蔔得分","detect_code": "23" ,"detect_text": "蹲下起來時間: "},
    {"code": "4", "record_code": "5", "name": "追趕跳碰", "scene_image": "Game_1_4.png", "intro_image": "Act_1_4.png", "intro_text": "雙腳保持頻率抬高，速度加快，反之減速，被狼追到就會結束遊戲","detect_code": "22" ,"detect_text": "抬腳速率: "},
    {"code": "5", "record_code": "6", "name": "抓蝴蝶", "scene_image": "Game_1_5.png", "intro_image": "Act_1_5.png", "intro_text": "雙手即網子，用兩個網子捕捉蝴蝶","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "6", "record_code": "7", "name": "鬆土", "scene_image": "Game_2_1.png", "intro_image": "Act_2_1.png", "intro_text": "雙手重複舉高放下，時限內去除越多稻草分數越高","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "7", "record_code": "8", "name": "踩水車", "scene_image": "Game_2_2.png", "intro_image": "Act_2_2.png", "intro_text": "當畫面出現左腳時抬左腳，反之右腳，每次踏步農田都會產生變化","detect_code": "26" ,"detect_text": "最高右抬腳距離: "},
    {"code": "8", "record_code": "9", "name": "施肥", "scene_image": "Game_2_3.png", "intro_image": "Act_2_3.png", "intro_text": "雙手向上舉起，每做一次就會長出一片稻穗","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "9", "record_code": "10", "name": "收割", "scene_image": "Game_2_4.png", "intro_image": "Act_2_4.png", "intro_text": "雙手向上舉起，每做一次就會割下一片稻穗","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "10", "record_code": "11", "name": "椿米", "scene_image": "Game_2_5.png", "intro_image": "Act_2_5.png", "intro_text": "雙腳張開與肩同寬，將腿部抬高，再放下","detect_code": "27" ,"detect_text": "最高左抬腳距離: "},
    {"code": "11", "record_code": "12", "name": "刺氣球", "scene_image": "Game_3_1.png", "intro_image": "Act_3_1.png", "intro_text": "當氣球出現於腳下時，可舉腳踩踏，若身體過於傾斜，人物將會跌倒","detect_code": "29" ,"detect_text": "右最遠臂展: "},
    {"code": "12", "record_code": "13", "name": "接雞蛋", "scene_image": "Game_3_2.png", "intro_image": "Act_3_2.png", "intro_text": "移動骨盆來控制接雞蛋的位置，一個一分","detect_code": "31" ,"detect_text": "髖關節最遠移動距離: "},
    {"code": "13", "record_code": "14", "name": "接果子", "scene_image": "Game_3_3.png", "intro_image": "Act_3_3.png", "intro_text": "身體呈側身，將手臂伸往前，控制籃子接果實，需再回到綠點，才能出現下一個","detect_code": "30" ,"detect_text": "左最遠臂展: "},
    {"code": "14", "record_code": "15", "name": "踩氣球", "scene_image": "Game_3_4.png", "intro_image": "Act_3_4.png", "intro_text": "當氣球出現於腳下時，可舉腳踩踏，若身體過於傾斜，人物將會跌倒","detect_code": "27" ,"detect_text": "最高左抬腳距離: "},
    {"code": "15", "record_code": "16", "name": "跳舞機", "scene_image": "Game_3_5.png", "intro_image": "Act_3_5.png", "intro_text": "用雙手伸向紅箭頭之位置後，回到中心綠點，才會有下一個紅箭頭出現","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "16", "record_code": "17", "name": "太空戰", "scene_image": "Game_4_1.png", "intro_image": "Act_4_1.png", "intro_text": "身體控制飛船左右，舉手發射子彈","detect_code": "28" ,"detect_text": "最高臂展: "},
    {"code": "17", "record_code": "18", "name": "桌球", "scene_image": "Game_4_2.png", "intro_image": "Act_4_2.png", "intro_text": "手掌控制擋板上下，球進結束遊戲，按下空白鍵結束"},
    {"code": "18", "record_code": "19", "name": "貪食蛇", "scene_image": "Game_4_3.png", "intro_image": "Act_4_3.png", "intro_text": "手掌控制擋板上下，球進結束遊戲，按下空白鍵結束"},
    {"code": "19", "record_code": "20", "name": "跑酷鳥", "scene_image": "Game_4_4.png", "intro_image": "Act_4_4.png", "intro_text": "頭部控制飛鳥上下移動，每過一個階段速度將會提升，碰到水管遊戲結束"},
    {"code": "20", "record_code": "21", "name": "射飛鏢", "scene_image": "Game_4_5.png", "intro_image": "Act_4_5.png", "intro_text": "眨眼就能發射飛鏢，不觸碰到球發射10根就獲勝"},
]

start_games = {
    "1": start_game_1,"2": start_game_2,"3": start_game_3,"4": start_game_4,"5": start_game_5,
    "6": start_game_6,"7": start_game_7,"8": start_game_8,"9": start_game_9,"10": start_game_10,
    "11": start_game_11,"12": start_game_12,"13": start_game_13,"14": start_game_14,"15": start_game_15,
    "16": start_game_16,"17": start_game_17,"18": start_game_18,"19": start_game_19,"20": start_game_20
}


def main():

    class PGManager:
        def __init__(self, root):
            self.root = root
            self.current_page = None

        def show_page(self, page_class, *args):
            # 清理当前UI页面
            if self.current_page is not None:
                self.current_page.destroy()

            # 切换到新的UI页面
            if page_class == GameMenuPage:
                self.current_page = page_class(self.root, games, *args)
            else:
                self.current_page = page_class(self.root, *args)
            self.current_page.grid(row=0, column=0, sticky="nsew")

    class FirstLoginPage(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master

            # 標籤按鈕
            self.image_path1 = "Resource/img/普通/image1.png"
            self.image1 = Image.open(self.image_path1)
            self.image1 = self.image1.resize((1000, 350))
            self.photo1 = ImageTk.PhotoImage(self.image1)
            self.pysenior1 = tk.Button(self, image=self.photo1)

            # 登入系統標籤
            self.label_1 = tk.Label(self, text='請輸入Email及金鑰解鎖系統', font=('Arial', 25), bg='red')

            # MAC標籤
            self.label_3 = tk.Label(self, text=f"{grab_verify_data(6)}", font=('Arial', 18), bg='purple')

            # 帳號標籤
            self.label_2 = tk.Label(self, text='Key： ', font=('Arial', 18))
            self.label_4 = tk.Label(self, text='Email： ', font=('Arial', 18))
            self.label_5 = tk.Label(self, text='據點名稱 ', font=('Arial', 18))


            # 輸入格
            self.StringVar1 = tk.StringVar()
            self.entry1 = tk.Entry(self, textvariable=self.StringVar1, width=50, bg="white", fg="black")
            self.StringVar2 = tk.StringVar()
            self.entry2 = tk.Entry(self, textvariable=self.StringVar2, width=50, bg="white", fg="black")
            self.StringVar3 = tk.StringVar()
            self.entry3 = tk.Entry(self, textvariable=self.StringVar3, width=50, bg="white", fg="black")

            # 背景
            self.image_path_bg = "Resource/img/普通/background.jpg"
            self.image_bg = Image.open(self.image_path_bg)
            self.image_bg = self.image_bg.resize((1280, 800))
            self.photo_bg = ImageTk.PhotoImage(self.image_bg)
            self.game_bg = tk.Label(self, image=self.photo_bg)
            self.game_bg.place(relwidth=1, relheight=1)
            self.game_bg.lower()

            # 登入按鈕
            self.login_button = tk.Button(self, text="確認", font=('Arial', 18), command=self.comfirm)

            # 版面編輯
            self.label_1.grid(row=0, sticky="n", padx=10, pady=5)
            self.pysenior1.grid(row=1, column=0, sticky="n", padx=10, pady=5)
            self.label_2.grid(row=2, column=0, sticky="w", padx=10, pady=5)
            self.entry1.grid(row=2, column=0, sticky="e", padx=10, pady=5)
            self.label_4.grid(row=3, column=0, sticky="w", padx=10, pady=5)
            self.entry2.grid(row=3, column=0, sticky="e", padx=10, pady=5)
            self.label_5.grid(row=4, column=0, sticky="w", padx=10, pady=5)
            self.entry3.grid(row=4, column=0, sticky="e", padx=10, pady=5)
            self.login_button.grid(row=5, column=0, sticky="n", padx=10, pady=5)
            self.label_3.grid(row=6, column=0, sticky="sw", padx=10, pady=5)
            
        def comfirm(self):
            global key
            key = self.StringVar1.get()
            email = self.StringVar2.get()
            location = self.StringVar3.get()
            print(key[0:9] + "***" + key[9:12] + "***" + key[12:])
            update_verify_data(0,key[9:12])
            update_verify_data(1,key[0:9])
            update_verify_data(5,email)
            update_verify_data(6,hash_mac(get_mac()))
            update_verify_data(7,location)
            print(hash_key(str((grab_verify_data_int(2) + 1))))
            if key[12:] == hash_key(str((grab_verify_data_int(2) + 1))):
                update_verify_data(2,str((grab_verify_data_int(2) + 1)))
                update_verify_data(3,key[12:])
                update_verify_data(4,365)
                encrypt_csv('Data/verify.csv', ENCRYPTKEY)
                pg_manager.show_page(LoginPage)
            else:
                self.label_1['text'] = 'Key或email錯誤！ 請再輸入一次'

    class InitPage(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master

            # 標籤按鈕
            self.image_path = "Resource/img/普通/image1.png"
            self.image = Image.open(self.image_path)
            self.image = self.image.resize((1000, 350))
            self.photo = ImageTk.PhotoImage(self.image)
            self.pysenior = tk.Button(self, image=self.photo)

            # 登入系統標籤
            self.label_1 = tk.Label(self, text='請輸入金鑰解鎖系統', font=('Arial', 25), bg='red')

            # MAC標籤
            self.label_3 = tk.Label(self, text=f"{grab_verify_data(7)}", font=('Arial', 18), bg='purple')

            # 帳號標籤
            self.label_2 = tk.Label(self, text='Key： ', font=('Arial', 18))

            # 輸入格
            self.StringVar = tk.StringVar()
            self.entry = tk.Entry(self, textvariable=self.StringVar, width=30, bg="white", fg="black")

            # 背景
            self.image_path_bg = "Resource/img/普通/background.jpg"
            self.image_bg = Image.open(self.image_path_bg)
            self.image_bg = self.image_bg.resize((1280, 800))
            self.photo_bg = ImageTk.PhotoImage(self.image_bg)
            self.game_bg = tk.Label(self, image=self.photo_bg)
            self.game_bg.place(relwidth=1, relheight=1)
            self.game_bg.lower()

            # 登入按鈕
            self.login_button = tk.Button(self, text="確認", font=('Arial', 18), command=self.comfirm)

            # 版面編輯
            self.label_1.grid(row=0, column=0, padx=10, pady=5)
            self.pysenior.grid(row=1, column=0, padx=10, pady=5)
            self.label_2.grid(row=2, column=0, padx=10, pady=5)
            self.entry.grid(row=3, column=0, padx=10, pady=5)
            self.login_button.grid(row=4, column=0, padx=10, pady=5)
            self.label_3.grid(row=5, column=0, sticky="sw", padx=10, pady=5)
            
        def comfirm(self):
            global key
            key = self.StringVar.get()
            if key == hash_key(str((grab_verify_data_int(2) + 1))):
                update_verify_data(2,str((grab_verify_data_int(2) + 1)))
                update_verify_data(3,key)
                update_verify_data(4,365)
                encrypt_csv('Data/verify.csv', ENCRYPTKEY)
                pg_manager.show_page(LoginPage)
            else:
                self.label_1['text'] = 'Key錯誤！ 請再輸入一次'
    
    class LoginPage(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master

            decrypt_csv('Data/verify.csv', ENCRYPTKEY)

            # 標籤按鈕
            self.image_path = "Resource/img/普通/pysenior.png"
            self.image = Image.open(self.image_path)
            self.image = self.image.resize((1000, 350))
            self.photo = ImageTk.PhotoImage(self.image)
            self.pysenior = tk.Button(self, image=self.photo)

            # 登入系統標籤
            self.label_1 = tk.Label(self, text='剩餘使用次數 : ' + grab_verify_data(4), font=('Arial', 18), bg='red')

            # MAC標籤
            self.label_3 = tk.Label(self, text=f"{grab_verify_data(6)}", font=('Arial', 18), bg='purple')

            #據點名稱標籤
            self.label_4 = tk.Label(self, text=f"{grab_verify_data(7)}", font=('Arial', 18), bg='purple')

            # 帳號標籤
            self.label_2 = tk.Label(self, text='使用者名稱 ： ', font=('Arial', 18), bg="purple")

            # 輸入格
            self.StringVar = tk.StringVar()
            self.entry = tk.Entry(self, textvariable=self.StringVar, width=30, bg="white", fg="black")

            # 背景
            self.image_path_bg = "Resource/img/普通/background.jpg"
            self.image_bg = Image.open(self.image_path_bg)
            self.image_bg = self.image_bg.resize((1280, 800))
            self.photo_bg = ImageTk.PhotoImage(self.image_bg)
            self.game_bg = tk.Label(self, image=self.photo_bg)
            self.game_bg.place(relwidth=1, relheight=1)
            self.game_bg.lower()

            # 登入按鈕
            self.login_button = tk.Button(self, text="登入", font=('Arial', 18), command=self.login)
            self.reigster_button = tk.Button(self, text="註冊", font=('Arial', 18), command=self.register)

            # 版面編輯
            self.label_1.grid(row=0, column=0, padx=10, pady=5)
            self.pysenior.grid(row=1, column=0, padx=10, pady=5)
            self.label_2.grid(row=2, column=0, padx=10, pady=5)
            self.entry.grid(row=3, column=0, padx=10, pady=5)
            self.login_button.grid(row=4, column=0, padx=10, pady=5)
            self.reigster_button.grid(row=5, column=0, padx=10, pady=5)
            self.label_3.grid(row=6, column=0, sticky="sw", padx=10, pady=5)
            self.label_4.grid(row=6, column=0, sticky="se", padx=10, pady=5)
       
        def login(self):
            global RELOADING
            mackey = hash_mac(get_mac())
            if mackey == grab_verify_data(6):
                global accountname
                accountname = self.StringVar.get()
                with open('Data/accountname.txt', 'w') as file:
                    file.write(accountname)  # 將 accountname 儲存到 txt 檔案
                with open('Data/game.csv', 'r', encoding='utf-8', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if row and row[0].startswith('#'):
                            continue
                        name = row[0]
                        if accountname == name:
                            if RELOADING == False:
                                update_verify_data(4,str(grab_verify_data_int(4) - 1))
                                RELOADING = True
                            encrypt_csv('Data/verify.csv', ENCRYPTKEY)
                            pg_manager.show_page(StyleChoosePage)
                        else:
                            self.label_1['text'] = '帳號錯誤！ 請再輸入一次'
            else:
                self.label_1['text'] = '遊戲序號與電腦序號不符，請連絡相關單位'
                print(mackey)
                        
        def register(self):
            pg_manager.show_page(RegisterPage)

    class RegisterPage(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master

            # 標籤按鈕
            self.image_path = "Resource/img/普通/pysenior.jpg"
            self.image = Image.open(self.image_path)
            self.image = self.image.resize((1000, 350))
            self.photo = ImageTk.PhotoImage(self.image)
            self.pysenior = tk.Button(self, image=self.photo)

            # 登入系統標籤
            self.label_1 = tk.Label(self, text='Pysenior註冊系統', font=('Arial', 18), bg='purple')

            # 帳號標籤
            self.label_2 = tk.Label(self, text='輸入使用者名稱 ： ', font=('Arial', 18), bg="purple")

            # 輸入格
            self.StringVar = tk.StringVar()
            self.entry = tk.Entry(self, textvariable=self.StringVar, width=30, bg="white", fg="black")

            # 背景
            self.image_path_bg = "Resource/img/普通/background.jpg"
            self.image_bg = Image.open(self.image_path_bg)
            self.image_bg = self.image_bg.resize((1280, 800))
            self.photo_bg = ImageTk.PhotoImage(self.image_bg)
            self.game_bg = tk.Label(self, image=self.photo_bg)
            self.game_bg.place(relwidth=1, relheight=1)
            self.game_bg.lower()

            # 登入按鈕
            self.reigster_button = tk.Button(self, text="註冊", font=('Arial', 18), command=self.register)
        
            # 換頁按鈕&現在頁碼
            self.prev_button = tk.Button(self, text="上一頁", font=('Arial', 18), command=self.prev_page)

            # 版面編輯
            self.label_1.grid(row=0, column=0, padx=10, pady=5)
            self.pysenior.grid(row=1, column=0, padx=10, pady=5)
            self.label_2.grid(row=2, column=0, padx=10, pady=5)
            self.entry.grid(row=3, column=0, padx=10, pady=5)
            self.reigster_button.grid(row=4, column=0, padx=10, pady=5)
            self.prev_button.grid(row=5, column=0, padx=10, pady=5)

        def prev_page(self):
            pg_manager.show_page(LoginPage)

        def register(self):
            accountname = self.StringVar.get()
            location = grab_verify_data(7)

            new_account_upload = [location,accountname,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            new_account_game = [accountname,0,10,10,10,3,3,3,10,10,5,30,2]

            # 將資料追加到 CSV 檔案的最後一行
            with open('Data/upload.csv','a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(new_account_upload)
                print("new_account_upload")
            with open('Data/game.csv','a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(new_account_game)
                self.label_2['text'] = '註冊成功！'

    class StyleChoosePage(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master

            self.choosen = 0
            # 選擇按鈕
            # 1
            self.image_path_1 = "Resource/img/普通/Bg_1.jpg"
            self.image_1 = Image.open(self.image_path_1)
            self.image_1 = self.image_1.resize((350, 200))
            self.photo_1 = ImageTk.PhotoImage(self.image_1)
            self.style_1 = tk.Button(self, image=self.photo_1, command=self.choose0)
            # 2
            self.image_path_2 = "Resource/img/特別/Bg_1.jpg"
            self.image_2 = Image.open(self.image_path_2)
            self.image_2 = self.image_2.resize((350, 200))
            self.photo_2 = ImageTk.PhotoImage(self.image_2)
            self.style_2 = tk.Button(self, image=self.photo_2, command=self.choose1)
            # 3
            self.image_path_3 = "Resource/img/草地/Bg_2.jpg"
            self.image_3 = Image.open(self.image_path_3)
            self.image_3 = self.image_3.resize((350, 200))
            self.photo_3 = ImageTk.PhotoImage(self.image_3)
            self.style_3 = tk.Button(self, image=self.photo_3, command=self.choose2)
            # 4
            self.image_path_4 = "Resource/img/夜空/Bg_1.jpg"
            self.image_4 = Image.open(self.image_path_4)
            self.image_4 = self.image_4.resize((350, 200))
            self.photo_4 = ImageTk.PhotoImage(self.image_4)
            self.style_4 = tk.Button(self, image=self.photo_4, command=self.choose3)
            # 5
            self.image_path_5 = "Resource/img/岩壁/Bg_1.jpg"
            self.image_5 = Image.open(self.image_path_5)
            self.image_5 = self.image_5.resize((350, 200))
            self.photo_5 = ImageTk.PhotoImage(self.image_5)
            self.style_5 = tk.Button(self, image=self.photo_5, command=self.choose4)
            # 6
            self.image_path_6 = "Resource/img/海洋/background.jpg"
            self.image_6 = Image.open(self.image_path_6)
            self.image_6 = self.image_6.resize((350, 200))
            self.photo_6 = ImageTk.PhotoImage(self.image_6)
            self.style_6 = tk.Button(self, image=self.photo_6, command=self.choose5)

            # 背景
            self.image_path_bg = "Resource/img/普通/background.jpg"
            self.image_bg = Image.open(self.image_path_bg)
            self.image_bg = self.image_bg.resize((1280, 800))
            self.photo_bg = ImageTk.PhotoImage(self.image_bg)
            self.game_bg = tk.Label(self, image=self.photo_bg)
            self.game_bg.place(relwidth=1, relheight=1)
            self.game_bg.lower()

            # 遊戲標籤
            self.label_1 = tk.Label(self, text='原始版', font=('Arial', 18))
            self.label_2 = tk.Label(self, text='特別版', font=('Arial', 18))
            self.label_3 = tk.Label(self, text='草地版', font=('Arial', 18))
            self.label_4 = tk.Label(self, text='夜空版', font=('Arial', 18))
            self.label_5 = tk.Label(self, text='岩壁版', font=('Arial', 18))
            self.label_6 = tk.Label(self, text='海洋版', font=('Arial', 18))

            # 換頁按鈕&現在頁碼
            self.prev_button = tk.Button(self, text="返回", font=('Arial', 20), command=self.prev_page)

            # 版面編輯
            self.style_1.grid(row=1, column=0, padx=5, pady=10)
            self.style_2.grid(row=1, column=1, padx=5, pady=10)
            self.style_3.grid(row=1, column=2, padx=5, pady=10)
            self.style_4.grid(row=4, column=0, padx=5, pady=10)
            self.style_5.grid(row=4, column=1, padx=5, pady=10)
            self.style_6.grid(row=4, column=2, padx=5, pady=10)

            self.label_1.grid(row=0, column=0, padx=5, pady=5)
            self.label_2.grid(row=0, column=1, padx=5, pady=5)
            self.label_3.grid(row=0, column=2, padx=5, pady=5)
            self.label_4.grid(row=3, column=0, padx=5, pady=5)
            self.label_5.grid(row=3, column=1, padx=5, pady=5)
            self.label_6.grid(row=3, column=2, padx=5, pady=5)

            self.prev_button.grid(row=5, column=0, padx=5, pady=5)

            # self.label_page.grid(row=6, column=1, padx=5, pady=20)

        def choose0(self):
            update_game_data(1,0)
            pg_manager.show_page(GameMenuPage)
        def choose1(self):
            update_game_data(1,1)
            pg_manager.show_page(GameMenuPage)
        def choose2(self):
            update_game_data(1,2)
            pg_manager.show_page(GameMenuPage)
        def choose3(self):
            update_game_data(1,3)
            pg_manager.show_page(GameMenuPage)
        def choose4(self):
            update_game_data(1,4)
            pg_manager.show_page(GameMenuPage)
        def choose5(self):
            update_game_data(1,5)
            pg_manager.show_page(GameMenuPage)
        def prev_page(self):
            pg_manager.show_page(LoginPage)
            global RELOADING
            RELOADING = True
            print(RELOADING)
        
    class GameMenuPage(tk.Frame):
        def __init__(self, parent, games):
            super().__init__(parent)
            self.parent = parent
            self.games = games
            self.buttons = []

            # 获取屏幕大小
            self.screen_width = self.parent.winfo_screenwidth()
            self.screen_height = self.parent.winfo_screenheight()

            # 动态调整图片大小
            self.image_width = int(self.screen_width / 5.2)  # 每行4个游戏，按钮占1/8宽度
            self.image_height = int(self.screen_height / 6)  # 每列放5个游戏，按钮占1/6高度

            self.load_images_and_buttons()

            # 换页按钮
            self.prev_button = tk.Button(self, text="上一頁", font=('Arial', 18), command=self.prev_page)
            self.prev_button.grid(row=4, column=2, padx=0, pady=0)

            # 上傳按钮
            self.upload_button = tk.Button(self, text="上傳", font=('Arial', 18), command=self.upload)
            self.upload_button.grid(row=4, column=4, padx=0, pady=0)

        def load_images_and_buttons(self):
            for idx, game in enumerate(self.games):
                image_path = f"Resource/img/gamelist/{game['scene_image']}"  # 使用 games 数据的图片路径
                image = Image.open(image_path)
                image = image.resize((self.image_width, self.image_height))  # 根据屏幕大小调整图片
                photo = ImageTk.PhotoImage(image)

                # 获取游戏名称
                game_name = game['name']

                # 创建带图片和游戏名称的按钮
                button = tk.Button(
                    self, image=photo, text=game_name, compound=tk.TOP,
                    command=lambda idx=idx: self.loading_page(idx)
                )
                button.image = photo  # 防止图片被垃圾回收

                # 计算按钮的位置，使每行有5个按钮
                row = idx // 5
                col = idx % 5

                button.grid(row=row, column=col, padx=0, pady=0)
                self.buttons.append(button)

        def prev_page(self):
            # 切换到第一个UI页面
            pg_manager.show_page(StyleChoosePage)

        def upload(self):
            upload_data()

        def loading_page(self, game_idx):
            pg_manager.show_page(LoadingPage, self.games[game_idx])


    class LoadingPage(tk.Frame):
        def __init__(self, master, game_data):
            super().__init__(master)
            self.master = master
            self.game_data = game_data

            # 设置窗口背景
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            self.master.configure(bg="lightsteelblue")

            #記錄欄位
            game_record = tk.Label(self, text="最高紀錄 : " + str(grab_upload_data(int(self.game_data['record_code']))), bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"), width=15)
            game_record.grid(row=0, column=0, columnspan=2, pady=5)
            #記錄欄位
            if self.game_data['code']in ['3', '4']:
                game_record = tk.Label(self, text=self.game_data['detect_text'] + str(grab_upload_data_float(int(self.game_data['detect_code']))), bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"))
            elif self.game_data['code']in ['17', '18', '19', '20']:
                game_record = tk.Label(self, text= "名稱: " + self.game_data['name'], bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"))
            else:
                game_record = tk.Label(self, text=self.game_data['detect_text'] + str(grab_upload_data(int(self.game_data['detect_code']))), bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"))
            game_record.grid(row=0, column=2, columnspan=2, pady=5)

            # 游戏场景图片
            image = Image.open(f"Resource/img/gamelist/{self.game_data['scene_image']}")
            image = image.resize((int(screen_width), int(screen_height*3/5)))
            photo = ImageTk.PhotoImage(image)
            game_scene_label = tk.Label(self, image=photo, bg="white")
            game_scene_label.image = photo  # 避免被垃圾回收
            game_scene_label.grid(row=1, column=0, columnspan=4, pady=25)

            # 底部按钮
            back_button = tk.Button(self, text="返回", font=("Helvetica", 35), fg="green", width=10, command=self.back)
            back_button.grid(row=2, column=0, padx=5, pady=20)

            intro_button = tk.Button(self, text="介紹", font=("Helvetica", 35), fg="purple", width=10, command=self.intro)
            intro_button.grid(row=2, column=1, padx=5, pady=20)

            detect_button = tk.Button(self, text="偵測", font=("Helvetica", 35), fg="orange", width=10, command=self.detect)
            detect_button.grid(row=2, column=2, padx=5, pady=20)

            start_button = tk.Button(self, text="開始", font=("Helvetica", 35), fg="red", width=10, command=self.start)
            start_button.grid(row=2, column=3, padx=5, pady=20)


        def back(self):
            pg_manager.show_page(GameMenuPage)

        def intro(self):
            pg_manager.show_page(IntroPage, self.game_data)

        def detect(self):
            if self.game_data['code'] in ['5', '6', '8', '9', '15', '16']:
                detect(17, 11, 12, 'vertical',28) #最高臂展（垂直）
            elif self.game_data['code'] in ['10', '14']:
                detect(26, 27, 28, 'vertical',27)   #最高右抬腳距離
            elif self.game_data['code'] == '1':
                detect(27, 27, 28, 'horizontal',24) #左跨步距離
            elif self.game_data['code'] == '2':
                detect(28, 27, 28, 'horizontal',25) #右跨步距離
            elif self.game_data['code'] == '3':
                squatting_detect()                  #蹲下起來時間
            elif self.game_data['code'] == '4':
                leg_up_detect()                  #抬腳速率
            elif self.game_data['code'] == '7':
                detect(25, 27, 28, 'vertical',26)   #最高左抬腳距離
            elif self.game_data['code'] == '11':
                detect(17, 11, 12, 'horizontal',29) #左最遠臂展（水平）
            elif self.game_data['code'] == '13':
                detect(18, 11, 12, 'horizontal',30) #右最遠臂展（水平）
            elif self.game_data['code'] == '12':
                detect(23, 11, 12, 'horizontal',31) #髖關節最遠移動距離
            elif self.game_data['code'] == '17':
                show_camera_with_pose(self.game_data['code'], 17, 18)             #蹲下起來時間
            elif self.game_data['code'] == '18':
                show_camera_with_pose(self.game_data['code'], 21, 22)             #蹲下起來時間
            elif self.game_data['code'] == '19':
                show_camera_with_pose(self.game_data['code'], 1, 4)             #蹲下起來時間
            elif self.game_data['code'] == '20':
                show_camera_with_pose(self.game_data['code'], 1, 4)             #蹲下起來時間
        
        def start(self):
            if self.game_data['code'] in start_games:
                start_games[self.game_data['code']]()  # 呼叫對應的函數
            else:
                print(f"找不到對應的遊戲，代碼：{self.game_data['code']}")
            upload_data()

    class IntroPage(tk.Frame):
        def __init__(self, master, game_data):
            super().__init__(master)
            self.master = master
            self.game_data = game_data

            # 窗口大小
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()

            # 游戏介绍
            label = tk.Label(self, text=f'遊戲說明: {self.game_data["intro_text"]}', font=('Arial', 25))
            label.grid(row=0, column=0, padx=10, pady=10)

            # 示意图
            image = Image.open(f"Resource/example/action/{self.game_data['intro_image']}")
            image = image.resize((screen_width, int(screen_height * 0.65)))
            photo = ImageTk.PhotoImage(image)
            pic = tk.Label(self, image=photo)
            pic.image = photo
            pic.grid(row=1, column=0, padx=10, pady=10)

            # 返回按钮
            back_button = tk.Button(self, text="返回", font=('Arial', 25), command=self.back)
            back_button.grid(row=2, column=0, padx=10, pady=10)

        def back(self):
            pg_manager.show_page(LoadingPage, self.game_data)

    # 初始化 Tk 
    root = tk.Tk()
    root.title("Pysenior")
    pg_manager = PGManager(root)

    # 頁面切換，顯示初始頁面
    decrypt_csv('Data/verify.csv', ENCRYPTKEY)
    if grab_verify_data_int(4) == 0:
        if grab_verify_data(3) == "null":
            pg_manager.show_page(FirstLoginPage)
        else:
            pg_manager.show_page(InitPage)
    else:
            pg_manager.show_page(LoginPage)
    # pg_manager.show_page(LoginPage)
    # 進入主循環
    root.mainloop()

if __name__ == "__main__":
    main()