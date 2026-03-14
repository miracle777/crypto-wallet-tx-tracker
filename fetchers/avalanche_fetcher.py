"""
avalanche_fetcher.py
====================
Avalanche C-Chain (Routescan API) の取引取得。

Avalanche は Etherscan グループではないため、Routescan の独自エンドポイントを使用します。
APIキーは ROUTESCAN_API_KEY (または旧 SNOWTRACE_API_KEY) を使用します。
"""
from fetchers.evm_fetcher import EVMFetcher


class AvalancheFetcher(EVMFetcher):
    """Avalanche C-Chain の取引フェッチャー。"""

    NETWORK_NAME    = "avalanche"
    CHAIN_ID        = 0      # 0 = Etherscan V2 の chainid を使わない (Routescan 独自エンドポイント)
    API_BASE        = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"
    NATIVE_TOKEN    = "AVAX"
    NATIVE_DECIMALS = 18
