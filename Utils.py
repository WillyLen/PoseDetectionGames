import tkinter as tk
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

ENCRYPTKEY = "032118800"

MAGIC_HEADER = b'ENCRYPTEDFILE'

global RELOADING
RELOADING = False

def get_accountname():
    try:
        with open('Data/accountname.txt', 'r') as file:
            return file.read()  # 讀取 txt 檔案中的 accountname
    except FileNotFoundError:
        print("accountname.txt 不存在，請確認是否已登入")
        return None
    


#更新及讀取csv檔參數
def update_upload_data(new_value_index, new_value):
    rows = []
    with open('Data/upload.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # 檢查是否以 # 開頭，若是則略過
            if row and row[0].startswith('#'):
                continue
            if row[1] == get_accountname():
                row[new_value_index] = new_value  # 更新指定列的值
            rows.append(row)

    with open('Data/upload.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def grab_upload_data(value_index):
    row = []
    with open('Data/upload.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].startswith('#'):
                continue
            if row[1] == get_accountname():
                return int(row[value_index])
            
def grab_upload_data_float(value_index):
    row = []
    with open('Data/upload.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].startswith('#'):
                continue
            if row[1] == get_accountname():
                return float(row[value_index])
            
def update_game_data(new_value_index, new_value):
    rows = []
    with open('Data/game.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].startswith('#'):
                continue
            if row[0] == get_accountname():
                row[new_value_index] = new_value  # 更新指定列的值
            rows.append(row)

    with open('Data/game.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def grab_game_data(value_index):
    row = []
    with open('Data/game.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0].startswith('#'):
                continue
            if row[0] == get_accountname():
                return int(row[value_index])
            
#更新及讀取認證參數
def update_verify_data(new_value_index, new_value):
        rows = []
        with open('Data/verify.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                row[new_value_index] = new_value  # 更新指定列的值
                rows.append(row)

        with open('Data/verify.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

def grab_verify_data(value_index):
    row = []
    with open('Data/verify.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            return row[value_index]
        
def grab_verify_data_int(value_index):
    row = []
    with open('Data/verify.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            return int(row[value_index])

#獲取每台電腦之固定 MAC Address(綁定電腦)
def get_mac():
    def get_mac_address():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ':'.join([mac[e:e+2] for e in range(0, 11, 2)])

    mac_address = get_mac_address()
    return(f"{mac_address}")

#加密上述獲取之 MAC Address
def hash_mac(mac_address):
    key = f"{mac_address},{grab_verify_data(0)},{grab_verify_data(1)}"

    data_bytes = key.encode('utf-8')

    sha256 = hashlib.sha256()

    sha256.update(data_bytes)

    data_bytes = sha256.digest()

    final_hash = data_bytes.hex()

    return(f"{final_hash}")

#Hash 字串
def hash_str(str):
    key = f"{str}"

    data_bytes = key.encode('utf-8')

    sha256 = hashlib.sha256()

    sha256.update(data_bytes)

    data_bytes = sha256.digest()

    final_hash = data_bytes.hex()

    return(f"{final_hash}")

#生成key
def generate_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

#加密x(by Email)
def hash_x(email):

    data_bytes = email.encode('utf-8')

    sha256 = hashlib.sha256()

    sha256.update(data_bytes)

    data_bytes = sha256.digest()

    final_hash = data_bytes.hex()

    return(f"{final_hash}")

#加密key(by X, TID, PyID, Time)
def hash_key(Time):
    print(hash_x(grab_verify_data(5)))
    print(grab_verify_data(1))
    print(grab_verify_data(0))
    key = f"{hash_x(grab_verify_data(5))},{grab_verify_data(1)},{grab_verify_data(0)},{Time}"

    data_bytes = key.encode('utf-8')

    sha256 = hashlib.sha256()

    sha256.update(data_bytes)

    data_bytes = sha256.digest()

    final_hash = data_bytes.hex()

    return(f"{final_hash}")

#加解密cvs檔
def encrypt(data: bytes, key: bytes):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

def encrypt_csv(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    if data.startswith(MAGIC_HEADER):
        print("檔案已加密，跳過加密")
        return
    
    salt = os.urandom(16)
    key = generate_key(password, salt)
    encrypted_data = encrypt(data, key)
    
    with open(file_path, 'wb') as f:
        f.write(MAGIC_HEADER + salt + encrypted_data)

def decrypt(encrypted_data: bytes, key: bytes):
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return data

def decrypt_csv(file_path: str, password: str):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    if not encrypted_data.startswith(MAGIC_HEADER):
        print("檔案未加密，跳過解密")
        return
    
    encrypted_data = encrypted_data[len(MAGIC_HEADER):]
    salt = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    key = generate_key(password, salt)
    decrypted_data = decrypt(encrypted_data, key)
    
    with open(file_path, 'wb') as f:
        f.write(decrypted_data)