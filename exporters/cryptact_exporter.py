"""
cryptact_exporter.py
====================
Cryptact (クリプタクト) 形式の CSV ファイルを出力するモジュール。

Cryptact フォーマット仕様:
  https://support.cryptact.com/hc/ja/articles/360002571312

出力列:
  Timestamp  - 取引日時 (JST, "YYYY/MM/DD HH:MM:SS" 形式)
  Action     - 取引アクション (TRADE / SEND / RECEIVE / etc.)
  Source     - 取引所・サービス名 (例: "ethereum", "polygon")
  Base       - 基軸通貨 (例: ETH, POL, AVAX, BTC)
  Volume     - 取引量
  Price      - 取引価格 (不明な場合は空欄)
  Counter    - 対価通貨 (不明な場合は空欄)
  Fee        - ガス手数料
  FeeCcy     - 手数料通貨 (例: ETH)
  Note       - 備考 (tx_hash など)

tx_type → Action マッピング:
  SELF_TRANSFER       → TRANSFER
  DEX_SWAP / SWAP     → TRADE
  NFT_PURCHASE        → BUY
  NFT_TRANSFER        → SEND (※自己発信時) / RECEIVE (※受取時)
  STAKE               → SEND (預け入れ)
  UNSTAKE             → RECEIVE (引き出し)
  REWARD / AIRDROP    → RECEIVE
  SEND                → SEND
  RECEIVE             → RECEIVE
  ADD_LIQUIDITY       → SEND
  REMOVE_LIQUIDITY    → RECEIVE
  CONTRACT_INTERACTION→ OTHERS
  UNKNOWN             → OTHERS
"""

import csv
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

JST = timezone(timedelta(hours=9))

# Cryptact CSV 列定義
CRYPTACT_FIELDNAMES = [
    "Timestamp",
    "Action",
    "Source",
    "Base",
    "Volume",
    "Price",
    "Counter",
    "Fee",
    "FeeCcy",
    "Note",
]

# tx_type → Cryptact Action マッピング
TX_TYPE_TO_ACTION: dict[str, str] = {
    "SELF_TRANSFER":      "TRANSFER",
    "DEX_SWAP":           "TRADE",
    "SWAP":               "TRADE",
    "NFT_PURCHASE":       "BUY",
    "NFT_TRANSFER":       "SEND",
    "STAKE":              "SEND",
    "UNSTAKE":            "RECEIVE",
    "REWARD":             "RECEIVE",
    "AIRDROP":            "RECEIVE",
    "SEND":               "SEND",
    "RECEIVE":            "RECEIVE",
    "ADD_LIQUIDITY":      "SEND",
    "REMOVE_LIQUIDITY":   "RECEIVE",
    "CONTRACT_INTERACTION": "OTHERS",
    "UNKNOWN":            "OTHERS",
}

# ネットワーク → ネイティブトークンシンボル
NETWORK_TO_TOKEN: dict[str, str] = {
    "base":      "ETH",
    "polygon":   "POL",
    "avalanche": "AVAX",
    "bitcoin":   "BTC",
    "ethereum":  "ETH",
}


def _to_cryptact_action(tx_type: str, direction: str) -> str:
    """
    tx_type と direction から Cryptact の Action を決定します。
    NFT_TRANSFER は direction で SEND/RECEIVE を切り替えます。
    """
    if tx_type == "NFT_TRANSFER":
        return "SEND" if direction == "OUT" else "RECEIVE"
    return TX_TYPE_TO_ACTION.get(tx_type, "OTHERS")


def _to_cryptact_timestamp(date_str: str) -> str:
    """
    "YYYY-MM-DD HH:MM:SS" → "YYYY/MM/DD HH:MM:SS" に変換。
    """
    return date_str.replace("-", "/")


def _to_cryptact_record(record: dict) -> dict:
    """
    通常レコードを Cryptact 形式のレコードに変換します。

    SELF_TRANSFER / OTHERS 等は税務上意味のない取引のため
    Note に補足情報を記録します。
    """
    tx_type   = record.get("tx_type", "UNKNOWN")
    direction = record.get("direction", "OUT")
    network   = record.get("network", "").lower()
    token     = record.get("token_symbol", "")
    value     = record.get("value", "0")
    gas_fee   = record.get("gas_fee", "")
    tx_hash   = record.get("tx_hash", "")
    date_str  = record.get("date", "")

    action      = _to_cryptact_action(tx_type, direction)
    timestamp   = _to_cryptact_timestamp(date_str)
    source      = network if network else "unknown"
    native_ccy  = NETWORK_TO_TOKEN.get(network, token or "UNKNOWN")

    # Bitcoin は tx_type も direction も異なるためそのまま使用
    fee_ccy = native_ccy

    return {
        "Timestamp": timestamp,
        "Action":    action,
        "Source":    source,
        "Base":      token if token else native_ccy,
        "Volume":    value,
        "Price":     "",         # 価格情報なし (Cryptact で自動取得)
        "Counter":   "",         # 対価通貨不明
        "Fee":       gas_fee if gas_fee else "",
        "FeeCcy":    fee_ccy if gas_fee else "",
        "Note":      f"{tx_type} | {tx_hash[:20]}..." if tx_hash else tx_type,
    }


def export_to_cryptact(records: List[Dict], output_dir: str = "output") -> str:
    """
    取引レコードを Cryptact 形式の CSV ファイルとして出力します。

    SELF_TRANSFER でも出力します (import 時に TRANSFER として扱われる)。
    Status が FAILED のレコードは除外します。

    Args:
        records:    正規化済み取引レコードのリスト
        output_dir: 出力ディレクトリ (存在しない場合は自動作成)

    Returns:
        作成した CSV ファイルのパス文字列
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    now = datetime.now(tz=JST)
    filename = f"cryptact_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"
    filepath = os.path.join(output_dir, filename)

    # FAILED 取引を除外
    valid_records = [r for r in records if r.get("status", "SUCCESS") != "FAILED"]

    cryptact_rows = [_to_cryptact_record(r) for r in valid_records]

    # utf-8-sig = UTF-8 BOM 付き (Excel で直接開ける)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CRYPTACT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cryptact_rows)

    logger.info(
        "Cryptact CSV エクスポート完了: %s (%d 件 / FAILED 除外: %d 件)",
        filepath, len(cryptact_rows), len(records) - len(valid_records),
    )
    return filepath
