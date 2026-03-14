# view
import tkinter as tk
from tkinter import messagebox

class SettingGui:
    def __init__(self, controller):
        self.controller = controller
        self.widgets = {}
        self.setting_window = tk.Tk()
        self.setting_window.title("歡迎來到踩地雷!")
        self.setting_window.geometry("320x200")

        self.text_label = tk.Label(self.setting_window, text="請選擇遊戲模式:")
        self.text_label.pack(pady=(10, 5))

        self.beginner_button = tk.Button(
            self.setting_window,
            text="初級(9x9, 10地雷)",
            command=lambda: self.controller.start(9, 9, 10, 3),
        )
        self.beginner_button.pack(fill="x", padx=20, pady=2)

        self.intermediate_button = tk.Button(
            self.setting_window,
            text="中級(16x16, 40地雷)",
            command=lambda: self.controller.start(16, 16, 40, 2),
        )
        self.intermediate_button.pack(fill="x", padx=20, pady=2)

        self.expert_button = tk.Button(
            self.setting_window,
            text="進階(30x16, 99地雷)",
            command=lambda: self.controller.start(30, 16, 99, 1),
        )
        self.expert_button.pack(fill="x", padx=20, pady=2)

        self.custom_button = tk.Button(
            self.setting_window, text="自定義", command=self.custom
        )
        self.custom_button.pack(fill="x", padx=20, pady=2)

    def run(self):
        self.setting_window.mainloop()

    def custom(self):
        custom_window = tk.Toplevel(self.setting_window)
        custom_window.title("自定義踩地雷")
        custom_window.geometry("320x220")

        text_label = tk.Label(custom_window, text="請輸入遊戲大小(X,Y)及地雷數:")
        text_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        text_x_label = tk.Label(custom_window, text="X:")
        text_x_label.grid(row=1, column=0, sticky="e", padx=5)
        x_entry = tk.Entry(custom_window)
        x_entry.grid(row=1, column=1, padx=5)
        self.widgets["x_entry"] = x_entry

        text_y_label = tk.Label(custom_window, text="Y:")
        text_y_label.grid(row=2, column=0, sticky="e", padx=5)
        y_entry = tk.Entry(custom_window)
        y_entry.grid(row=2, column=1, padx=5)
        self.widgets["y_entry"] = y_entry

        text_mines_label = tk.Label(custom_window, text="地雷數:")
        text_mines_label.grid(row=3, column=0, sticky="e", padx=5)
        mines_entry = tk.Entry(custom_window)
        mines_entry.grid(row=3, column=1, padx=5)
        self.widgets["mines_entry"] = mines_entry

        resurrections_label = tk.Label(custom_window, text="可復活次數:")
        resurrections_label.grid(row=4, column=0, sticky="e", padx=5)
        resurrections_entry = tk.Entry(custom_window)
        resurrections_entry.grid(row=4, column=1, padx=5)
        self.widgets["resurrections_entry"] = resurrections_entry

        start_button = tk.Button(
            custom_window,
            text="開始遊戲",
            command=lambda: self.controller.check_parameters(
                x_entry.get(), y_entry.get(), mines_entry.get(), resurrections_entry.get()
            ),
        )
        start_button.grid(row=5, column=0, columnspan=2, pady=10)

    def showerror(self, title, message):
        messagebox.showerror(title, message)

    def entry_delete(self, entry):
        widget = self.widgets.get(entry)
        if widget:
            widget.delete(0, tk.END)
