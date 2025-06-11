import json
import logging
import time
import requests
from fake_useragent import UserAgent


class StockChecker:
    """負責檢查 iPhone 現貨並發送通知的類別。"""

    def __init__(self, token: str, json_path: str):
        """
        初始化 StockChecker 實例。

        Args:
            token (str): 用於發送通知的 Line Notify Token。
            json_path (str): 本地 JSON 檔案的路徑。
        """
        self.token = token
        self.json_path = json_path

    def get_product_models(self, selected_device: str) -> list:
        """
        從本地 JSON 檔案中提取機型資訊。

        Args:
            selected_device (str): 選擇的機型代碼，如 "iphone16" 或 "iphone16pro"。

        Returns:
            list: 包含機型資訊的列表，若提取失敗則返回空列表。
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            models = []
            for code, info in data.items():
                if selected_device == info['name']:
                    model = {
                        'code': code,
                        'model': info['name'],
                        'price': info['price'],
                        'currency': info['currency'],
                        'capacity': info['capacity'],
                        'color': info['color']
                    }
                    models.append(model)
            models.sort(key=lambda x: x['color'])
            logging.info(f"成功從 JSON 檔案中提取 {selected_device} 的機型資訊。")
            return models
        except Exception as e:
            logging.error(f"從 JSON 檔案中提取機型資訊失敗：{e}")
            return []

    def request_json_based_on_model(self, model_code: str) -> dict:
        """
        根據機身型號發送後續的 JSON 請求，並返回解析後的資料。

        Args:
            model_code (str): 機型的代碼。

        Returns:
            dict: 解析後的 JSON 資料，若請求失敗則返回 None。
        """
        api_endpoint = f"https://www.apple.com/tw/shop/fulfillment-messages?pl=true&mts.0=regular&mts.1=compact&cppart=UNLOCKED/WW&parts.0={model_code}&searchNearby=true&store=R713"

        try:
            headers = {
                'User-Agent': UserAgent().random,
                'Accept': 'application/json',
            }
            response = requests.get(api_endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logging.info(f"成功獲取模型 {model_code} 的 JSON 資料。")
            return data
        except requests.RequestException as e:
            logging.error(f"請求 JSON 資料失敗：{e}")
            return None

    def check_availability(self, json_data: dict, model_code: str) -> tuple:
        """
        檢查 JSON 資料中的庫存狀態，並返回有無現貨的結果。

        Args:
            json_data (dict): 從 API 獲取的 JSON 資料。
            model_code (str): 機型的代碼。

        Returns:
            tuple: (bool, str 或 None) 是否有現貨及現貨所在的店鋪名稱。
        """
        try:
            stores = json_data.get('body', {}).get('PickupMessage', {}).get('stores', [])
            if not stores:
                stores = json_data.get('body', {}).get('content', {}).get('pickupMessage', {}).get('stores', [])
            for store in stores:
                parts_availability = store.get('partsAvailability', {})
                for part_number, availability in parts_availability.items():
                    if availability.get('pickupDisplay') == 'available' and part_number == model_code:
                        return True, store['storeName']
            return False, None
        except Exception as e:
            logging.error(f"檢查庫存時出錯：{e}")
            return False, None

    def send_notification(self, message: str) -> None:
        """
        使用 Line Notify 發送通知訊息。

        Args:
            message (str): 要發送的通知訊息。
        """
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'message': message
        }
        try:
            response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
            if response.status_code == 200:
                logging.info("通知發送成功")
            else:
                logging.error(f"通知發送失敗：{response.status_code}, {response.text}")
        except requests.RequestException as e:
            logging.error(f"通知發送時發生錯誤：{e}")

    def monitor(self, selected_models: list) -> None:
        """
        開始監控選定的機型庫存狀態。

        Args:
            selected_models (list): 要監控的機型資訊列表。
        """
        self.send_notification("程式已啟動，開始監控現貨情況。")
        next_alive_time = time.time() + 3600  # 下一次發送 alive 訊息的時間

        while True:
            for model in selected_models:
                model_code = model['code']
                json_data = self.request_json_based_on_model(model_code)
                if json_data:
                    available, store_name = self.check_availability(json_data, model_code)
                    if available:
                        # 修改通知訊息，包含容量資訊
                        message = f"{model['model']} - {model['color']} ({model['capacity']}) 在 {store_name} 有現貨！"
                        self.send_notification(message)
                        logging.info(message)
                    else:
                        logging.info(f"{model['model']} - {model['color']} ({model['capacity']}) 目前無現貨")
                else:
                    logging.error("無法獲取庫存資訊。")
            current_time = time.time()
            if current_time >= next_alive_time:
                self.send_notification("程式正常運作中")
                next_alive_time = current_time + 3600
            logging.info("等待 5 分鐘後重新檢查...")
            time.sleep(300)  # 每五分鐘檢查一次
