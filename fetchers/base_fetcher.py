"""
base_fetcher.py
===============
Base チェーン (Etherscan API V2) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class BaseFetcher(EVMFetcher):
    """Base チェーン (L2 on Ethereum) の取引フェッチャー。"""

    NETWORK_NAME    = "base"
    CHAIN_ID        = 8453   # Base Mainnet
    NATIVE_TOKEN    = "ETH"
    NATIVE_DECIMALS = 18
