# 這是 model
import random
from typing import Any
from . import Tile  # 從Tile.Tile.py導入 Tile 類別

def func_call_log(func):
    """Decorator for logging when a function is entered and exited.

    This is primarily for debugging and can be removed in production.
    """

    def wrapper(*args, **kwargs):
        print("執行函數", f"{__name__}.Minesweeper.{func.__name__}")
        result = func(*args, **kwargs)
        print("函數執行完畢")
        return result

    return wrapper


class Minesweeper:
    """踩地雷遊戲本體

    Attributes:
        running (bool): 遊戲是否開始或暫停
        x_range (int): 一橫列有幾格
        y_range (int): 一直行有幾格
        mines_num (int): 地雷數
        remaining_tiles (int): 剩餘需翻開的格子數
        is_first_click (bool): 是否是第一次點擊
        resurrections (int): 可回到上一個狀態的次數
        tiles (list[list[Tile.Tile]]): 格子
    """

    def __init__(self, x_range: int, y_range: int, mines_num: int, resurrections=0):
        """初始化遊戲並開始新局。"""
        self.start(x_range, y_range, mines_num, resurrections)

    def start(self, x_range: int, y_range: int, mines_num: int, resurrections=0) -> None:
        """開始/重置一局新的踩地雷遊戲。

        Args:
            x_range (int): 欄數（橫向格子數）
            y_range (int): 列數（直向格子數）
            mines_num (int): 地雷數
            resurrections (int): 可回到上一個狀態的次數

        Raises:
            ValueError: 當設定的地雷數過多、尺寸不合理時拋出。
        """
        if x_range <= 0 or y_range <= 0:
            raise ValueError("遊戲尺寸必須為正整數")
        if mines_num < 0:
            raise ValueError("地雷數不能為負數")
        max_mines = x_range * y_range - 1
        if mines_num > max_mines:
            raise ValueError(f"地雷數過多: 最多可有 {max_mines} 顆 (保留至少 1 個安全格)")

        self.running: bool = True
        self.x_range: int = x_range
        self.y_range: int = y_range
        self.mines_num: int = mines_num
        self.remaining_tiles: int = x_range * y_range - mines_num
        self.is_first_click: bool = True
        self.resurrections: int = resurrections
        # 在踩到地雷時記錄該格位置，方便後續顯示完全結束畫面
        self._last_exploded: tuple[int, int] | None = None

        self.tiles: list[list[Tile.Tile]] = [[Tile.NULLTILE] * y_range for _ in range(x_range)]
        for i in range(x_range):
            for j in range(y_range):
                self.tiles[i][j] = Tile.Tile(self, i, j)

        self.logs: list[dict] = []
        self._save_log()

    def _save_log(self) -> None:
        """儲存遊戲當前狀態快照，用於復活功能回到上一個步驟。"""
        self.logs.append(
            {
                "statuses": [[self.tiles[i][j].status for j in range(self.y_range)] for i in range(self.x_range)],
                "remaining_tiles": self.remaining_tiles,
                "is_first_click": self.is_first_click,
                "resurrections": self.resurrections,
            }
        )

    def laying_mines(self, x, y) -> None:
        """在遊戲板上隨機放置地雷。

        第一個點擊的位置永遠不會放置地雷，以避免玩家第一步就輸。

        Args:
            x (int): 第一次點擊的格子 x 座標
            y (int): 第一次點擊的格子 y 座標
        """
        for _ in range(self.mines_num):
            while True:
                random_x = random.randint(0, self.x_range - 1)
                random_y = random.randint(0, self.y_range - 1)
                # 確保不會裝在第一次點擊的格子上
                # 若該格已經有地雷 (set_mine 回傳 False)，則重新隨機選一格
                if (random_x == x and random_y == y) or not self.tiles[random_x][random_y].set_mine():
                    continue
                break

        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j].set_num()  # 設定格子的數字

    def is_mine_at(self, x: int, y: int) -> bool:
        """檢查指定座標是否為地雷。

        Args:
            x (int): 欄座標
            y (int): 列座標

        Returns:
            bool: 如果座標在遊戲範圍內且該格為地雷，則為 True，否則為 False。
        """
        if 0 <= x < self.x_range and 0 <= y < self.y_range:
            return self.tiles[x][y].is_mine
        return False

    def tile_status(self, x, y) -> Tile.Status:
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

    def tile_click(self, x: int, y: int, save_log: bool = True) -> dict[str, Any]:
        """處理使用者點擊格子的邏輯。

        Args:
            x: 格子的 x 座標。
            y: 格子的 y 座標。
            save_log: 若為 True，會在本次操作後儲存狀態快照 (用於復活 / 回到上一個步驟)。

        Returns:
            dict: 可能包含以下鍵：
                - "update_tile": 要更新的格子顯示資料列表
                - "game_over": 遊戲失敗
                - "game_win": 遊戲勝利
        """
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

        # 翻開格子，若是地雷會進入以下區塊
        if tile.open():
            # 若尚有復活次數，先不要揭露所有地雷，以免玩家看到答案
            reveal_all = self.resurrections <= 0
            result = self._handle_game_over(x, y, reveal_all=reveal_all)
            # 將遊戲結束的狀態存入日誌，方便復活功能還原
            self._save_log()
            return result

        returns: dict[str, list] = {"update_tile": []}

        self.remaining_tiles -= 1
        returns["update_tile"].append(self._tile_display_update(tile))

        if tile.num == 0:
            # 自動翻開周圍的格子
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    if 0 <= i < self.x_range and 0 <= j < self.y_range:
                        neighbor_tile = self.tiles[i][j]
                        if neighbor_tile.status == Tile.Status.NO_FLAG:
                            child = self.tile_click(i, j, save_log=False)
                            # 合併更新資訊
                            returns["update_tile"].extend(child.get("update_tile", []))
                            # 若在遞迴中達成勝利或失敗，立即將結果向上傳遞
                            if "game_over" in child or "game_win" in child:
                                child["update_tile"] = returns["update_tile"]
                                return child

        if self.remaining_tiles == 0:
            return self._handle_win(returns)

        if save_log:
            self._save_log()
        return returns

    def _chord_tile(self, x: int, y: int, save_log: bool = True) -> dict:
        """當已翻開的格子被點擊時，自動翻開周圍未插旗的格子（chording）。

        只有當周圍旗子數等於此格顯示的數字時才會執行。

        Args:
            x: 格子的 x 座標。
            y: 格子的 y 座標。
            save_log: 若為 True，會在動作結束後儲存狀態快照。

        Returns:
            dict: 更新結果，可能包含 "update_tile" 或 "game_over"。
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
                # 合併更新資訊
                returns["update_tile"].extend(result.get("update_tile", []))
                if "game_over" in result or "game_win" in result:
                    result["update_tile"] = returns["update_tile"]
                    return result

        if save_log:
            self._save_log()
        return returns

    def flag_tile(self, x: int, y: int) -> dict[str, list]:
        """切換指定格子的旗幟狀態。

        Args:
            x (int): 格子的 x 座標。
            y (int): 格子的 y 座標。

        Returns:
            dict: 包含需要更新的格子資訊。
        """
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
        self.running = True

        # 將復活次數同步到快照，以便後續的回復操作能正確扣除
        last["resurrections"] = self.resurrections

        updates = []
        for i in range(self.x_range):
            for j in range(self.y_range):
                self.tiles[i][j].status = last["statuses"][i][j]
                updates.append(self._tile_display_update(self.tiles[i][j]))

        return {"update_tile": updates, "resurrections": self.resurrections}

    @func_call_log
    def _handle_game_over(self, x: int, y: int, reveal_all: bool = True) -> dict[str, Any|bool]:
        """處理遊戲失敗的情境。

        Args:
            x: 踩到地雷的格子 x 座標。
            y: 踩到地雷的格子 y 座標。
            reveal_all: 是否要揭示所有地雷（遊戲結束時才會揭示）。

        Returns:
            dict: 包含需要更新的格子顯示資料，以及 game_over 標記。
        """
        self.running = False
        updates = []

        for i in range(self.x_range):
            for j in range(self.y_range):
                tile = self.tiles[i][j]
                if reveal_all and tile.is_mine and tile.status != Tile.Status.OPENED:
                    updates.append(self._tile_display_update(tile, reveal_mine=True))
                elif tile.status == Tile.Status.FLAG and not tile.is_mine:
                    updates.append(self._tile_display_update(tile, wrong_flag=True))

        self._last_exploded = (x, y)
        updates.append(self._tile_display_update(self.tiles[x][y], reveal_exploded=True))
        return {"update_tile": updates, "game_over": True}

    @func_call_log
    def _handle_win(self, returns: dict) -> dict[str, Any|bool]:
        """處理遊戲勝利的情境。

        會把所有尚未插旗的地雷自動插旗，並標記勝利。
        """
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
    ) -> dict[str, int|str]:
        """產生 UI 更新用的格子顯示資訊。

        Args:
            tile: 要更新的格子。
            reveal_mine: 若為 True，顯示所有地雷。
            wrong_flag: 若為 True，顯示錯誤插旗位置。
            reveal_exploded: 若為 True，顯示踩到的地雷。
            flag: 強制將此格顯示為旗子 (用於勝利時補旗)。

        Returns:
            dict: 包含 x/y 座標與 button 要顯示的文字、背景/文字顏色。
        """
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
            info.update({"text": "🚩", "bg": "white", "fg": "black"})
        else:
            info.update({"text": "", "bg": "white", "fg": "black"})

        return info

    def add_logs(self) -> None:
        """手動將目前狀態寫入快照。"""
        self._save_log()

    def reveal_full_game_over(self) -> dict[str, Any]:
        """在遊戲結束時揭露全部地雷與錯誤旗子。

        這個方法不改變遊戲進行邏輯，只回傳用於更新 View 的資料。
        """
        if not self._last_exploded:
            return {}
        x, y = self._last_exploded
        return self._handle_game_over(x, y, reveal_all=True)

    def print_logs(self) -> None:
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
