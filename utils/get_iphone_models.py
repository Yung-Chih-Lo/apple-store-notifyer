# models.py

import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json5
import os


class IPhoneModelsManager:
    """管理 iPhone 型號資訊的類別。"""

    def __init__(self, json_path: str, url: str):
        """
        初始化 IPhoneModelsManager 實例。

        Args:
            json_path (str): 型號 JSON 檔案的路徑。
        """
        self.json_path = json_path
        self.models ={}
        self.url = url
    
    def update_models(self):
        """
        更新 iPhone 型號資訊。
        """
        # 獲取頁面內容
        html_content = self.get_page_content(self.url)
        if html_content is None:
            logging.error("無法獲取頁面內容，更新失敗。")
            return
    
        # 提取 PRODUCT_SELECTION_BOOTSTRAP 資料
        product_selection_data = self.extract_product_selection_bootstrap(html_content)
        if product_selection_data is None:
            logging.error("無法提取 PRODUCT_SELECTION_BOOTSTRAP 資料，更新失敗。")
            return
        
        # 提取機身型號資訊
        self.models = self.get_product_models(product_selection_data)
        if not self.models:
            logging.error("無法提取機身型號資訊，更新失敗。")
            return
        logging.info("成功更新 iPhone 型號資訊。")
        
        # 如果存在，則保存型號資訊到 JSON 檔案
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r', encoding='utf-8') as f:
                ex_data = json.load(f)
                ex_data.update(self.models)
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(ex_data, f, ensure_ascii=False, indent=4)
            logging.info(f"已將型號資訊保存到 {self.json_path}。")
    
    def find_matching_brace(self, s: str, start_index: int) -> int:
        """
        在字串中尋找與起始索引對應的右大括號位置。

        Args:
            s (str): 要搜尋的字串。
            start_index (int): 左大括號的起始索引。

        Returns:
            int: 對應的右大括號的索引，若未找到則返回 -1。
        """
        brace_stack = []
        for i in range(start_index, len(s)):
            if s[i] == '{':
                brace_stack.append('{')
            elif s[i] == '}':
                brace_stack.pop()
                if not brace_stack:
                    return i
        return -1

    def fix_json(self, json_str: str) -> str:
        """
        修正 JSON 字串格式，以便能夠正確解析。

        Args:
            json_str (str): 原始的 JSON 字串。

        Returns:
            str: 修正後的 JSON 字串。
        """
        json_str = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', json_str)
        json_str = json_str.replace("'", '"')
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        return json_str

    def get_page_content(self, url: str) -> str:
        """
        請求目標 URL 並返回頁面內容。

        Args:
            url (str): 要請求的網址。

        Returns:
            str: 網頁內容，若請求失敗則返回 None。
        """
        try:
            ua = UserAgent()
            headers = {
                'User-Agent': ua.random, # 使用隨機 User-Agent
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info(f"成功獲取頁面內容：{url}")
            return response.text
        except requests.RequestException as e:
            logging.error(f"請求頁面失敗：{e}")
            return None

    def extract_product_selection_bootstrap(self, html_content: str) -> dict:
        """
        從頁面 HTML 中提取 window.PRODUCT_SELECTION_BOOTSTRAP 的內容。

        Args:
            html_content (str): 網頁的 HTML 內容。

        Returns:
            dict: 解析後的 PRODUCT_SELECTION_BOOTSTRAP 資料，若解析失敗則返回 None。
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            script_content = script.string
            if script_content is None:
                continue
            if 'window.PRODUCT_SELECTION_BOOTSTRAP' in script_content:
                start = script_content.find('productSelectionData:') # 尋找 'productSelectionData:'
                if start == -1:
                    logging.error("未找到 'productSelectionData:'")
                    return None
                else:
                    start_json = start + len('productSelectionData:')
                    while script_content[start_json] in ' \n\r\t':
                        start_json += 1
                    if script_content[start_json] != '{':
                        logging.error("JSON 數據未以 '{' 開始")
                        return None
                    end_json = self.find_matching_brace(script_content, start_json)
                    if end_json == -1:
                        logging.error("未找到匹配的結束大括號")
                        return None
                    json_str = script_content[start_json:end_json+1]
                    json_str = self.fix_json(json_str)
                    try:
                        data = json5.loads(json_str)
                        logging.info("成功提取 PRODUCT_SELECTION_BOOTSTRAP 資料")
                        return data
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON 解析錯誤: {e}")
                        return None
        return None
    
    def get_product_models(self, product_selection_data: dict) -> dict  :
            """
            從 PRODUCT_SELECTION_BOOTSTRAP 資料中提取機身型號或其他相關資訊。

            Args:
                product_selection_data (dict): PRODUCT_SELECTION_BOOTSTRAP 的資料。

            Returns:
                list: 包含機型資訊的列表，若提取失敗則返回空列表。
            """
            try:
                models = {}
                # 取得顏色資訊
                colors = {} # dict, ex: {"naturaltitanium": "原色鈦金屬"}
                dimension_color = product_selection_data["displayValues"]["dimensionColor"] 
                for key, value in dimension_color.items():
                    if isinstance(value, dict) and value.get("value"):
                       colors[key] = value["value"]
                
                # 取得價格資訊
                prices = {}
                for key, value in product_selection_data["displayValues"]["prices"].items():
                    key = key.upper().replace("_", "/")
                    prices[key] = {
                        "price": value["currentPrice"]["raw_amount"],
                        "currency": value["priceCurrency"]
                    }
                
                
                """
                name (str): 型號名稱，例如 "iPhone 16" or "iPhone 16 Pro Max".
                code (str): 型號代碼，例如 "MYNL3ZP/A".
                price (float): 價格。
                currency (str): 貨幣，例如 "TWD".
                capacity (str): 容量，例如 "128GB" or "256GB".
                color (str): 顏色，例如 "Midnight Green" or "Space Gray".
                """
                
                # 透過 product 取得機型資訊
                products = product_selection_data["products"] # list
                for p in products:
                    name = p["familyType"] # 機型名稱
                    code = p["partNumber"]# 機身代號
                    price = prices[code]["price"]
                    currency = prices[code]["currency"]
                    capacity = p["dimensionCapacity"]
                    color = colors[p["dimensionColor"]]
                    
                    models[code] = {
                        "name": name,
                        "price": price,
                        "currency": currency,
                        "capacity": capacity,
                        "color": color
                    }
                    
                logging.info(f"提取到 {len(models)} 個機身型號。")
                return models
            except Exception as e:
                logging.error(f"提取機身型號時出錯：{e}")
                return {}

if __name__ == "__main__":
    
    # iphone_manager = IPhoneModelsManager(
    #     json_path = "resources/iphone_models.json",
    #     url = "https://www.apple.com/tw/shop/buy-iphone/iphone-16-pro"
    # )
    iphone_manager = IPhoneModelsManager(
        json_path = "resources/iphone_models.json",
        url = "https://www.apple.com/tw/shop/buy-iphone/iphone-16"
    )
    iphone_manager.update_models()