"""
avalanche_fetcher.py
====================
Avalanche C-Chain (Routescan API) の取引取得。
"""
from fetchers.evm_fetcher import EVMFetcher


class AvalancheFetcher(EVMFetcher):
    """Avalanche C-Chain の取引フェッチャー。
    
    Routescan (旧 Snowtrace) の Etherscan 互換エンドポイントを使用します。
    旧 Snowtrace API キーもそのまま利用可能です。
    """

    NETWORK_NAME    = "avalanche"
    # Routescan の Etherscan 互換エンドポイント (chain ID: 43114 = Avalanche C-Chain)
    API_BASE        = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"
    NATIVE_TOKEN    = "AVAX"
    NATIVE_DECIMALS = 18
