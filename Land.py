import tkinter as tk

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
            #print(f"點擊了({self.x},{self.y})")
            self.isClicked = True
            self.config(bg="gray", fg="white", text=self.display)
            self.game.remainingLands -= 1
            #print(f"剩餘需翻開的格子數為 {self.game.remainingLands}")
            if self.game.isFirstClick:
                self.game.laying_mines(self.x, self.y)  # 開始遊戲，裝地雷
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
                self.config(bg="red", text=self.display)
            elif not self.isFlagged and self.isMine:
                self.config(bg="orange", text="💣")
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

