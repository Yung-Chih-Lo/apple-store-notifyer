# Apple 現貨查詢助手

## 更新
為了讓大家更方便地獲取 Apple 現貨資訊，我們現已推出了全新的付費服務！

### 服務內容：

- 價格：每個 Token 價格為 50 TWD。
- 通知次數：每個 Token 可獲得 3 次成功通知機會。
    - 成功通知是指當有現貨時，我們成功通知到您；若無現貨則不計算通知次數。
- 檢查頻率：每 5 分鐘自動檢查一次庫存狀態，確保您第一時間獲知現貨資訊。
- 專屬綁定：一個 Token 只能綁定一支手機。如需同時監控多個 iPhone，請購買相應數量的 Token。
- 使用流程：
    - 購買 Token：前往我們的購買頁面進行購買。
    - 綁定手機：使用購買的 Token 綁定您想監控的 iPhone 型號。
    - 開始監控：系統將自動開始監控，並在有現貨時通知您。

此付費服務免除了您自行安裝和操作程式的麻煩，讓您更輕鬆地獲得現貨通知，搶先購買心儀的 iPhone！

歡迎前往服務詳情頁面了解[更多資訊](https://yclabtech.com/product/apple-store-notifyer/)。但依舊開放 python 版本給大家使用！

--------
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

### 1. 啟動應用程式

終端中運行以下命令啟動應用程式：
```bash
cd apple-store-notifyer
python main.py
```
### 2. 設置 Line Notify Token

在主頁面中，找到「Line Notify Token」的輸入框，輸入您的 Line Notify Token。您可以通過 Line Notify 官方網站 獲取 Token。

([使用教學參考連結](https://greentracks.app/index.php/2023/01/29/line-notify-access-token/))

!!注意!! Line Notify 於 2025 年3 月 31 日結束本服務。後續需要其他替代方案。

### 3. 選擇 iPhone 機型

在「請選擇機型」部分，選擇您想要監控的 iPhone 機型（如 iPhone 16）。選擇後，相應的型號列表將顯示在下方的表格中。

### 4. 選擇型號

在型號列表中，選擇您想要監控的具體 iPhone 型號。

### 5. 開始監控

選擇完型號後，點擊「開始監控」按鈕。此時，所有設置按鈕和輸入框將被禁用，程式將自動跳轉到「監控」頁面，並開始定時檢查庫存狀態。

### 6. 查看監控日誌
在「監控」頁面，您可以實時查看程式的運行日誌，包括現貨狀態更新和通知發送情況。

### 7. 停止程式
若要停止監控，請關閉應用程式窗口。

## Windows
我有添加一個.exe版本可以使用，使用 pyinstaller 打包，請查看旁邊 release ！

## 未來計畫
1. 添加更多產品監控
2. 跨產品監控
3. 使用其他替代通訊服務

## 貢獻
歡迎提交 issue 或 pull request 來改進此專案。如果您有任何建議或發現錯誤，請隨時聯繫我。

## 授權
此專案使用 AGPL 授權。詳情請參見 LICENSE 文件。
