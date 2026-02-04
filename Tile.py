import pygame as pg
from typing import Dict

IMAGES: Dict[str, pg.Surface] = dict()
def load_img():
    for i in range(9):
        img_path = "images/tile_"+str(i)+".png"
        IMAGES[str(i)] = pg.image.load(img_path).convert()
    IMAGES["flag"] = pg.image.load("images/tile_flag.png").convert()
    IMAGES["plain"] = pg.image.load("images/tile_plain.png").convert()

class Tile:
    #Tile.game = None
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
        self.rect = pg.Rect(50*x, 50*y, 50, 50) # 偵測點擊用
        self.status: bool | None = False # None=翻開，True或False表示是否插旗
        self.num = 0 # 0~8表示周圍有幾個雷，9表示自己是雷
    
    @property
    def is_mine(self) -> bool:
        return self.num == 9
    
    def set_mine(self):
        if self.is_mine:
            return False
        else:
            self.num == 9
            return True
    
    def count_adjacent_mines(self):
        count = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if not (i == self.x and j == self.y) and Tile.game.is_mine_at(i, j):
                    count += 1
        return count
    
    def click(self):
        if not Tile.game.running:
            print("遊戲已經結束，不能點擊格子！")
            return
        print(f"點擊了({self.x},{self.y})")
        # 之後再補上邏輯
    
    def draw(self):
        #pg.draw.rect(Tile.game.screen, (0, 255, 0), self.rect, 1)
        if self.status is None: # 翻開
            Tile.game.screen.blit(IMAGES[+str(self.num)])
        elif self.status: # 插旗
            Tile.game.screen.blit(IMAGES["flag"])
        else:
            Tile.game.screen.blit(IMAGES["plain"])