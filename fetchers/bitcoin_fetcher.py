"""
bitcoin_fetcher.py
==================
Bitcoin の取引取得モジュール。
Blockstream.info API を使用 (APIキー不要・無料)。

Bitcoin は UTXO モデルのため、以下の情報を提供します:
  - direction: IN (受取) / OUT (送金)
  - tx_type:   RECEIVE / SEND
  - value: BTC 単位 (satoshi → BTC 変換)
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

BLOCKSTREAM_API = "https://blockstream.info/api"
JST = timezone(timedelta(hours=9))
SAT_TO_BTC = 1e8  # 1 BTC = 100,000,000 satoshi


class BitcoinFetcher:
    """Bitcoin 取引フェッチャー (Blockstream.info)。"""

    def __init__(self):
        self.one_year_ago = int(
            (datetime.now(timezone.utc) - timedelta(days=365)).timestamp()
        )

    # ──────────────────────────────────────────────────────────
    # 内部ユーティリティ
    # ──────────────────────────────────────────────────────────

    def _get(self, url: str, retries: int = 3) -> Optional[object]:
        """リトライ付き GET リクエスト。"""
        for attempt in range(retries):
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning(
                    "[bitcoin] Request failed (attempt %d/%d): %s",
                    attempt + 1, retries, exc,
                )
                if attempt < retries - 1:
                    time.sleep(2**attempt)
        return None

    def _fetch_txs(self, address: str) -> List[dict]:
        """Blockstream API からトランザクションを全件取得 (最大過去1年分)。"""
        all_txs: List[dict] = []
        last_txid: Optional[str] = None

        while True:
            if last_txid:
                url = f"{BLOCKSTREAM_API}/address/{address}/txs/chain/{last_txid}"
            else:
                url = f"{BLOCKSTREAM_API}/address/{address}/txs"

            txs = self._get(url)
            if not txs:
                break

            found_old = False
            for tx in txs:
                block_time = tx.get("status", {}).get("block_time")
                # 未確認または1年以内のものを含める
                if block_time is None or block_time >= self.one_year_ago:
                    all_txs.append(tx)
                else:
                    found_old = True

            if found_old or len(txs) < 25:
                break

            last_txid = txs[-1]["txid"]
            time.sleep(0.5)  # レート制限対策

        return all_txs

    def _calc_values(self, tx: dict, address: str) -> Tuple[int, int]:
        """
        トランザクション内で address が送った / 受け取った satoshi を計算。
        Returns: (sent_sat, received_sat)
        """
        sent = sum(
            vin.get("prevout", {}).get("value", 0)
            for vin in tx.get("vin", [])
            if vin.get("prevout", {}).get("scriptpubkey_address") == address
        )
        received = sum(
            vout.get("value", 0)
            for vout in tx.get("vout", [])
            if vout.get("scriptpubkey_address") == address
        )
        return sent, received

    def _to_btc(self, sat: int) -> str:
        """satoshi を BTC 文字列に変換。"""
        return f"{sat / SAT_TO_BTC:.8f}".rstrip("0").rstrip(".")

    def _normalize(self, tx: dict, address: str) -> List[Dict]:
        """生 TX を共通フォーマットに変換。複数レコードを返す場合あり。"""
        status_info = tx.get("status", {})
        block_time  = status_info.get("block_time")
        confirmed   = status_info.get("confirmed", False)

        date_str = (
            datetime.fromtimestamp(block_time, tz=JST).strftime("%Y-%m-%d %H:%M:%S")
            if block_time else "UNCONFIRMED"
        )
        status_str = "SUCCESS" if confirmed else "PENDING"
        txid = tx.get("txid", "")
        fee_sat = tx.get("fee", 0) or 0

        sent, received = self._calc_values(tx, address)

        records: List[Dict] = []

        if sent > 0:
            # 送金：差し引きを記録 (お釣りを除く)
            net_sent = max(sent - received, 0)
            records.append({
                "date":         date_str,
                "network":      "bitcoin",
                "tx_hash":      txid,
                "from":         address,
                "to":           "",   # BTC は複数出力のため省略
                "value":        self._to_btc(net_sent),
                "token_symbol": "BTC",
                "gas_fee":      self._to_btc(fee_sat),
                "direction":    "OUT",
                "tx_type":      "SEND",
                "status":       status_str,
            })
        elif received > 0:
            # 純粋な受取
            records.append({
                "date":         date_str,
                "network":      "bitcoin",
                "tx_hash":      txid,
                "from":         "",   # BTC は複数入力のため省略
                "to":           address,
                "value":        self._to_btc(received),
                "token_symbol": "BTC",
                "gas_fee":      "",
                "direction":    "IN",
                "tx_type":      "RECEIVE",
                "status":       status_str,
            })

        return records

    # ──────────────────────────────────────────────────────────
    # 公開 API
    # ──────────────────────────────────────────────────────────

    def fetch(self, address: str) -> List[Dict]:
        """
        指定アドレスの過去1年分の Bitcoin 取引を取得し、
        正規化済みレコードのリストを返します。
        """
        logger.info("[bitcoin] 取引を取得中: %s", address)
        raw_txs = self._fetch_txs(address)

        records: List[Dict] = []
        for tx in raw_txs:
            records.extend(self._normalize(tx, address))

        records.sort(key=lambda r: r["date"], reverse=True)
        logger.info("[bitcoin] 合計 %d 件取得", len(records))
        return records
