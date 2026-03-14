# 這是 model
class Setting:
    def __init__(self):
        pass
        # TODO: 之後把x, y, mines, resurrections存起來，以後可以重開一局一樣的遊戲

    def start(self, x, y, mines, resurrections):
        from controller.Controller import Controller
        Controller(x, y, mines, resurrections)


    def check_parameters(self, x, y, mines, resurrections) -> dict[str, str]:
        x, y, mines = x.strip(), y.strip(), mines.strip()
        if resurrections == "": resurrections = "0"  # 如果沒有輸入復活的次數，則預設為0
        resurrections = resurrections.strip()
        returns = {}
        if (not x.isdigit()) or (not y.isdigit()) or (not mines.isdigit()) or (not resurrections.isdigit()):
            returns["message_error"] = ["輸入錯誤!", "請輸入正確的遊戲大小、地雷數及復活的次數"]
            returns["delete_entries"] = ["x_entry", "y_entry", "mines_entry"]
        x, y, mines, resurrections = int(x), int(y), int(mines), int(resurrections)
        if x < 3 or y < 3 or mines < 1:
            returns["message_error"] = ["遊戲大小或地雷數過小!", "遊戲大小不能小於3x3，地雷數不能小於1"]
            returns["delete_entries"] = ["x_entry", "y_entry", "mines_entry"]
        elif x > 49 or y > 23:
            returns["message_error"] = ["遊戲大小過大!", "遊戲大小不能超過49x23"]
            returns["delete_entries"] = ["x_entry", "y_entry"]
        elif mines > x * y:
            returns["message_error"] = ["地雷數過多!", "地雷數不能超過格子數"]
            returns["delete_entries"] = ["mines_entry"]
        elif resurrections < 0:
            returns["message_error"] = ["復活的次數錯誤!", "復活的次數不能小於0"]
            returns["delete_entries"] = ["resurrections_entry"]
        return returns
