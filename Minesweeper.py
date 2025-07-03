import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
from sys import exit


TILE_BG = "pink"  # 按鈕背景色
TILE_FG = "white"  # 按鈕文字顏色

class Land(tk.Button):
    def __init__(self, game, x, y, font_size=12):
        super().__init__(game.panel, width=2, height=1, font=("Arial", font_size), bg=TILE_BG, fg=TILE_FG, state="normal")
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
                if not (i == self.x and j == self.y) and self.isMineAt(i, j):
                    count += 1
        return count

    def isMineAt(self, x, y):
        if 0 <= x < self.game.Xrange and 0 <= y < self.game.Yrange:
            return self.game.lands[x][y].isMine
        return False

    def clickLand(self):
        if not self.game.canClick:
            #print("遊戲已經結束，不能點擊格子！")
            return
        if not self.isClicked and not self.isFlagged: # 還沒被翻開的格子且沒插旗才能點擊
            #print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            self.game.remainingLands -= 1
            #print(f"剩餘需翻開的格子數為 {self.game.remainingLands}")
            if self.isMine:
                self.game.gameover()
            elif self.game.isFirstClick:
                self.game.start(self.x, self.y)  # 開始遊戲，裝地雷
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
            self.autoclick_land_with_no_flags()
        elif self.isFlagged:
            #print("該格已經被插旗了！")
            pass

    # 處理右鍵點擊事件
    def flagLand(self, event):
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
                if not (i == x and j == y) and 0 <= i < self.game.Xrange and 0 <= j < self.game.Yrange:
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
    def autoclick_land_with_no_flags(self):
        num_of_lands_with_flags = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if 0 <= i < self.game.Xrange and 0 <= j < self.game.Yrange:
                    if self.game.lands[i][j].isFlagged: num_of_lands_with_flags += 1
        
        # 周圍插旗的地不能自己的數字少，不然就return不自動點擊，算是保護玩家
        if num_of_lands_with_flags < int(self.display): return
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if 0 <= i < self.game.Xrange and 0 <= j < self.game.Yrange:
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
                if not (i == self.x and j == self.y) and 0 <= i < self.game.Xrange and 0 <= j < self.game.Yrange and\
                        self.game.lands[i][j].display == " ": # 點擊周圍的空格
                    self.game.lands[i][j].autoClickLand()


