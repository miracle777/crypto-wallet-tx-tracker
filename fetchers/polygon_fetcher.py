"""
polygon_fetcher.py
==================
Polygon チェーン (Etherscan API V2) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class PolygonFetcher(EVMFetcher):
    """Polygon (POL) チェーンの取引フェッチャー。"""

    NETWORK_NAME    = "polygon"
    CHAIN_ID        = 137    # Polygon Mainnet
    NATIVE_TOKEN    = "POL"  # 旧MATIC / 2024年以降 POL にリブランド
    NATIVE_DECIMALS = 18
