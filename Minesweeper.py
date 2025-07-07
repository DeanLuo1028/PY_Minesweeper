import tkinter as tk
from tkinter import messagebox
import random
from tkinter import ttk
from numpy import empty
from sys import exit
# -*- coding: utf-8 -*-

class Land(tk.Button):
    def __init__(self, game, x, y, font_size=12, land_bg="white", land_fg="black"):
        super().__init__(game.panel, width=2, height=1, font=("Arial", font_size), bg=land_bg, fg=land_fg, state="normal")
        self.game = game
        self.x = x
        self.y = y
        self.isMine = False
        self.isClicked = False
        self.isFlagged = False
        self.display = ""
        self.config(command=self.clickLand)
        self.bind("<Button-3>", self.flagLand)  # 綁定右鍵點擊事件
        self.grid(row=y, column=x) # 將按鈕放置在界面

    def setMines(self):
        if self.isMine:
            return False
        else:
            self.isMine = True
            return True

    def setDisplay(self):
        if self.isMine:
            self.display = "💣"
        else:
            if (symbol := self.countAdjacentMines()) == 0: 
                # 不能寫`if symbol := self.countAdjacentMines() == 0:`不然symbol會是bool
                self.display = " " # 若symbol為0，則顯示空格
            else:
                self.display = str(symbol)

    def countAdjacentMines(self):
        count = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if not (i == self.x and j == self.y) and self.game.isMineAt(i, j):
                    count += 1
        return count

    

    def clickLand(self):
        if self.game.gameFinished: # 如果遊戲還沒結束才能點擊格子
            print("遊戲已經結束，不能點擊格子！")
            return
        if not self.isClicked and not self.isFlagged: # 還沒被翻開的格子且沒插旗才能點擊
            if self.isMine:
                self.game.click_on_mine(self.x, self.y)  # 點到地雷了
                return
            print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            self.game.remainingLands -= 1
            #print(f"剩餘需翻開的格子數為 {self.game.remainingLands}")
            if self.game.isFirstClick:
                self.game.laying_mines(self.x, self.y)  # 開始遊戲，裝地雷 # TODO
                self.game.isFirstClick = False
                self.config(bg="gray", fg="white", text=self.display)
                self.firstClick(self.x, self.y)
            elif self.display == " ":
                self.autoClick(self.x, self.y)
            else:
                #print("點到數字格")
                pass
            if self.game.remainingLands == 0:
                self.game.win()
        elif self.isClicked:
            if self.display == " ": return
            self.autoClickTileWithNoFlags()
        elif self.isFlagged:
            #print("該格已經被插旗了！")
            pass

    # 處理右鍵點擊事件
    def flagLand(self, event):
        if self.game.gameFinished: # 如果遊戲已經結束，不能插旗
            return
        # 在這裡處理右鍵點擊事件，插旗的操作
        if not(self.isClicked): # 如果還沒被翻開的格子才能插旗
            if not(self.isFlagged): # 若沒插旗
                self.config(text="🚩")# 插旗🚩
                #print("插旗")
                self.isFlagged = True
            else:
                self.config(text="")# 取消插旗
                #print("取消插旗")
                self.isFlagged = False
        else:
            #print("該格已經被翻開了！")
            pass

    def autoClick(self, x, y):
        #print("自動翻開周圍的格子")
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if not (i == x and j == y) and 0 <= i < self.game.x_range and 0 <= j < self.game.y_range:
                    self.game.lands[i][j].autoClickLand()

    def autoClickLand(self):
        if not self.isClicked:
            self.isFlagged = False
            #print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            self.game.remainingLands -= 1
            #print(f"剩餘需翻開的格子數為 {self.game.remainingLands}")
            if self.display == " ":
                self.autoClick(self.x, self.y)
            if self.game.remainingLands == 0:
                self.game.win()

    # 自動點擊周圍沒插旗的地
    def autoClickTileWithNoFlags(self):
        num_of_lands_with_flags = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if 0 <= i < self.game.x_range and 0 <= j < self.game.y_range:
                    if self.game.lands[i][j].isFlagged: num_of_lands_with_flags += 1
        
        # 周圍插旗的地不能自己的數字少，不然就return不自動點擊，算是保護玩家
        if num_of_lands_with_flags < int(self.display): return
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if 0 <= i < self.game.x_range and 0 <= j < self.game.y_range:
                    if not self.game.lands[i][j].isClicked and not self.game.lands[i][j].isFlagged:
                        self.game.lands[i][j].clickLand()
    
    def endState(self):
        #print(f"({self.x},{self.y}) 遊戲結束")
        if not self.isClicked:
            if self.isFlagged and self.isMine:
                self.config(bg="green", text="🚩")
            elif self.isFlagged and not self.isMine:
                self.config(bg="orange", text=self.display)
            elif not self.isFlagged and self.isMine:
                self.config(bg="red", text="💣")
            else:
                self.config(bg="blue", text=self.display)
            self.config(fg="gray")
        else:
            self.config(fg="white")

    def firstClick(self, x, y):
        #print(f"第一次點擊的格子({self.x},{self.y})")
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                #print( i, j)
                if not (i == self.x and j == self.y) and 0 <= i < self.game.x_range and 0 <= j < self.game.y_range and\
                        self.game.lands[i][j].display == " ": # 點擊周圍的空格
                    self.game.lands[i][j].autoClickLand()


