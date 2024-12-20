import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
cred = credentials.Certificate("Data/pysenior-0716-firebase-adminsdk-nmyt1-ed6540e28a.json")  # 替換為你的 Firebase 憑證路徑
firebase_admin.initialize_app(cred)
db = firestore.client()

class FirebaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pysenior據點數據")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        # 下拉選單
        self.collection_label = ttk.Label(root, text="選擇據點：")
        self.collection_label.pack(pady=5)
        self.collection_combobox = ttk.Combobox(root, state="readonly", values=self.get_collections())
        self.collection_combobox.pack(pady=5)

        # 搜尋按鈕
        self.search_button = ttk.Button(root, text="搜尋", command=self.search_data)
        self.search_button.pack(pady=5)

        # 表格
        self.table = ttk.Treeview(root, columns=("field1", "field2", "field3"), show="headings")
        self.table.heading("field1", text="欄位1")
        self.table.heading("field2", text="欄位2")
        self.table.heading("field3", text="欄位3")
        self.table.pack(fill="both", expand=True, pady=10)

    def get_collections(self):
        """取得 Firebase 中的集合名稱，並增加 '全部' 選項"""
        collections = db.collections()
        collection_names = [collection.id for collection in collections]
        collection_names.insert(0, "全部")  # 在開頭插入 '全部'
        return collection_names

    def search_data(self):
        """根據選取的集合名稱搜尋資料，並按指定順序顯示欄位"""
        selected_collection = self.collection_combobox.get()
        if not selected_collection:
            messagebox.showerror("錯誤", "請選擇據點")
            return

        # 清空表格
        for item in self.table.get_children():
            self.table.delete(item)
        self.table["columns"] = ()  # 清空表格欄位

        try:
            data_list = []
            if selected_collection == "全部":
                # 遍歷所有集合並合併數據
                collections = db.collections()
                for collection in collections:
                    docs = collection.stream()
                    data_list.extend([doc.to_dict() for doc in docs])
            else:
                # 提取選定集合的數據
                collection_ref = db.collection(selected_collection)
                docs = collection_ref.stream()
                data_list = [doc.to_dict() for doc in docs]

            if not data_list:
                messagebox.showinfo("資訊", "沒有資料")
                return

            # 指定欄位顯示順序
            preferred_order = ["據點", "ID", "G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", 
                            "G09", "G10", "G11", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G19"]

            # 動態生成並排序欄位
            all_fields = set()
            for data in data_list:
                all_fields.update(data.keys())
            ordered_fields = [field for field in preferred_order if field in all_fields]  # 按指定順序排序
            remaining_fields = sorted(all_fields - set(preferred_order))  # 其他欄位按字母順序排列
            final_fields = ordered_fields + remaining_fields  # 合併欄位順序

            # 設置表格欄位
            self.table["columns"] = final_fields
            for field in final_fields:
                self.table.heading(field, text=field)
                self.table.column(field, width=100, anchor="center")  # 調整列寬和對齊方式

            # 插入資料到表格
            for data in data_list:
                self.table.insert("", "end", values=[data.get(field, "") for field in final_fields])

        except Exception as e:
            messagebox.showerror("錯誤", f"無法提取資料：{e}")

# 啟動應用程式
if __name__ == "__main__":
    root = tk.Tk()
    app = FirebaseApp(root)
    root.mainloop()