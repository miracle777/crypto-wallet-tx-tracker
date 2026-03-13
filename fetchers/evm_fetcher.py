"""
evm_fetcher.py
==============
EVM チェーン向け取引取得の基底クラス。
Etherscan 互換 API (Basescan / Polygonscan / Routescan) に対応。

ページネーション・レート制限・正規化を共通で処理します。
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict

import requests

from classifiers.tx_classifier import classify_evm_tx

logger = logging.getLogger(__name__)

# JST タイムゾーン
JST = timezone(timedelta(hours=9))


class EVMFetcher:
    """EVM チェーン取引取得の基底クラス。"""

    NETWORK_NAME: str = ""   # サブクラスで定義
    API_BASE: str = ""       # サブクラスで定義
    NATIVE_TOKEN: str = ""   # サブクラスで定義
    NATIVE_DECIMALS: int = 18

    def __init__(self, api_key: str):
        self.api_key = api_key
        # 1年前の Unix タイムスタンプ
        self.one_year_ago = int(
            (datetime.now(timezone.utc) - timedelta(days=365)).timestamp()
        )

    # ──────────────────────────────────────────────────────────
    # 内部ユーティリティ
    # ──────────────────────────────────────────────────────────

    def _request(self, params: dict, retries: int = 3) -> dict:
        """リトライ付き API リクエスト。"""
        params = {**params, "apikey": self.api_key}
        for attempt in range(retries):
            try:
                resp = requests.get(self.API_BASE, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                if data.get("status") == "1":
                    return data
                # "No transactions found" は正常終了とみなす
                msg = data.get("message", "")
                if "No " in msg and ("found" in msg or "record" in msg.lower()):
                    return {"result": []}
                logger.warning(
                    "[%s] API warning: %s", self.NETWORK_NAME, data.get("message")
                )
                return {"result": []}

            except requests.RequestException as exc:
                logger.warning(
                    "[%s] Request failed (attempt %d/%d): %s",
                    self.NETWORK_NAME, attempt + 1, retries, exc,
                )
                if attempt < retries - 1:
                    time.sleep(2**attempt)

        return {"result": []}

    def _fetch_paged(self, address: str, action: str) -> List[dict]:
        """ページネーション付きで全件取得（過去1年分のみ）。"""
        all_results: List[dict] = []
        page = 1

        while True:
            params = {
                "module": "account",
                "action": action,
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": page,
                "offset": 10000,
                "sort": "desc",
            }
            data = self._request(params)
            results = data.get("result", [])

            if not results or not isinstance(results, list):
                break

            for tx in results:
                if int(tx.get("timeStamp", 0)) >= self.one_year_ago:
                    all_results.append(tx)

            # 最古レコードが1年以上前なら打ち切り
            if int(results[-1].get("timeStamp", 0)) < self.one_year_ago:
                break
            if len(results) < 10000:
                break

            page += 1
            time.sleep(0.25)  # レート制限対策

        return all_results

    def _normalize(self, tx: dict, address: str, source: str) -> Dict:
        """生 API レスポンスを共通フォーマットに正規化。"""
        ts = int(tx.get("timeStamp", 0))
        dt = datetime.fromtimestamp(ts, tz=JST)

        from_addr = (tx.get("from") or "").lower()
        to_addr   = (tx.get("to") or "").lower()
        addr      = address.lower()

        # トークン / 金額
        if source == "tokentx":
            direction    = "IN" if to_addr == addr else "OUT"
            decimals     = int(tx.get("tokenDecimal", 18))
            value        = int(tx.get("value", 0)) / (10**decimals)
            token_symbol = tx.get("tokenSymbol", "UNKNOWN")
        elif source == "internal":
            direction    = "IN" if to_addr == addr else "OUT"
            value        = int(tx.get("value", 0)) / (10**self.NATIVE_DECIMALS)
            token_symbol = self.NATIVE_TOKEN
        else:  # normal
            direction    = "OUT" if from_addr == addr else "IN"
            value        = int(tx.get("value", 0)) / (10**self.NATIVE_DECIMALS)
            token_symbol = self.NATIVE_TOKEN

        # ガス手数料（自分が送信者の通常 tx のみ）
        gas_fee_str = ""
        if source == "normal" and from_addr == addr:
            gas_used = int(tx.get("gasUsed", 0))
            gas_price = int(tx.get("gasPrice", 0))
            gas_fee = gas_used * gas_price / (10**self.NATIVE_DECIMALS)
            gas_fee_str = f"{gas_fee:.8f}".rstrip("0").rstrip(".")

        # 取引タイプ分類
        tx["_source"] = source
        tx_type = classify_evm_tx(tx, address, self.NETWORK_NAME)

        status = "SUCCESS" if tx.get("isError", "0") == "0" else "FAILED"

        return {
            "date":         dt.strftime("%Y-%m-%d %H:%M:%S"),
            "network":      self.NETWORK_NAME,
            "tx_hash":      tx.get("hash", ""),
            "from":         tx.get("from", ""),
            "to":           tx.get("to", ""),
            "value":        f"{value:.8f}".rstrip("0").rstrip(".") if value else "0",
            "token_symbol": token_symbol,
            "gas_fee":      gas_fee_str,
            "direction":    direction,
            "tx_type":      tx_type,
            "status":       status,
        }

    # ──────────────────────────────────────────────────────────
    # 公開 API
    # ──────────────────────────────────────────────────────────

    def fetch(self, address: str) -> List[Dict]:
        """
        指定アドレスの過去1年分の取引を全種類取得し、
        正規化済みレコードのリストを返します。
        """
        logger.info("[%s] 取引を取得中: %s", self.NETWORK_NAME, address)
        records: List[Dict] = []

        # 1. 通常トランザクション
        logger.info("[%s] 通常TX を取得中...", self.NETWORK_NAME)
        for tx in self._fetch_paged(address, "txlist"):
            records.append(self._normalize(tx, address, "normal"))

        # 2. ERC-20 トークン転送
        logger.info("[%s] ERC-20 転送を取得中...", self.NETWORK_NAME)
        for tx in self._fetch_paged(address, "tokentx"):
            records.append(self._normalize(tx, address, "tokentx"))

        # 3. 内部トランザクション
        logger.info("[%s] 内部TX を取得中...", self.NETWORK_NAME)
        for tx in self._fetch_paged(address, "txlistinternal"):
            records.append(self._normalize(tx, address, "internal"))

        # 日付降順ソート
        records.sort(key=lambda r: r["date"], reverse=True)
        logger.info("[%s] 合計 %d 件取得", self.NETWORK_NAME, len(records))
        return records
