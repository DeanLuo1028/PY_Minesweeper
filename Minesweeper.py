import tkinter as tk
from tkinter import messagebox
import random
from tkinter import ttk
from sys import exit
# -*- coding: utf-8 -*-


class Minesweeper:
    def __init__(self, x_range, y_range, mines_number, times_of_can_back=0):
        #setting_window.destroy()  # 關閉開始視窗
        self.gameFinished = False
        self.x_range = x_range
        self.y_range = y_range
        self.mines_number = mines_number
        self.isFirstClick = True
        self.remainingLands = x_range * y_range - mines_number
        self.times_of_can_back = times_of_can_back # 用來計算可以回到上一個狀態的次數
        self.land_bg , self.land_fg = "white", "black"  # 按鈕背景色與文字顏色
        self.lands = [[None for _ in range(y_range)] for _ in range(x_range)] # 建立二維陣列儲存格子物件
        self.time = 0  # 初始化時間屬性
        
        # 設定字體大小與視窗大小
        self.root = tk.Tk()
        self.root.title("踩地雷!")
        self.font_size = 12
        if x_range < 10 and y_range < 10:
            self.root.geometry("500x700")
            self.font_size = 24
        elif 10 <= x_range < 17 and 10 <= y_range <= 16:
            self.root.geometry("1000x700")
            self.font_size = 16
        elif 17 <= x_range <= 30 and 16 <= y_range < 24:
            self.root.state('zoomed')
            self.font_size = 16
        else:
            self.root.state('zoomed')
            self.font_size = 12

        # 創建格子按鈕並設置到界面
        self.panel = tk.Frame(self.root)
        self.panel.grid(row=0, column=0, rowspan=3)
        from Land import Land  # 從Land.py導入Land類別
        for i in range(x_range):
            for j in range(y_range): 
                self.lands[i][j] = Land(self, i, j, self.font_size)
        self.pause_btn = tk.Button(self.root, text="暫停", command=self.pause, bg="gray", fg="white")
        self.pause_btn.grid(row=0, column=1)
        self.timer_label = tk.Label(self.root, text="時間: ")
        self.timer_label.grid(row=1, column=1)
        self.timer_var = tk.StringVar()
        self.timer_var.set("0秒")  # 初始化為 0 秒
        self.timer = tk.Label(self.root, textvariable=self.timer_var, bg="pink", fg="black")
        self.timer.grid(row=1, column=2)

        self.color_picker = tk.Button(self.root, text="設定格子背景色與文字顏色", command=self.setLandBgFg)
        self.color_picker.grid(row=3, column=0)
        # 開始遊戲
        self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器
        self.root.mainloop()

    def pause(self):
        self.gameFinished = True
        result = messagebox.askyesno("暫停遊戲", "遊戲已暫停，是否繼續遊戲？\n選擇「是」繼續遊戲，選擇「否」結束遊戲。")
        if result: # 如果選擇繼續遊戲
            self.gameFinished = False  # 恢復遊戲狀態
            self.updateTimer()  # 繼續計時器
            return  # 不做任何操作，繼續遊戲
        else:  # 如果選擇結束遊戲
            self.gameover()  # 結束遊戲
        
    
    def updateTimer(self):
        if not self.gameFinished:  # 如果遊戲尚未結束
            self.time += 1  # 更新時間
            self.timer_var.set(f"{self.time}秒")  # 更新顯示的時間
            self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器

    def laying_mines(self, x, y): # 傳入第一個點擊的格子的座標，確保第一次點擊的格子不是地雷
        for _ in range(self.mines_number):
            while True:
                random_x = random.randint(0, self.x_range - 1)
                random_y = random.randint(0, self.y_range - 1)
                # 確保不會裝在第一次點擊的格子上             # False代表已經有地雷了，裝地雷失敗
                if (random_x == x and random_y == y) or not self.lands[random_x][random_y].setMines():
                    continue
                break # True代表裝地雷成功，跳出迴圈
        
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.lands[i][j].setDisplay() # 設定格子的顯示文字

    def isMineAt(self, x, y):
        if 0 <= x < self.x_range and 0 <= y < self.y_range:
            return self.lands[x][y].isMine
        return False
    
    def setLandBgFg(self):
        root = tk.Tk()
        root.geometry("300x150")
        root.title("設定格子背景色與文字顏色")
        bg_var = tk.StringVar()
        bg_var.set("white")  # 預設為白色
        bg_label = tk.Label(root, text="格子背景色:")
        bg_color_label = tk.Label(root, textvariable=bg_var, fg = bg_var.get())
        colors = ["white", "black", "gray", "red", "green", "blue", "yellow", "pink", "orange"]
        bg_box = ttk.Combobox(root, values=colors)
        bg_box.set("white")  # 預設為白色
        def setLandBg(color):
            self.land_bg = color
            bg_var.set(bg_box.get())
            bg_color_label.config(fg=bg_var.get())  # 更新顏色標籤的顏色
            for i in range(self.x_range):
                for j in range(self.y_range):
                    if not self.lands[i][j].isClicked:  # 如果格子已經被點擊過，則不改變背景色
                        self.lands[i][j].config(bg=self.land_bg)  # 更新格子的背景顏色
        bg_sure_btn = tk.Button(root, text="確定", command=lambda: setLandBg(bg_box.get()))
        
        fg_var = tk.StringVar()
        fg_var.set("black")  # 預設為黑色
        fg_label = tk.Label(root, text="格子文字顏色:")
        fg_color_label = tk.Label(root, textvariable=fg_var, fg=fg_var.get())
        fg_box = ttk.Combobox(root, values=colors)
        fg_box.set("black")  # 預設為黑色
        def setLandFg(color):
            self.land_fg = color
            fg_var.set(fg_box.get())
            fg_color_label.config(fg=fg_var.get())  # 更新顏色標籤的顏色
            for i in range(self.x_range):
                for j in range(self.y_range):
                    if not self.lands[i][j].isClicked:  # 如果格子已經被點擊過，則不改變文字顏色
                        self.lands[i][j].config(fg=self.land_fg)  # 更新格子的文字顏色
        fg_sure_btn = tk.Button(root, text="確定", command=lambda: setLandFg(fg_box.get()))
        
        bg_label.grid(row=0, column=0)
        bg_color_label.grid(row=0, column=1)
        bg_box.grid(row=0, column=2)
        bg_sure_btn.grid(row=0, column=3)
        fg_label.grid(row=1, column=0)
        fg_color_label.grid(row=1, column=1)
        fg_box.grid(row=1, column=2)
        fg_sure_btn.grid(row=1, column=3)
    
    def click_on_mine(self, x, y):
        if self.times_of_can_back > 0:
            root = tk.Tk()
            root.title("踩到地雷了!")
            root.geometry("300x150")
            label = tk.Label(root, text=f"你踩到了地雷({x},{y})，但你還有{self.times_of_can_back}次機會可以回到上一步")
            label.pack()
            btn = tk.Button(root, text="回到上一步", command=root.destroy)
            btn.pack()
            def give_up():
                root.destroy()
                self.gameover()
            give_up_btn = tk.Button(root, text="放棄", command=give_up)
            give_up_btn.pack()
            self.times_of_can_back -= 1
            root.mainloop()
        else:
            self.gameover()
    
    def gameover(self):
        self.gameFinished = True
        messagebox.showinfo("遊戲結束!", f"你踩到了地雷，遊戲結束！\n共耗時{self.time}秒")
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.lands[i][j].endState() # 設定格子的顏色
        self.ask_restart()

    def win(self):
        self.gameFinished = True
        messagebox.showinfo("遊戲成功!", f"恭喜你找出所有安全區塊！\n你成功了！\n共耗時{self.time}秒")
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.lands[i][j].endState() # 設定格子的顏色
        self.ask_restart()
    
    def ask_restart(self):
        answer = messagebox.askyesno("再玩一次", "要再玩一次嗎？")
        self.root.destroy()
        if answer:
            from GameSetting import game_setting
            game_setting()
        else:
            exit(0)            