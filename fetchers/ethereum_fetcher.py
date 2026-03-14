"""
ethereum_fetcher.py
===================
Ethereum メインネット (Etherscan API V2) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class EthereumFetcher(EVMFetcher):
    """Ethereum メインネットの取引フェッチャー。"""

    NETWORK_NAME    = "ethereum"
    CHAIN_ID        = 1      # Ethereum Mainnet
    NATIVE_TOKEN    = "ETH"
    NATIVE_DECIMALS = 18
