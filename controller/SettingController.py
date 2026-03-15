# controller
from model.Setting import Setting
from view.SettingGui import SettingGui

class SettingController:
    def __init__(self):
        self.model = Setting()
        self.view = SettingGui(self)
        # 將 mainloop 交給 view 的 run 方法，避免在 controller 初始化期間執行
        self.view.run()

    def start(self, x, y, mines, resurrections):
        # 關閉初始設定畫面，並啟動遊戲
        if hasattr(self, "view") and self.view and hasattr(self.view, "setting_window"):
            self.view.destroy()
        self.model.start(x, y, mines, resurrections)

    def check_parameters(self, x, y, mines, resurrections):
        returns = self.model.check_parameters(x, y, mines, resurrections)
        if "message_error" not in returns:
            self.start(int(x.strip()), int(y.strip()), int(mines.strip()), int(resurrections.strip()) if resurrections != "" else 0)
        if "message_error" in returns:
            self.showerror(returns["message_error"][0], returns["message_error"][1])
        for entry in returns.get("delete_entries", []):
            self.entry_delete(entry)

    def showerror(self, title, message):
        self.view.showerror(title, message)

    def entry_delete(self, entry):
        self.view.entry_delete(entry)


