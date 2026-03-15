# controller
from sys import exit
import time
from model.Minesweeper import Minesweeper
from view.GUI import View

def func_call_log(func):
    def wrapper(*args, **kwargs):
        print("執行函數", f"{__name__}.Controller.{func.__name__}")
        result = func(*args, **kwargs)
        print("函數執行完畢")
        return result
    return wrapper
class Controller:
    """遊戲控制器 (Controller) - 負責協調 Model 與 View 的溝通。"""

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
        """處理使用者點擊格子事件。

        會請 model 進行遊戲邏輯處理，並將更新結果傳給 view 顯示。
        """
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
        """處理使用者右鍵插旗事件。"""
        returns = self.model.flag_tile(x, y)
        if not returns:
            return
        for update in returns.get("update_tile", []):
            self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))
        self.update_status()

    def back(self):
        """回到上一個步驟（復活功能）。"""
        returns = self.model.back()
        if not returns:
            self.showerror("無法回到上一個步驟", "已沒有可回到的步驟或復活次數已用完。")
            return
        for update in returns.get("update_tile", []):
            self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))
        self.update_status()

    def pause(self):
        """暫停/繼續遊戲並詢問玩家是否要結束遊戲。"""
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

    @func_call_log
    def _handle_end(self, win: bool):
        """處理遊戲結束的邏輯。

        會顯示勝利/失敗提示，並提供復活選項或重新開始遊戲。
        """
        # 先計算並暫停計時
        self.elapsed_time = time.time() - self.start_time
        self.timer_running = False
        self.view.gameover()

        message = "恭喜你贏得遊戲！" if win else "你踩到了地雷，遊戲失敗！"
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
            else:
                # 玩家選擇不復活 ⇒ 顯示完整結束畫面（揭露所有地雷、錯誤旗子）
                for update in self.model.reveal_full_game_over().get("update_tile", []):
                    self.view.update_tile(update["x"], update["y"], update["text"], update.get("bg"), update.get("fg"))

        # 若不復活或已無復活次數，提示是否重新開始遊戲
        if self.askyesno("遊戲結束", message + "\n要再玩一次嗎？"):
            # 重新進入選擇畫面
            self.view.destroy_window()
            from controller.SettingController import SettingController
            SettingController()
        else:
            self.view.destroy_window()
            exit(0)

    def tile_status(self, x, y):
        """取得指定格子的狀態（OPENED/FLAG/NO_FLAG）。"""
        return self.model.tile_status(x, y)

    def get_elapsed_seconds(self) -> int:
        """取得已經過的秒數（用於 UI 顯示）。"""
        return self.get_elapsed_time()
