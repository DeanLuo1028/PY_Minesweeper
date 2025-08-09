import tkinter as tk
from tkinter import messagebox
from Minesweeper import Minesweeper

def start(x, y, mines, times_of_can_back):
    setting_window.destroy()  # 關閉開始視窗
    Minesweeper(x, y, mines, times_of_can_back)
    

def custom():
    def check_parameters(x, y, mines, times_of_can_back):
        x, y, mines = x.strip(), y.strip(), mines.strip()
        times_of_can_back = times_of_can_back.strip()
        if times_of_can_back == "": times_of_can_back = "0"  # 如果沒有輸入可回到上一步的次數，則預設為0
        if (not x.isdigit()) or (not y.isdigit()) or (not mines.isdigit()) or (not times_of_can_back.isdigit()):
            messagebox.showerror("輸入錯誤!", "請輸入正確的遊戲大小、地雷數及可回到上一步的次數")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            mines_entry.delete(0, tk.END)
            return
        x, y, mines, times_of_can_back = int(x), int(y), int(mines), int(times_of_can_back)
        if x < 3 or y < 3 or mines < 1:
            messagebox.showerror("遊戲大小或地雷數過小!", "遊戲大小不能小於3x3，地雷數不能小於1")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            mines_entry.delete(0, tk.END)
            return
        elif x > 49 or y > 23:
            messagebox.showerror("遊戲大小過大!", "遊戲大小不能超過49x23")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            return
        elif mines > x * y:
            messagebox.showerror("地雷數過多!", "地雷數不能超過格子數")
            mines_entry.delete(0, tk.END)
            return
        elif times_of_can_back < 0:
            messagebox.showerror("可回到上一步的次數錯誤!", "可回到上一步的次數不能小於0")
            times_of_can_back_entry.delete(0, tk.END)
            return
        root.destroy()  # 關閉開始畫面，這行超重要！因為沒有它，計時器就會壞掉
        start(x, y, mines, times_of_can_back)
        
    root = tk.Tk()
    root.title("自定義踩地雷")
    root.geometry("300x150")
    text_label = tk.Label(root, text="請輸入遊戲大小(X,Y)及地雷數:")
    text_label.grid(row=0, column=0, columnspan=2)
    text_x_label = tk.Label(root, text="X:")
    text_x_label.grid(row=1, column=0)
    x_entry = tk.Entry(root)
    x_entry.grid(row=1, column=1)
    text_y_label = tk.Label(root, text="Y:")
    text_y_label.grid(row=2, column=0)
    y_entry = tk.Entry(root)
    y_entry.grid(row=2, column=1)
    text_mines_label = tk.Label(root, text="地雷數:")
    text_mines_label.grid(row=3, column=0)
    mines_entry = tk.Entry(root)
    mines_entry.grid(row=3, column=1)
    times_of_can_back_label = tk.Label(root, text="可復活次數:")
    times_of_can_back_label.grid(row=4, column=0)
    times_of_can_back_entry = tk.Entry(root)
    times_of_can_back_entry.grid(row=4, column=1)
    start_button = tk.Button(root, text="開始遊戲", command=lambda: \
        check_parameters(x_entry.get(), y_entry.get(), mines_entry.get(), times_of_can_back_entry.get()))
    start_button.grid(row=5, column=0, columnspan=2)
    root.mainloop()


def game_setting():
    global setting_window
    setting_window = tk.Tk()
    setting_window.title("歡迎來到踩地雷!")
    setting_window.geometry("300x150")
    text_label = tk.Label(setting_window, text="請選擇遊戲模式:")
    text_label.pack()
    beginner_button = tk.Button(setting_window, text="初級(9x9, 10地雷)", command=lambda: start(9, 9, 10, 3))
    beginner_button.pack()
    intermediate_button = tk.Button(setting_window, text="中級(16x16, 40地雷)", command=lambda: start(16, 16, 40, 2))
    intermediate_button.pack()
    expert_button = tk.Button(setting_window, text="進階(30x16, 99地雷)", command=lambda: start(30, 16, 99, 1))
    expert_button.pack()
    custom_button = tk.Button(setting_window, text="自定義", command=custom)
    custom_button.pack()
    setting_window.mainloop()
    

if __name__ == "__main__":
    game_setting()  # 啟動遊戲設定界面