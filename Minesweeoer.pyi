# Minesweeper.py
# -*- coding: utf-8 -*-
import tkinter as tk
#from tkinter import messagebox
#import random
#import numpy as np


TILE_BG = "white"
TILE_FG = "black"

class Tile(tk.Button):
    # 定義類別屬性
    canClick = True
    isFirstClick = True

    def __init__(self, game: 'Minesweeper', x: int, y: int, font_size=12) -> None: ...

    def setMines(self) -> bool: ...

    def setDisplay(self) -> None: ...

    def countAdjacentMines(self) -> int: ...

    def isMineAt(self, x:int, y:int) -> bool: ...

    def clickTile(self) -> None: ...

    # 處理右鍵點擊事件
    def flagTile(self, event) -> None: ...

    def autoClick(self, x:int, y:int) -> None: ...

    def autoClickTile(self) -> None: ...

    # 自動點擊周圍沒插旗的地
    def autoclick_tile_with_no_flags(self) -> None: ...
    
    def endState(self) -> None: ...

    def firstClick(self, x, y) -> None: ...


class Minesweeper:
    def __init__(self, Xrange:int, Yrange:int, minesNumber:int) -> None: ...

    def updateTimer(self) -> None: ...



    def start(self) -> None: ...

    def gameover(self) -> None: ...

    def win(self) -> None: ...
                


def custom() -> None:
    def start(x:str, y:str, mines:str) -> None: ...
    ...


def main() -> None: ...

if __name__ == "__main__":
    main()