"""
avalanche_fetcher.py
====================
Avalanche C-Chain (Etherscan API V2) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class AvalancheFetcher(EVMFetcher):
    """Avalanche C-Chain の取引フェッチャー。"""

    NETWORK_NAME    = "avalanche"
    CHAIN_ID        = 43114  # Avalanche C-Chain Mainnet
    NATIVE_TOKEN    = "AVAX"
    NATIVE_DECIMALS = 18
