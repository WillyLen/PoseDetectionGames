import csv
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 初始化为单例模式
def initialize_firebase():
    if not firebase_admin._apps:  # 检查是否已有初始化的 Firebase app
        cred = credentials.Certificate("Data/pysenior-0716-firebase-adminsdk-nmyt1-ed6540e28a.json")
        firebase_admin.initialize_app(cred)

def upload_data():
    # 确保 Firebase 初始化只运行一次
    initialize_firebase()

    # 连接到 Firestore
    db = firestore.client()

    # CSV 文件路径
    csv_file_path = 'Data/upload.csv'

    # 读取 CSV 并写入 Firestore
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                doc_id = row['使用者帳號']
                # 将数据写入 Firestore 的 'game_data' 集合
                db.collection(row['#場域名稱']).document(doc_id).set(row)
        print("Data uploaded successfully!")
    except FileNotFoundError:
        print(f"Error: File not found at {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
upload_data()