# view
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class View:
    def __init__(self, x_range: int, y_range: int):
        self.x_range = x_range
        self.y_range = y_range
        self.buttons: list[list[tk.Button]] = [[None for _ in range(y_range)] for _ in range(x_range)]
        self.tile_bg = "white" # 按鈕背景顏色
        self.tile_fg = "black" # 按鈕文字顏色
        self.running: bool = False

    def set_controller(self, controller):
        self.controller = controller

    def create_window(self):
        self.root = tk.Tk()
        self.root.title("踩地雷!")

        if self.x_range < 10 and self.y_range < 10:
            self.root.geometry("500x700")
            self.font_size = 24
        elif 10 <= self.x_range < 17 and 10 <= self.y_range <= 16:
            self.root.geometry("1000x700")
            self.font_size = 16
        elif 17 <= self.x_range <= 30 and 16 <= self.y_range < 24:
            self.root.state('zoomed')
            self.font_size = 16
        else:
            self.root.state('zoomed')
            self.font_size = 12

        # 創建格子按鈕並設置到界面
        self.panel = tk.Frame(self.root)
        self.panel.grid(row=0, column=0, rowspan=3)
        for i in range(self.x_range):
            for j in range(self.y_range):
                btn = tk.Button(
                    self.panel,
                    text="",
                    width=2,
                    height=1,
                    font=("Arial", self.font_size),
                    command=lambda i=i, j=j: self.controller.click_tile(i, j),
                )
                btn.grid(row=i, column=j)
                btn.bind("<Button-3>", lambda event, i=i, j=j: self.controller.flag_tile(i, j))
                self.buttons[i][j] = btn

        self.pause_btn = tk.Button(self.root, text="暫停", command=self.controller.pause, bg="gray", fg="white")
        self.pause_btn.grid(row=0, column=1, padx=10, pady=2)

        self.timer_var = tk.StringVar()
        self.timer_var.set("時間: 0秒")
        self.timer = tk.Label(self.root, textvariable=self.timer_var, bg="pink", fg="black")
        self.timer.grid(row=1, column=1, padx=10, pady=2)

        # 顯示剩餘地雷與可復活次數（可由 Controller 更新）
        self.status_var = tk.StringVar()
        self.status_var.set("地雷剩餘: 0    復活: 0")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bg="lightgray", fg="black")
        self.status_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")

        self.color_picker = tk.Button(self.root, text="設定格子背景色與文字顏色", command=self.set_tile_bgfg)
        self.color_picker.grid(row=3, column=0, padx=10, pady=2)

        self.back_btn = tk.Button(self.root, text="回到上一步", command=self.controller.back, bg="gray", fg="white")
        self.back_btn.grid(row=2, column=1, padx=10, pady=2)

        self.running = True
        self.update_timer_loop()
        self.root.mainloop()

    def update_tile(self, x: int, y: int, text: str, bg: str = "", fg: str = ""):
        """更新指定格子的按鈕顯示內容

        Args:
            x (int): 格子的x座標
            y (int): 格子的y座標
            text (str): 按鈕上顯示的文字
            bg (str, optional): 按鈕背景顏色. Defaults to "".
            fg (str, optional): 按鈕文字顏色. Defaults to "".
        """
        button = self.buttons[x][y]
        button.config(text=text)
        if bg:
            button.config(bg=bg)
        if fg:
            button.config(fg=fg)
    
    def gameover(self):
        self.running = False

    def update_timer(self, seconds: int):
        """更新計時器顯示"""
        self.timer_var.set(f"時間: {seconds}秒")

    def update_timer_loop(self):
        """每秒更新一次遊戲時間、剩餘地雷與復活次數顯示。"""
        if self.running and hasattr(self, "controller"):
            seconds = self.controller.get_elapsed_seconds()
            self.update_timer(seconds)
            # 由 Controller 提供遊戲狀態（地雷剩餘、復活次數）
            self.controller.update_status()
            self.root.after(1000, self.update_timer_loop)

    def update_status(self, mines_left: int, resurrections: int):
        """更新畫面上顯示的遊戲狀態（地雷剩餘、復活次數）。"""
        self.status_var.set(f"地雷剩餘: {mines_left}    復活: {resurrections}")

    def set_tile_bgfg(self):
        # 彈出視窗讓玩家調整格子的背景/文字顏色
        dialog = tk.Toplevel(self.root)
        dialog.title("設定格子背景色與文字顏色")
        dialog.geometry("320x160")

        colors = ["white", "black", "gray", "red", "green", "blue", "yellow", "pink", "orange"]

        bg_var = tk.StringVar(value=self.tile_bg)
        fg_var = tk.StringVar(value=self.tile_fg)

        tk.Label(dialog, text="格子背景色:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        bg_box = ttk.Combobox(dialog, values=colors, textvariable=bg_var, state="readonly")
        bg_box.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(dialog, text="文字顏色:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        fg_box = ttk.Combobox(dialog, values=colors, textvariable=fg_var, state="readonly")
        fg_box.grid(row=1, column=1, padx=6, pady=6)

        def apply_colors():
            self.tile_bg = bg_var.get()
            self.tile_fg = fg_var.get()
            for i in range(self.x_range):
                for j in range(self.y_range):
                    status = self.controller.tile_status(i, j)
                    if status and getattr(status, "name", None) == "OPENED":
                        continue
                    self.buttons[i][j].config(bg=self.tile_bg, fg=self.tile_fg)
            dialog.destroy()

        tk.Button(dialog, text="確定", command=apply_colors).grid(row=2, column=0, columnspan=2, pady=10)

    def showerror(self, title, message):
        messagebox.showerror(title, message)
    
    def askyesno(self, title, message) -> bool:
        return messagebox.askyesno(title, message)
