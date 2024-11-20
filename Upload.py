import csv
import firebase_admin
from firebase_admin import credentials, firestore

def upload_data():
    # 初始化 Firebase
    cred = credentials.Certificate("Data/pysenior-0716-firebase-adminsdk-nmyt1-ed6540e28a.json")
    firebase_admin.initialize_app(cred)

    # 連接到 Firestore
    db = firestore.client()

    # CSV 文件路径
    csv_file_path = 'Data/upload.csv'

    # 讀取 CSV 並寫入 Firestore
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            doc_id = row['ID']
            # 将数据写入 Firestore 的 'game_data' 集合
            db.collection(row['據點']).document(doc_id).set(row)

    print("Data uploaded successfully!")
# upload_data()