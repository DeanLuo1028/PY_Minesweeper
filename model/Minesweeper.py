# 這是 model
import random
from . import Tile  # 從Tile.Tile.py導入 Tile 類別


class Minesweeper:
    """踩地雷遊戲本體
    Attributes:
        running: bool 遊戲是否開始或暫停
        x_range: int 一橫列有幾格
        y_range: int 一直行有幾格
        mines_num: int 地雷數
        remaining_tiles: 剩餘需翻開的格子數
        is_first_click: bool 是否是第一次點擊
        resurrections: 可回到上一個狀態的次數
        tiles: 格子
    """
    def __init__(self, x_range: int, y_range: int, mines_num: int , resurrections=0):
        self.start(x_range, y_range, mines_num , resurrections)

    def start(self, x_range: int, y_range: int, mines_num: int , resurrections=0):
        self.running: bool = True
        self.x_range: int = x_range
        self.y_range: int = y_range
        self.mines_num: int = mines_num
        self.remaining_tiles: int = x_range * y_range - mines_num
        self.is_first_click = True
        self.resurrections = resurrections

        self.tiles: list[list[Tile.Tile]] = [[Tile.NullTile] * y_range for _ in range(x_range)]
        for i in range(x_range):
            for j in range(y_range):
                self.tiles[i][j] = Tile.Tile(self, i, j)

        self.logs: list[dict] = []
        self._save_log()

    def _save_log(self):
        self.logs.append(
            {
                "statuses": [[self.tiles[i][j].status for j in range(self.y_range)] for i in range(self.x_range)],
                "remaining_tiles": self.remaining_tiles,
                "is_first_click": self.is_first_click,
                "resurrections": self.resurrections,
            }
        )

    def laying_mines(self, x, y): # 傳入第一個點擊的格子的座標，確保第一次點擊的格子不是地雷
        for _ in range(self.mines_num):
            while True:
                random_x = random.randint(0, self.x_range - 1)
                random_y = random.randint(0, self.y_range - 1)
                # 確保不會裝在第一次點擊的格子上             # False代表已經有地雷了，裝地雷失敗
                if (random_x == x and random_y == y) or not self.tiles[random_x][random_y].set_mine():
                    continue
                break # True代表裝地雷成功，跳出迴圈

        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j].set_num() # 設定格子的數字

    def is_mine_at(self, x, y):
        if 0 <= x < self.x_range and 0 <= y < self.y_range:
            return self.tiles[x][y].is_mine
        return False

    def tile_status(self, x, y):
        """取得指定格子的狀態（OPENED/FLAG/NO_FLAG）。"""
        return self.tiles[x][y].status

    def get_flag_count(self) -> int:
        """計算目前插上的旗幟數量。"""
        return sum(1 for row in self.tiles for tile in row if tile.status == Tile.Status.FLAG)

    def get_remaining_mines(self) -> int:
        """預估剩餘地雷數（地雷總數 - 旗幟數）。"""
        return max(0, self.mines_num - self.get_flag_count())

    def get_resurrections(self) -> int:
        """取得目前可用的復活次數。"""
        return self.resurrections

    def tile_click(self, x: int, y: int, save_log: bool = True) -> dict:
        if not self.running:
            return {}

        tile = self.tiles[x][y]
        # 如果格子已翻開，則嘗試自動翻開周圍未插旗的格子（chording）
        if tile.status == Tile.Status.OPENED:
            return self._chord_tile(x, y, save_log=save_log)

        # 插旗的格子不會動作
        if tile.status == Tile.Status.FLAG:
            return {}

        if self.is_first_click:
            self.laying_mines(x, y)
            self.is_first_click = False

        returns: dict[str, list] = {"update_tile": []}

        hit_mine = tile.open()
        if hit_mine:
            result = self._handle_game_over(x, y)
            # 將遊戲結束的狀態存入 log，方便復活功能恢復到上一步
            self._save_log()
            return result

        self.remaining_tiles -= 1
        returns["update_tile"].append(self._tile_display_update(tile))

        if tile.num == 0:
            # 自動翻開周圍的格子
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if 0 <= i < self.x_range and 0 <= j < self.y_range:
                        neighbor_tile = self.tiles[i][j]
                        if neighbor_tile.status == Tile.Status.NO_FLAG:
                            returns["update_tile"].extend(self.tile_click(i, j, save_log=False)["update_tile"])

        if self.remaining_tiles == 0:
            return self._handle_win(returns)

        if save_log:
            self._save_log()
        return returns

    def _chord_tile(self, x: int, y: int, save_log: bool = True) -> dict:
        """當已翻開的格子被點擊時，自動翻開周圍未插旗的格子（chording）。

        只有當周圍旗子數等於此格顯示的數字時才會執行。
        """
        tile = self.tiles[x][y]
        if tile.status != Tile.Status.OPENED or tile.num == 0:
            return {}

        # 計算周圍旗子數
        flags = 0
        neighbors = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (i, j) == (x, y):
                    continue
                if 0 <= i < self.x_range and 0 <= j < self.y_range:
                    neighbors.append((i, j))
                    if self.tiles[i][j].status == Tile.Status.FLAG:
                        flags += 1

        # 旗子數小於數字時不做任何動作
        if flags < tile.num:
            return {}

        returns: dict[str, list] = {"update_tile": []}

        # 自動翻開周圍未插旗的格子
        for i, j in neighbors:
            neighbor = self.tiles[i][j]
            if neighbor.status == Tile.Status.NO_FLAG:
                result = self.tile_click(i, j, save_log=False)
                if "game_over" in result:
                    return result
                returns["update_tile"].extend(result.get("update_tile", []))

        if save_log:
            self._save_log()
        return returns

    def flag_tile(self, x: int, y: int) -> dict:
        if not self.running:
            return {}

        tile = self.tiles[x][y]
        if tile.status == Tile.Status.OPENED:
            return {}

        tile.toggle_flag()
        self._save_log()
        return {"update_tile": [self._tile_display_update(tile)]}

    def back(self) -> dict:
        """回到上一步（復活功能）：還原到上一個操作前的狀態。

        Returns:
            dict: 包含需要更新的格子資訊與剩餘復活次數。
        """
        if self.resurrections <= 0 or len(self.logs) <= 1:
            return {}

        # 使用一次復活機會
        self.resurrections -= 1

        # 恢復到上一個狀態快照
        self.logs.pop()
        last = self.logs[-1]
        self.remaining_tiles = last["remaining_tiles"]
        self.is_first_click = last["is_first_click"]

        # 將復活次數同步到快照，以便後續的回復操作能正確扣除
        last["resurrections"] = self.resurrections

        updates = []
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j].status = last["statuses"][i][j]
                updates.append(self._tile_display_update(self.tiles[i][j]))

        return {"update_tile": updates, "resurrections": self.resurrections}

    def _handle_game_over(self, x: int, y: int) -> dict:
        self.running = False
        updates = []

        for i in range(self.x_range):
            for j in range(self.y_range):
                tile = self.tiles[i][j]
                if tile.is_mine and tile.status != Tile.Status.OPENED:
                    updates.append(self._tile_display_update(tile, reveal_mine=True))
                elif tile.status == Tile.Status.FLAG and not tile.is_mine:
                    updates.append(self._tile_display_update(tile, wrong_flag=True))

        updates.append(self._tile_display_update(self.tiles[x][y], reveal_exploded=True))
        return {"update_tile": updates, "game_over": True}

    def _handle_win(self, returns: dict) -> dict:
        self.running = False
        updates = returns.get("update_tile", [])
        for i in range(self.x_range):
            for j in range(self.y_range):
                tile = self.tiles[i][j]
                if tile.is_mine and tile.status != Tile.Status.OPENED:
                    tile.status = Tile.Status.FLAG
                    updates.append(self._tile_display_update(tile, flag=True))
        return {"update_tile": updates, "game_win": True}

    def _tile_display_update(
        self,
        tile: Tile.Tile,
        reveal_mine: bool = False,
        wrong_flag: bool = False,
        reveal_exploded: bool = False,
        flag: bool = False,
    ) -> dict:
        info = {"x": tile.x, "y": tile.y, "text": "", "bg": "", "fg": ""}

        if reveal_exploded:
            info.update({"text": "💥", "bg": "red", "fg": "white"})
            return info

        if wrong_flag:
            info.update({"text": "❌", "bg": "orange", "fg": "white"})
            return info

        if reveal_mine:
            info.update({"text": "💣", "bg": "black", "fg": "white"})
            return info

        if tile.status == Tile.Status.OPENED:
            text = "" if tile.num == 0 else str(tile.num)
            info.update({"text": text, "bg": "gray", "fg": "black"})
        elif tile.status == Tile.Status.FLAG or flag:
            info.update({"text": "🚩", "bg": "yellow", "fg": "black"})
        else:
            info.update({"text": "", "bg": "white", "fg": "black"})

        return info

    def add_logs(self):
        self._save_log()

    def print_logs(self):
        """印出目前快照的格子狀態（debug 用）。"""
        print("print_logs")
        last = self.logs[-1]
        # 是為了輸出和畫面相同才先遍歷 y，再遍歷 x
        for j in range(self.y_range):
            for i in range(self.x_range):
                status = last["statuses"][i][j]
                if status == Tile.Status.OPENED:
                    print(self.tiles[i][j].num, end="")
                elif status == Tile.Status.FLAG:
                    print("F", end="")
                else:
                    print(".", end="")
            print()
