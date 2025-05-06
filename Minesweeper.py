import tkinter as tk
from tkinter import messagebox
import random
import numpy as np



TILE_BG = "white"
TILE_FG = "black"

class Tile(tk.Button):
    # 定義類別屬性
    canClick = True
    isFirstClick = True

    def __init__(self, master, x, y, font_size=12):
        super().__init__(master, width=2, height=1, font=("Arial", font_size), bg=TILE_BG, fg=TILE_FG, state="normal")
        self.x = x
        self.y = y
        self.isMines = False
        self.isClicked = False
        self.flag = False
        self.display = ""
        self.config(command=self.clickTile)
        self.bind("<Button-3>", self.flagTile)  # 綁定右鍵點擊事件
        self.grid(row=y, column=x) # 將按鈕放置在界面

    def setMines(self):
        if self.isMines:
            return False
        else:
            self.isMines = True
            return True

    def setDisplay(self):
        if self.isMines:
            symbol = "💣"
        else:
            symbol = str(self.countAdjacentMines())
        self.display = symbol if symbol != "0" else " " # 若symbol為0，則顯示空格

    def countAdjacentMines(self):
        count = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if not (i == self.x and j == self.y) and self.isMineAt(i, j):
                    count += 1
        return count

    def isMineAt(self, x, y):
        if 0 <= x < Minesweeper.Xrange and 0 <= y < Minesweeper.Yrange:
            return Minesweeper.tiles[x][y].isMines
        return False

    def clickTile(self):
        if not self.isClicked and not self.flag:
            print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            Minesweeper.remainingTiles -= 1
            print(f"剩餘需翻開的格子數為 {Minesweeper.remainingTiles}")
            if self.isMines:
                Minesweeper.gameover()
            elif Tile.isFirstClick:
                Tile.isFirstClick = False
                self.firstClick(self.x, self.y)
            elif self.display == " ":
                self.autoClick(self.x, self.y)
            else:
                print("點到數字格")
            if Minesweeper.remainingTiles == 0:
                Minesweeper.win()
        elif self.isClicked:
            if self.display == " ": return
            self.autoclick_tile_with_no_flags()
        elif self.flag:
            print("該格已經被插旗了！")

    # 處理右鍵點擊事件
    def flagTile(self, event):
        # 在這裡處理右鍵點擊事件，插旗的操作
        if not(self.isClicked): # 如果還沒被翻開的格子才能插旗
            if not(self.flag): # 若沒插旗
                self.config(text="🚩")# 插旗🚩
                print("插旗")
                self.flag = True
            else:
                self.config(text="")# 取消插旗
                print("取消插旗")
                self.flag = False
        else:
            print("該格已經被翻開了！")

    def autoClick(self, x, y):
        print("自動翻開周圍的格子")
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if not (i == x and j == y) and 0 <= i < Minesweeper.Xrange and 0 <= j < Minesweeper.Yrange:
                    Minesweeper.tiles[i][j].autoClickTile()

    def autoClickTile(self):
        if not self.isClicked:
            self.flag = False
            print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            Minesweeper.remainingTiles -= 1
            print(f"剩餘需翻開的格子數為 {Minesweeper.remainingTiles}")
            if self.display == " ":
                self.autoClick(self.x, self.y)
            if Minesweeper.remainingTiles == 0:
                Minesweeper.win()

    # 自動點擊周圍沒插旗的地
    def autoclick_tile_with_no_flags(s):
        num_of_tiles_with_flags = 0
        for i in range(s.x - 1, s.x + 2):
            for j in range(s.y - 1, s.y + 2):
                if 0 <= i < Minesweeper.Xrange and 0 <= j < Minesweeper.Yrange:
                    if Minesweeper.tiles[i][j].flag: num_of_tiles_with_flags += 1
        
        # 周圍插旗的地不能自己的數字少，不然就return不自動點擊，算是保護玩家
        if num_of_tiles_with_flags < int(s.display): return
        for i in range(s.x - 1, s.x + 2):
            for j in range(s.y - 1, s.y + 2):
                if 0 <= i < Minesweeper.Xrange and 0 <= j < Minesweeper.Yrange:
                    if not Minesweeper.tiles[i][j].isClicked and not Minesweeper.tiles[i][j].flag:
                        Minesweeper.tiles[i][j].clickTile()
    
    def endState(self):
        #print(f"({self.x},{self.y}) 遊戲結束")
        Tile.canClick = False
        if not self.isClicked:
            if self.flag and self.isMines:
                self.config(bg="green", text="🚩")
            elif self.flag and not self.isMines:
                self.config(bg="orange", text=self.display)
            elif not self.flag and self.isMines:
                self.config(bg="red", text="💣")
            else:
                self.config(bg="blue", text=self.display)
            self.config(fg="gray")
        else:
            self.config(fg="white")

    def firstClick(self, x, y):
        print(f"第一次點擊的格子({self.x},{self.y})")
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                print(i, j)
                if not (i == self.x and j == self.y) and 0 <= i < Minesweeper.Xrange and 0 <= j < Minesweeper.Yrange and\
                        Minesweeper.tiles[i][j].display == " ": # 點擊周圍的空格
                    Minesweeper.tiles[i][j].autoClickTile()


