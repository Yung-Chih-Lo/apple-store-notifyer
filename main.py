import os
import logging
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from multiprocessing import freeze_support
from modules import StockChecker, TextHandler

# 確保 log 資料夾存在
os.makedirs('log', exist_ok=True)

# 設置日誌，寫入 log/app.log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log/app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class App:
    """負責建立和管理應用程式 GUI 的類別。"""

    def __init__(self):
        """初始化 App 實例並啟動主迴圈。"""
        self.root = self.create_root_window()  # 創建主視窗
        self.notebook = self.create_notebook(self.root)  # 創建 Notebook 容器，作為頁籤
        self.models = []  # 存儲機型資訊的列表
        self.device_var = tk.StringVar()  # 用於存儲選擇的機型的變數
        self.token_var = tk.StringVar()  # 用於存儲 Line Notify Token 的變數
        self.stock_checker = None  # 將在開始監控時初始化
        self.json_path = "resources/iphone_models.json"  # 請將此路徑修改為你的 JSON 檔案路徑

        # 建立頁面
        self.main_page = self.create_main_page(self.notebook)  # 主頁面
        self.monitoring_page = self.create_monitoring_page(self.notebook)  # 監控頁面

        # 在主頁面中添加元件
        self.setup_main_page(
            self.main_page,
            self.device_var,
            self.token_var,
            self.models
        )

    def create_root_window(self) -> tk.Tk:
        """
        創建主視窗。

        Returns:
            tk.Tk: 主視窗物件。
        """
        root = tk.Tk()
        root.title("Apple 現貨查詢")
        root.geometry("800x600")
        root.resizable(False, False)  # 禁止調整大小

        # 設置背景顏色
        root.configure(bg="#f0f0f0")

        # 設置應用程式圖標（可選）
        # root.iconbitmap('path_to_icon.ico')  # 請將 'path_to_icon.ico' 修改為你的圖標路徑

        return root

    def create_notebook(self, root: tk.Tk) -> ttk.Notebook:
        """
        創建 Notebook 小工具，作為頁籤容器。

        Args:
            root (tk.Tk): 主視窗物件。

        Returns:
            ttk.Notebook: Notebook 物件。
        """
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # 設置 Notebook 樣式
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 12, 'bold'))

        return notebook

    def create_main_page(self, notebook: ttk.Notebook) -> ttk.Frame:
        """
        創建主頁面，包含設備選擇、Token 輸入、型號選擇和開始監控按鈕。

        Args:
            notebook (ttk.Notebook): Notebook 容器。

        Returns:
            ttk.Frame: 主頁面的 Frame 物件。
        """
        page = ttk.Frame(notebook)
        notebook.add(page, text='設定')
        return page

    def create_monitoring_page(self, notebook: ttk.Notebook) -> ttk.Frame:
        """
        創建監控頁面。

        Args:
            notebook (ttk.Notebook): Notebook 容器。

        Returns:
            ttk.Frame: 監控頁面的 Frame 物件。
        """
        page = ttk.Frame(notebook)
        notebook.add(page, text='監控')
        self.log_text = tk.Text(page, state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True)
        return page

    def setup_main_page(
        self,
        page: ttk.Frame,
        device_var: tk.StringVar,
        token_var: tk.StringVar,
        models: list
    ) -> None:
        """
        設置主頁面的元件。

        Args:
            page (ttk.Frame): 主頁面的 Frame 物件。
            device_var (tk.StringVar): 用於存儲選擇的機型的變數。
            token_var (tk.StringVar): 用於存儲 Line Notify Token 的變數。
            models (list): 存儲機型資訊的列表。
        """
        # 創建內框架以增加間距
        inner_frame = ttk.Frame(page, padding=20)
        inner_frame.pack(fill='both', expand=True)

        # Line Token 輸入
        tk.Label(inner_frame, text="Line Notify Token：", font=("Arial", 12, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        token_entry = ttk.Entry(inner_frame, textvariable=token_var, width=50, show="*")
        token_entry.grid(row=0, column=1, sticky='w', pady=(0, 10))

        # 機型選擇標籤
        tk.Label(inner_frame, text="請選擇機型：", font=("Arial", 12, 'bold')).grid(row=1, column=0, sticky='w')

        # 機型選項
        devices = [("iPhone 16", "iphone16"), ("iPhone 16 Plus", "iphone16plus"), ("iPhone 16 Pro", "iphone16pro"), ("iPhone 16 Pro Max", "iphone16promax")]

        # 使用 Frame 組織 Radiobutton
        device_frame = ttk.Frame(inner_frame)
        device_frame.grid(row=1, column=1, sticky='w')

        for idx, (text, value) in enumerate(devices):
            rb = ttk.Radiobutton(device_frame, text=text, variable=device_var, value=value, command=self.on_device_selected)
            rb.pack(side='left', padx=5)

        # 型號列表的 Treeview
        columns = ("型號", "價格", "顏色", "容量", "代碼")
        self.model_tree = ttk.Treeview(inner_frame, columns=columns, show='headings', height=15, selectmode='extended')

        # 定義 Treeview 的列
        for col in columns:
            self.model_tree.heading(col, text=col)
            self.model_tree.column(col, anchor='center', width=140)

        # 添加垂直滾動條
        scrollbar = ttk.Scrollbar(inner_frame, orient='vertical', command=self.model_tree.yview)
        self.model_tree.configure(yscroll=scrollbar.set)
        self.model_tree.grid(row=2, column=0, columnspan=2, sticky='nsew')
        scrollbar.grid(row=2, column=2, sticky='ns')

        # 開始監控按鈕
        start_button = ttk.Button(
            inner_frame,
            text="開始監控",
            command=lambda: self.start_monitoring(
                self.token_var.get(),
                self.models,
                self.model_tree,
                start_button
            )
        )
        start_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # 配置網格權重
        inner_frame.rowconfigure(2, weight=1)
        inner_frame.columnconfigure(1, weight=1)

        # 儲存按鈕和輸入框，以便在監控開始後禁用
        self.start_button = start_button
        self.token_entry = token_entry
        self.device_frame = device_frame

    def on_device_selected(self):
        """
        當選擇機型時載入相應的型號。
        """
        # 取得選擇的機型
        selected_device = self.device_var.get()
        if not selected_device:
            return

        # 清空在頁面上顯示的型號
        self.models.clear()
        for item in self.model_tree.get_children():
            self.model_tree.delete(item)

        # 使用 StockChecker 來載入模型
        checker = StockChecker(token="", json_path=self.json_path)
        loaded_models = checker.get_product_models(selected_device)
        if not loaded_models:
            messagebox.showerror("錯誤", "無法載入型號資訊。")
            return

        self.models = loaded_models

        # 顯示模型選項，讓使用者選擇
        for model in self.models:
            self.model_tree.insert("", "end", values=(
                model['model'],
                f"{model['currency']} {model['price']}",
                model['color'],
                model['capacity'],
                model['code']
            ))

    def start_monitoring(
        self,
        token: str,
        models: list,
        model_tree: ttk.Treeview,
        start_button: ttk.Button
    ) -> None:
        """
        開始監控庫存狀態。

        Args:
            token (str): Line Notify Token。
            models (list): 存儲機型資訊的列表。
            model_tree (ttk.Treeview): 型號列表的 Treeview 物件。
            start_button (ttk.Button): 開始監控按鈕。
        """
        if not token:
            messagebox.showwarning("警告", "請輸入 Token")
            return

        selected_items = model_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請至少選擇一個手機型號")
            return

        # 禁用按鈕和輸入框
        start_button.config(state=tk.DISABLED)
        self.token_entry.config(state=tk.DISABLED)
        for child in self.device_frame.winfo_children():
            child.config(state=tk.DISABLED)


        # 收集選擇的型號資訊
        selected_models = []
        for item in selected_items:
            item_values = model_tree.item(item, 'values')
            model_dict = next((model for model in models if model['code'] == item_values[4]), None)
            if model_dict:
                selected_models.append(model_dict)

        if not selected_models:
            messagebox.showwarning("警告", "未選擇任何有效的手機型號")
            start_button.config(state=tk.NORMAL)
            return

        # 初始化 StockChecker 實例
        self.stock_checker = StockChecker(token=token, json_path=self.json_path)

        # 設置日誌處理器
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        logging.getLogger().addHandler(text_handler)

        # 跳轉到監控頁面
        self.notebook.select(self.monitoring_page)

        # 開始監控
        def monitor():
            self.stock_checker.monitor(selected_models)

        threading.Thread(target=monitor, daemon=True).start()

    def run(self) -> None:
        """啟動應用程式的主迴圈。"""
        self.root.mainloop()

def main():
    """應用程式的主函數。"""
    app = App()
    app.run()

if __name__ == "__main__":
    freeze_support()  # Windows 打包時需要加上這行
    main()