class Minesweeper:
    def __init__(self, x_range, y_range, mines_number, times_of_can_back=0):
        setting_window.destroy()  # 關閉開始視窗
        self.gameFinished = False
        self.x_range = x_range
        self.y_range = y_range
        self.mines_number = mines_number
        self.isFirstClick = True
        self.remainingLands = x_range * y_range - mines_number
        self.times_of_can_back = times_of_can_back # 用來計算可以回到上一個狀態的次數
        self.land_bg , self.land_fg = "white", "black"  # 按鈕背景色與文字顏色
        self.lands = empty((x_range, y_range), dtype=object)  # 建立二維陣列儲存格子物件
        self.time = 0  # 初始化時間屬性
        
        # 設定字體大小與視窗大小
        self.root = tk.Tk()
        self.root.title("踩地雷!")
        self.font_size = 12
        if x_range < 10 and y_range < 10:
            self.root.geometry("700x700")
            self.font_size = 24
        elif 10 <= x_range < 17 and 10 <= y_range < 30:
            self.root.geometry("1000x700")
            self.font_size = 18
        else:
            self.root.state('zoomed')
            self.font_size = 12

        # 創建格子按鈕並設置到界面
        self.panel = tk.Frame(self.root)
        self.panel.grid(row=0, column=0)
        for i in range(x_range):
            for j in range(y_range): 
                self.lands[i][j] = Land(self, i, j, self.font_size)
        self.timer_label = tk.Label(self.root, text="時間: ")
        self.timer_label.grid(row=0, column=1)
        self.timer_var = tk.StringVar()
        self.timer_var.set("0秒")  # 初始化為 0 秒
        self.timer = tk.Label(self.root, textvariable=self.timer_var, bg="pink", fg="black")
        self.timer.grid(row=0, column=2)

        self.color_picker = tk.Button(self.root, text="設定格子背景色與文字顏色", command=self.setLandBgFg)
        self.color_picker.grid(row=2, column=0)
        # 開始遊戲
        self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器
        self.root.mainloop()

    def updateTimer(self):
        if not self.gameFinished:  # 如果遊戲尚未結束
            self.time += 1  # 更新時間
            self.timer_var.set(f"{self.time}秒")  # 更新顯示的時間
            self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器

    def laying_mines(self, x, y): # 傳入第一個點擊的格子的座標，確保第一次點擊的格子不是地雷
        for _ in range(self.mines_number):
            while True:
                randomX = random.randint(0, self.x_range - 1)
                randomY = random.randint(0, self.y_range - 1)
                if not self.lands[randomX][randomY].setMines(): # False代表已經有地雷了，裝地雷失敗
                    continue
                break # True代表裝地雷成功，跳出迴圈
        
        if self.lands[x][y].isMine:  # 如果第一次點擊的格子是地雷，則補裝一個雷
            self.lands[x][y].isMine = False  # 確保第一次點擊的格子不是地雷  
            while True:
                randomX = random.randint(0, self.x_range - 1)
                randomY = random.randint(0, self.y_range - 1) 
                # 確保不會裝在第一次點擊的格子上
                if (randomX == x and randomY == y) or not self.lands[randomX][randomY].setMines(): # False代表已經有地雷了，裝地雷失敗
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
            give_up_btn = tk.Button(root, text="放棄", command=self.gameover)
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
            game_setting()
        else:
            exit(0)
                


def custom():
    def start(x, y, mines, times_of_can_back):
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
        #root.destroy() # 關閉開始畫面，這行超重要！因為沒有它，計時器就會壞掉
        Minesweeper(x, y, mines, times_of_can_back)
        
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
    times_of_can_back_label = tk.Label(root, text="可回到上一步的次數:")
    times_of_can_back_label.grid(row=4, column=0)
    times_of_can_back_entry = tk.Entry(root)
    times_of_can_back_entry.grid(row=4, column=1)
    start_button = tk.Button(root, text="開始遊戲", command=lambda: \
        start(x_entry.get(), y_entry.get(), mines_entry.get(), times_of_can_back_entry.get()))
    start_button.grid(row=5, column=0, columnspan=2)
    root.mainloop()


def game_setting():
    global setting_window
    setting_window = tk.Tk()
    setting_window.title("歡迎來到踩地雷!")
    setting_window.geometry("300x150")
    text_label = tk.Label(setting_window, text="請選擇遊戲模式:")
    text_label.pack()
    beginner_button = tk.Button(setting_window, text="初級(8x8)", command=lambda: Minesweeper(8, 8, 10, 3))
    beginner_button.pack()
    intermediate_button = tk.Button(setting_window, text="中級(16x16)", command=lambda: Minesweeper(16, 16, 40, 2))
    intermediate_button.pack()
    expert_button = tk.Button(setting_window, text="專家(24x20)", command=lambda: Minesweeper(24, 20, 80, 1))
    expert_button.pack()
    custom_button = tk.Button(setting_window, text="自定義", command=custom)
    custom_button.pack()
    setting_window.mainloop()
    

if __name__ == "__main__":
    game_setting()  # 啟動遊戲設定界面