class Minesweeper:
    def __init__(self, Xrange, Yrange, minesNumber):
        setting_window.destroy()  # 關閉開始視窗
        Minesweeper.gameFinished = False
        Minesweeper.Xrange = Xrange
        Minesweeper.Yrange = Yrange
        Minesweeper.minesNumber = minesNumber
        Minesweeper.remainingTiles = Xrange * Yrange - minesNumber
        Minesweeper.tiles = np.empty((Xrange, Yrange), dtype=object)  # 建立二維陣列儲存格子物件
        Minesweeper.time = 0  # 初始化時間屬性
        
        # 設定字體大小與視窗大小
        self.root = tk.Tk()
        self.root.title("踩地雷!")
        self.font_size = 12
        if Xrange < 10 and Yrange < 10:
            self.root.geometry("700x700")
            self.font_size = 24
        elif 10 <= Xrange < 15 and 10 <= Yrange < 30:
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
                tile = Tile(self.panel, i, j, self.font_size)
                Minesweeper.tiles[i][j] = tile
        self.timer_label = tk.Label(self.root, text="時間: ")
        self.timer_label.grid(row=0, column=1)
        self.timer_var = tk.StringVar()
        self.timer_var.set("0秒")  # 初始化為 0 秒
        self.timer = tk.Label(self.root, textvariable=self.timer_var, bg="pink", fg="black")
        self.timer.grid(row=0, column=2)

        # 開始遊戲
        self.start()
        self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器
        self.root.mainloop()

    def updateTimer(self):
        if not Minesweeper.gameFinished:  # 如果遊戲尚未結束
            Minesweeper.time += 1  # 更新時間
            self.timer_var.set(f"{Minesweeper.time}秒")  # 更新顯示的時間
            self.root.after(1000, self.updateTimer)  # 每秒更新一次計時器



    def start(self):
        for _ in range(Minesweeper.minesNumber):
            while True:
                randomX = random.randint(0, Minesweeper.Xrange - 1)
                randomY = random.randint(0, Minesweeper.Yrange - 1)
                if not Minesweeper.tiles[randomX][randomY].setMines():
                    continue
                break

        for i in range(Minesweeper.Xrange):
            for j in range(Minesweeper.Yrange):
                Minesweeper.tiles[i][j].setDisplay() # 設定格子的顯示文字

    @staticmethod
    def gameover():
        Minesweeper.gameFinished = True
        messagebox.showinfo("遊戲結束!", f"你踩到了地雷，遊戲結束！\n共耗時{Minesweeper.time}秒")
        for i in range(Minesweeper.Xrange):
            for j in range(Minesweeper.Yrange):
                t = Minesweeper.tiles[i][j]
                t.endState() # 設定格子的顏色

    @staticmethod
    def win():
        Minesweeper.gameFinished = True
        messagebox.showinfo("遊戲成功!", f"恭喜你找出所有安全區塊！\n你成功了！\n共耗時{Minesweeper.time}秒")
        for i in range(Minesweeper.Xrange):
            for j in range(Minesweeper.Yrange):
                t = Minesweeper.tiles[i][j]
                t.endState() # 設定格子的顏色



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