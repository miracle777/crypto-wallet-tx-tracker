"""
base_fetcher.py
===============
Base チェーン (Blockscout API) の取引取得。
Blockscout は Etherscan 互換 API を無料で提供しています。
APIキー不要（任意）。
"""
from typing import List

from fetchers.evm_fetcher import EVMFetcher


class BaseFetcher(EVMFetcher):
    """Base チェーン (Blockscout) の取引フェッチャー。"""

    NETWORK_NAME     = "base"
    CHAIN_ID         = 0      # Blockscout は chainid パラメータ不要
    NATIVE_TOKEN     = "ETH"
    NATIVE_DECIMALS  = 18

    # Blockscout Base エンドポイント (無料・APIキー不要)
    API_BASE         = "https://base.blockscout.com/api"
    PAGE_SIZE        = 50    # Blockscout 向けに小さめに設定
    REQUEST_TIMEOUT  = 60    # Blockscout はレスポンスが遅いため長めに設定
    RETRIES          = 1     # タイムアウト時は即諦めて次に進む

    def _fetch_paged(
        self, address: str, action: str,
        max_pages: int = None, page_size: int = None,
    ) -> List[dict]:
        """Blockscout 向け: startblock/endblock を省いてシンプルなクエリにする。"""
        all_results: List[dict] = []
        page = 1
        offset = page_size if page_size is not None else self.PAGE_SIZE

        while True:
            # Blockscout は startblock/endblock の全範囲指定でフルスキャンになるため省略
            params = {
                "module": "account",
                "action": action,
                "address": address,
                "page": page,
                "offset": offset,
                "sort": "desc",
            }
            data = self._request(params)
            results = data.get("result", [])

            if not results or not isinstance(results, list):
                break

            for tx in results:
                ts = tx.get("timeStamp") or "0"
                if int(ts) >= self.one_year_ago:
                    all_results.append(tx)

            # 最古レコードが1年以上前なら打ち切り
            last_ts = results[-1].get("timeStamp") or "0"
            if int(last_ts) < self.one_year_ago:
                break
            if len(results) < offset:
                break
            if max_pages is not None and page >= max_pages:
                break

            page += 1

        return all_results
