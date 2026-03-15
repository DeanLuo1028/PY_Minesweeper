# 這是 model
from enum import Enum, auto

class Status(Enum):
    OPENED = auto() # 格子已翻開
    FLAG = auto() # 格子已插旗（未翻開）
    NO_FLAG = auto() # 格子未插旗（未翻開）

class Tile:
    """一個格子
    game: Minesweeper 主體，不改成Tile類的屬性是因為可能會同時開不只一局
    x, y: 格子座標
    status: 格子狀態，True和False代表是否插旗，None代表已經翻開
    num: 周圍的地雷數量，9代表自身為地雷
    """
    def __init__(self, game, x: int, y: int):
        """初始化Tile
        Args:
            game (Minesweeper): 遊戲主體
            x (int): 格子的x座標
            y (int): 格子的y座標

        """
        self.game = game
        self.x, self.y = x, y
        self.status: Status = Status.NO_FLAG
        self.num: int = 0


    @property
    def is_mine(self) -> bool:
        """是否是地雷"""
        return self.num == 9
    
    def is_(self, x: int, y: int) -> bool:
        return self.x == x and self.y == y
    def is_not_(self, x: int, y: int) -> bool:
        return self.x != x or self.y != y

    def set_mine(self) -> bool:
        """將此格子設為地雷
        Returns:
            bool: 裝地雷是否成功
        """
        if self.is_mine:
            return False
        else:
            self.num = 9
            return True

    def set_num(self) -> None:
        """設定此格子的數字"""
        if not self.is_mine:
            self.num = self.count_adjacent_mines()

    def count_adjacent_mines(self) -> int:
        """計算周圍的地雷數量"""
        count = 0
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if self.is_not_(i, j) and self.game.is_mine_at(i, j):
                    count += 1
        return count

    def open(self) -> bool:
        """翻開此格子。

        Returns:
            bool: 是否點擊到地雷
        """
        if self.status == Status.OPENED:
            return False

        self.status = Status.OPENED
        return self.is_mine

    def toggle_flag(self) -> None:
        """切換旗幟狀態"""
        if self.status == Status.NO_FLAG:
            self.status = Status.FLAG
        elif self.status == Status.FLAG:
            self.status = Status.NO_FLAG



NULLTILE = Tile(None, -1, -1)