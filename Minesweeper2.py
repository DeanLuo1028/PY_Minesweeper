import pygame as pg
import random
from sys import exit
from typing import List
from Tile import Tile, load_img  # 從Tile2.py導入Tile類別
# -*- coding: utf-8 -*-

FPS = 60

class Minesweeper:
    def __init__(self, x_range: int, y_range: int, mines_number: int , times_of_can_back=0):
        Tile.game = self
        self.running: bool = True
        self.x_range, self.y_range = x_range, y_range
        self.mines_number = mines_number
        self.is_first_click = True
        self.remaining_Tiles = x_range * y_range - mines_number
        #self.times_of_can_back = times_of_can_back # 用來計算可以回到上一個狀態的次數
        self.tiles: List[List[Tile]] = [[None for _ in range(y_range)] for _ in range(x_range)] # 建立二維陣列儲存格子物件
        #self.time = 0  # 初始化時間屬性
    
        pg.init()
        self.screen_size = (500,500)
        self.screen=pg.display.set_mode(self.screen_size)
        pg.display.set_caption("Minesweeper")

        self.surface = pg.Surface(self.screen_size)
        self.surface.fill((0,0,0))
        self.screen.blit(self.surface, (0,0))
        
        load_img()
        
        self.clock=pg.time.Clock()

        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j] = Tile(i, j)
        
        self.mainloop()
    
    def mainloop(self):
        while self.running:
            self.clock.tick(FPS)
            for events in pg.event.get():
                if events.type == pg.QUIT:
                    self.running = False

            self.draw_tiles()
            pg.display.update()
        
        pg.quit()

    def draw_tiles(self):
        self.screen.fill((255,255,255)) # 清除畫面
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j].draw()
        pg.display.flip()


if __name__ == "__main__":
    Minesweeper(10, 10, 10, 3)