class Minesweeper:
    def __init__(self, Xrange, Yrange, minesNumber):
        setting_window.destroy()  # 關閉開始視窗
        self.gameFinished = False
        self.Xrange = Xrange
        self.Yrange = Yrange
        self.minesNumber = minesNumber
        self.canClick = True
        self.isFirstClick = True
        self.remainingLands = Xrange * Yrange - minesNumber
        self.lands = np.empty((Xrange, Yrange), dtype=object)  # 建立二維陣列儲存格子物件
        self.time = 0  # 初始化時間屬性
        
        # 設定字體大小與視窗大小
        self.root = tk.Tk()
        self.root.title("踩地雷!")
        self.font_size = 12
        if Xrange < 10 and Yrange < 10:
            self.root.geometry("700x700")
            self.font_size = 24
        elif 10 <= Xrange < 17 and 10 <= Yrange < 30:
            self.root.geometry("1000x700")
            self.font_size = 18
        else:
            self.root.state('zoomed')
            self.font_size = 12

        # 創建格子按鈕並設置到界面
        self.panel = tk.Frame(self.root)
        self.panel.grid(row=0, column=0)
        for i in range(Xrange):
            for j in range(Yrange): 
                self.lands[i][j] = Land(self, i, j, self.font_size)
        self.timer_label = tk.Label(self.root, text="時間: ")
        self.timer_label.grid(row=0, column=1)
        self.timer_var = tk.StringVar()
        self.timer_var.set("0秒")  # 初始化為 0 秒
        self.timer = tk.Label(self.root, textvariable=self.timer_var, bg="pink", fg="black")
        self.timer.grid(row=0, column=2)

        # 開始遊戲
        self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器
        self.root.mainloop()

    def updateTimer(self):
        if not self.gameFinished:  # 如果遊戲尚未結束
            self.time += 1  # 更新時間
            self.timer_var.set(f"{self.time}秒")  # 更新顯示的時間
            self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器

    def start(self, x, y): # 傳入第一個點擊的格子的座標，確保第一次點擊的格子不是地雷
        for _ in range(self.minesNumber):
            while True:
                randomX = random.randint(0, self.Xrange - 1)
                randomY = random.randint(0, self.Yrange - 1)
                if not self.lands[randomX][randomY].setMines(): # False代表已經有地雷了，裝地雷失敗
                    continue
                break # True代表裝地雷成功，跳出迴圈
        
        if self.lands[x][y].isMine:  # 如果第一次點擊的格子是地雷，則補裝一個雷
            self.lands[x][y].isMine = False  # 確保第一次點擊的格子不是地雷  
            while True:
                randomX = random.randint(0, self.Xrange - 1)
                randomY = random.randint(0, self.Yrange - 1) 
                # 確保不會裝在第一次點擊的格子上
                if (randomX == x and randomY == y) or not self.lands[randomX][randomY].setMines(): # False代表已經有地雷了，裝地雷失敗
                    continue
                
                break # True代表裝地雷成功，跳出迴圈
        
        for i in range(self.Xrange):
            for j in range(self.Yrange):
                self.lands[i][j].setDisplay() # 設定格子的顯示文字

    def gameover(self):
        self.gameFinished = True
        self.canClick = False  # 禁止點擊格子
        messagebox.showinfo("遊戲結束!", f"你踩到了地雷，遊戲結束！\n共耗時{self.time}秒")
        for i in range(self.Xrange):
            for j in range(self.Yrange):
                t = self.lands[i][j].endState() # 設定格子的顏色
        self.ask_restart()  # 新增這行

    def win(self):
        self.gameFinished = True
        messagebox.showinfo("遊戲成功!", f"恭喜你找出所有安全區塊！\n你成功了！\n共耗時{self.time}秒")
        for i in range(self.Xrange):
            for j in range(self.Yrange):
                self.lands[i][j].endState() # 設定格子的顏色
        self.ask_restart()  # 新增這行
    
    def ask_restart(self):
        answer = messagebox.askyesno("再玩一次", "要再玩一次嗎？")
        self.root.destroy()
        if answer:
            main()
        else:
            exit(0)
                


def custom():
    def start(x, y, mines):
        x, y, mines = x.strip(), y.strip(), mines.strip()
        if (not x.isdigit()) or (not y.isdigit()) or (not mines.isdigit()):
            messagebox.showerror("輸入錯誤!", "請輸入正確的遊戲大小及地雷數")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            mines_entry.delete(0, tk.END)
            return
        x, y, mines = int(x), int(y), int(mines)
        if x < 3 or y < 3 or mines < 1:
            messagebox.showerror("遊戲大小或地雷數過小!", "遊戲大小不能小於3x3，地雷數不能小於1")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            mines_entry.delete(0, tk.END)
            return
        elif x > 30 or y > 20:
            messagebox.showerror("遊戲大小過大!", "遊戲大小不能超過30x20")
            x_entry.delete(0, tk.END)
            y_entry.delete(0, tk.END)
            return
        elif mines > x * y:
            messagebox.showerror("地雷數過多!", "地雷數不能超過格子數")
            mines_entry.delete(0, tk.END)
            return
        root.destroy() # 關閉開始畫面，這行超重要！因為沒有它，計時器就會壞掉
        Minesweeper(x, y, mines)
        
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
    start_button = tk.Button(root, text="開始遊戲", command=lambda: start(x_entry.get(), y_entry.get(), mines_entry.get()))
    start_button.grid(row=4, column=0, columnspan=2)
    root.mainloop()


def main():
    global setting_window
    setting_window = tk.Tk()
    setting_window.title("歡迎來到踩地雷!")
    setting_window.geometry("300x150")
    text_label = tk.Label(setting_window, text="請選擇遊戲模式:")
    text_label.pack()
    beginner_button = tk.Button(setting_window, text="初級(8x8)", command=lambda: Minesweeper(8, 8, 10))
    beginner_button.pack()
    intermediate_button = tk.Button(setting_window, text="中級(16x16)", command=lambda: Minesweeper(16, 16, 40))
    intermediate_button.pack()
    expert_button = tk.Button(setting_window, text="專家(24x24)", command=lambda: Minesweeper(24, 24, 99))
    expert_button.pack()
    custom_button = tk.Button(setting_window, text="自定義", command=custom)
    custom_button.pack()
    setting_window.mainloop()
    

if __name__ == "__main__":
    main()