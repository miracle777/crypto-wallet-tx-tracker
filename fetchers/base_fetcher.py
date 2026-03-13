"""
base_fetcher.py
===============
Base チェーン (Basescan API) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class BaseFetcher(EVMFetcher):
    """Base チェーン (L2 on Ethereum) の取引フェッチャー。"""

    NETWORK_NAME    = "base"
    API_BASE        = "https://api.basescan.org/api"
    NATIVE_TOKEN    = "ETH"
    NATIVE_DECIMALS = 18
