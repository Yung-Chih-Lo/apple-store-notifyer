import logging
import tkinter as tk

class TextHandler(logging.Handler):
    """自定義日誌處理器，用於將日誌寫入 Tkinter 的 Text 小工具。"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            # 自動滾動到最後
            self.text_widget.yview(tk.END)
        self.text_widget.after(0, append)
