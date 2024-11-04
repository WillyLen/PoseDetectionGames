import tkinter as tk
from PIL import Image, ImageTk

# 創建主視窗
root = tk.Tk()
root.title("Game Layout")

# 設定視窗大小為螢幕大小
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# 創建 Game Name 標籤
game_name_label = tk.Label(root, text="躲隕石", bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"), width=10)
game_name_label.grid(row=0, column=0, columnspan=4, pady=5)

# 載入並顯示圖片
image_path = "Resource/img/gamelist/Game_1_1.jpg"  # 替換成你的圖片路徑
image = Image.open(image_path)
image = image.resize((int(screen_width), int(screen_height*3/5)))  # 調整圖片大小
photo = ImageTk.PhotoImage(image)

# 創建 Game Scene 圖像的占位符
game_scene_label = tk.Label(root, image=photo, bg="white")
game_scene_label.image = photo  # 防止圖片被垃圾回收
game_scene_label.grid(row=1, column=0, columnspan=4, pady=25)

# 創建底部的按鈕
back_button = tk.Button(root, text="返回", font=("Helvetica", 35), fg="green", width=10)
back_button.grid(row=2, column=0, padx=5, pady=20)

intro_button = tk.Button(root, text="介紹", font=("Helvetica", 35), fg="purple", width=10)
intro_button.grid(row=2, column=1, padx=5, pady=20)

detect_button = tk.Button(root, text="偵測", font=("Helvetica", 35), fg="orange", width=10)
detect_button.grid(row=2, column=2, padx=5, pady=20)

start_button = tk.Button(root, text="開始", font=("Helvetica", 35), fg="red", width=10)
start_button.grid(row=2, column=3, padx=5, pady=20)

# 開始主循環
root.mainloop()



# class LoadingPage(tk.Frame):
#         def __init__(self, master=None):
#             super().__init__(master)
#             self.master = master

#             # 設置窗口大小為螢幕大小
#             screen_width = self.master.winfo_screenwidth()
#             screen_height = self.master.winfo_screenheight()
#             self.master.geometry(f"{screen_width}x{screen_height}")

#             self.master.configure(bg="lightsteelblue")  # 設置主窗口背景顏色

#             # 創建 Game Name 標籤
#             game_name_label = tk.Label(root, text="躲隕石", bg="lightsteelblue", fg="blue", font=("Helvetica", 40, "bold"), width=10)
#             game_name_label.grid(row=0, column=0, columnspan=4, pady=5)

#             # 載入並顯示圖片
#             image_path = "Resource/img/gamelist/Game_1_1.jpg"  # 替換成你的圖片路徑
#             image = Image.open(image_path)
#             image = image.resize((int(screen_width), int(screen_height*3/5)))  # 調整圖片大小
#             photo = ImageTk.PhotoImage(image)

#             # 創建 Game Scene 圖像的占位符
#             game_scene_label = tk.Label(root, image=photo, bg="white")
#             game_scene_label.image = photo  # 防止圖片被垃圾回收
#             game_scene_label.grid(row=1, column=0, columnspan=4, pady=25)

#             # 創建底部的按鈕
#             back_button = tk.Button(root, text="返回", font=("Helvetica", 35), fg="green", width=10)
#             back_button.grid(row=2, column=0, padx=5, pady=20)

#             intro_button = tk.Button(root, text="介紹", font=("Helvetica", 35), fg="purple", width=10)
#             intro_button.grid(row=2, column=1, padx=5, pady=20)

#             detect_button = tk.Button(root, text="偵測", font=("Helvetica", 35), fg="orange", width=10)
#             detect_button.grid(row=2, column=2, padx=5, pady=20)

#             start_button = tk.Button(root, text="開始", font=("Helvetica", 35), fg="red", width=10)
#             start_button.grid(row=2, column=3, padx=5, pady=20)

#         def prev_page(self):
#             pg_manager.show_page(StyleChoosePage)
#         def intro(self):
#             pg_manager.show_page(intro_1)