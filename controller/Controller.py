# controller
import sys
import time
from model.Minesweeper import Minesweeper
from view.GUI import View


class Controller:
    def __init__(self, x, y, mines, resurrections):
        self.model = Minesweeper(x, y, mines, resurrections)
        self.view: View = View(x, y)
        self.view.set_controller(self)

        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.timer_running = True

        self.view.create_window()

    def get_elapsed_time(self) -> int:
        if not self.timer_running:
            return int(self.elapsed_time)
        return int(time.time() - self.start_time)

    def update_status(self):
        """更新畫面上顯示的遊戲狀態（地雷剩餘、復活次數）。"""
        mines_left = self.model.get_remaining_mines()
        resurrections = self.model.get_resurrections()
        self.view.update_status(mines_left, resurrections)

    def showerror(self, title, message):
        self.view.showerror(title, message)

    def askyesno(self, title, message) -> bool:
        return self.view.askyesno(title, message)

    def click_tile(self, x: int, y: int):
        returns = self.model.tile_click(x, y)
        if not returns:
            return

        if "update_tile" in returns:
            for update in returns["update_tile"]:
                self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))

        if "game_over" in returns:
            self._handle_end(win=False)
        elif "game_win" in returns:
            self._handle_end(win=True)
        else:
            self.update_status()

    def flag_tile(self, x: int, y: int):
        returns = self.model.flag_tile(x, y)
        if not returns:
            return
        for update in returns.get("update_tile", []):
            self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))
        self.update_status()

    def back(self):
        returns = self.model.back()
        if not returns:
            self.showerror("無法回到上一個步驟", "已沒有可回到的步驟或復活次數已用完。")
            return
        for update in returns.get("update_tile", []):
            self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))
        self.update_status()

    def pause(self):
        if not self.timer_running:
            self.start_time = time.time() - self.elapsed_time
            self.timer_running = True
            return

        self.timer_running = False
        self.elapsed_time = time.time() - self.start_time
        if not self.askyesno("暫停遊戲", "遊戲已暫停，是否繼續遊戲？\n選擇「是」繼續遊戲，選擇「否」結束遊戲。"):
            self._handle_end(win=False)
        else:
            self.start_time = time.time() - self.elapsed_time
            self.timer_running = True

    def _handle_end(self, win: bool):
        # 先計算並暫停計時
        self.elapsed_time = time.time() - self.start_time
        self.timer_running = False
        self.view.gameover()

        message = "恭喜你贏得遊戲！" if win else "你踩到了地雷，遊戲結束！"
        message += f"\n總共耗時 {self.get_elapsed_time()} 秒。"

        # 若未贏且還有復活次數，可選擇回到上一個步驟繼續遊戲
        if not win and self.model.get_resurrections() > 0:
            if self.askyesno("遊戲結束", message + "\n是否要使用復活回到上一步繼續遊戲？"):
                returns = self.model.back()
                if returns:
                    for update in returns.get("update_tile", []):
                        self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))
                    # 恢復遊戲狀態並繼續計時
                    self.model.running = True
                    self.view.running = True
                    self.timer_running = True
                    self.start_time = time.time() - self.elapsed_time
                    self.update_status()
                    return

        # 若不復活或已無復活次數，提示是否重新開始遊戲
        if self.askyesno("遊戲結束", message + "\n要再玩一次嗎？"):
            # 重新進入選擇畫面
            self.view.root.destroy()
            from controller.SettingController import SettingController
            SettingController()
        else:
            self.view.root.destroy()
            sys.exit(0)

    def tile_status(self, x, y):
        return self.model.tile_status(x, y)

    def get_elapsed_seconds(self) -> int:
        return self.get_elapsed_time()
