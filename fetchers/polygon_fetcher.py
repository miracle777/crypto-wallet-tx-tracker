"""
polygon_fetcher.py
==================
Polygon チェーン (Polygonscan API) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class PolygonFetcher(EVMFetcher):
    """Polygon (MATIC) チェーンの取引フェッチャー。"""

    NETWORK_NAME    = "polygon"
    API_BASE        = "https://api.polygonscan.com/api"
    NATIVE_TOKEN    = "POL"   # 旧MATIC / 2024年以降 POL にリブランド
    NATIVE_DECIMALS = 18
