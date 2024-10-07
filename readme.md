# Apple 現貨查詢助手

## 前言

Apple 現貨查詢助手是一款基於 Python 和 Tkinter 開發的桌面應用程式，希望幫助用戶即時檢查 Apple Store 中 iPhone 的現貨狀態，並通過 Line Notify 發送通知。

## 特點

- **即時現貨檢查**：定時檢查選定機型的庫存狀態，確保您能第一時間獲知現貨信息。
- **多機型支持**：支持多款 iPhone 型號，包括 iPhone 16 和 iPhone 16 Pro。
- **Line 通知**：通過 Line Notify 發送現貨通知，讓您不錯過任何購買機會。
- **友好的 GUI**：使用 Tkinter 提供直觀的圖形介面，操作簡便。
- **日誌記錄**：實時顯示監控日誌，讓您了解程式運行狀態。


## 安裝指南

### 1. 安裝 Python

請參考網路教學。
本專案使用 python 3.10.15進行。

### 2. 下載專案

Clone 或下載此專案到本地機器：
```bash
git clone https://github.com/yourusername/apple-store-notifyer.git
cd apple-store-notifyer
```

### 3. 安裝依賴庫

```bash
pip install -r requirements.txt
```

## 使用手冊

1. 啟動應用程式
終端中運行以下命令啟動應用程式：

```bash
cd apple-store-notifyer
python main.py
```
2. 設置 Line Notify Token
在主頁面中，找到「Line Notify Token」的輸入框，輸入您的 Line Notify Token。您可以通過 Line Notify 官方網站 獲取 Token。

([使用教學參考連結](https://greentracks.app/index.php/2023/01/29/line-notify-access-token/))

!!注意!! Line Notify 於 2025 年3 月 31 日結束本服務。後續需要其他替代方案。

3. 選擇 iPhone 機型
在「請選擇機型」部分，選擇您想要監控的 iPhone 機型（如 iPhone 16）。選擇後，相應的型號列表將顯示在下方的表格中。

4. 選擇型號
在型號列表中，選擇您想要監控的具體 iPhone 型號。

5. 開始監控
選擇完型號後，點擊「開始監控」按鈕。此時，所有設置按鈕和輸入框將被禁用，程式將自動跳轉到「監控」頁面，並開始定時檢查庫存狀態。

6. 查看監控日誌
在「監控」頁面，您可以實時查看程式的運行日誌，包括現貨狀態更新和通知發送情況。

7. 停止程式
若要停止監控，請關閉應用程式窗口。

## 未來計畫
1. 添加更多產品監控
2. 跨產品監控
3. 使用其他替代通訊服務

## 貢獻
歡迎提交 issue 或 pull request 來改進此專案。如果您有任何建議或發現錯誤，請隨時聯繫我。

## 授權
此專案使用 GPL 授權。詳情請參見 LICENSE 文件。

