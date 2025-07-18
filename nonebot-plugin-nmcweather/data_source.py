import json
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# 加载城市数据
QX_DATA = Path(__file__).parent / "qx.json"
with open(QX_DATA, "r", encoding="utf-8") as f:
    CITY_DATABASE: List[Dict[str, str]] = json.load(f)

async def find_city_code(province: str, city: str) -> Optional[str]:
    """
    保留完整行政区划名称的两级模糊匹配：
    1. 先模糊匹配省份（不修改省份名称）
    2. 再在匹配到的省份中模糊匹配城市（不修改城市名称）
    """
    # 仅去除首尾空格（保留"省/市/县"等后缀）
    province = province.strip()
    city = city.strip()
    
    # 第一步：模糊匹配省份（支持简称）
    matched_provinces = [
        item for item in CITY_DATABASE 
        if province in item["province"] or item["province"].startswith(province)
    ]
    
    if not matched_provinces:
        return None
    
    # 第二步：在匹配省份中模糊匹配城市（支持简称）
    for item in matched_provinces:
        # 完整匹配（如"xx市"）或前缀匹配（如"xx"匹配"xx市"）
        if city == item["city"] or item["city"].startswith(city):
            return item["code"]
    
    return None

async def search_city_code(keyword: str) -> Optional[str]:
    """全局模糊搜索（保留完整名称）"""
    keyword = keyword.strip()
    
    # 优先全称匹配（如"北京市"）
    for item in CITY_DATABASE:
        if keyword == item["city"]:
            return item["code"]
    
    # 其次简称匹配（如"北京"匹配"北京市"）
    for item in CITY_DATABASE:
        if item["city"].startswith(keyword):
            return item["code"]
    
    return None

async def get_weather(stationid: str) -> Optional[Dict[str, Any]]:
    """调用 NMC 天气 API"""
    url = f"https://www.nmc.cn/rest/weather?stationid={stationid}&_={int(time.time() * 1000)}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"天气API请求失败: {e}")
        return None


async def get_all_districts(province: str) -> Dict[str, List[str]]:
    """
    获取省份下全部区县名称（不去重）
    返回格式: {
        "province": "匹配到的完整省份名称",
        "districts": ["区县1", "区县2", ...]
    }
    """
    province = province.strip()
    
    # 找出所有匹配的省份名称（保留原始顺序）
    matched_provinces = list({
        item["province"]: None for item in CITY_DATABASE 
        if province in item["province"]
    }.keys())
    
    if not matched_provinces:
        return {"province": "", "districts": []}
    
    # 取名称最长的匹配项
    target_province = max(matched_provinces, key=len)
    
    # 获取该省份下所有区县（保留原始顺序）
    districts = [
        item["city"] for item in CITY_DATABASE
        if item["province"] == target_province
    ]
    
    return {
        "province": target_province,
        "districts": districts
    }