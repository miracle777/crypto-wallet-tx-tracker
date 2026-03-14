"""
exporters/cryptolink_exporter.py
================================
クリプトリンク (CryptoLink) 汎用フォーマット CSV エクスポーター

cl_exchange_format.xlsx の仕様に基づいて出力します。

列構成:
  No, 取引年, 取引日, 取引時間, 取引所, 国外取引, 取引種別,
  取引通貨, 決済通貨, 取引通貨対JPYレート, 決済通貨対JPYレート,
  決済代金, 取引量, 手数料通貨, 手数料, 備考
"""

import csv
import logging
import os
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# 定数
# ──────────────────────────────────────────────────────────────

JST = timezone(timedelta(hours=9))

OUTPUT_DIR = "output"

HEADERS = [
    "No", "取引年", "取引日", "取引時間", "取引所", "国外取引",
    "取引種別", "取引通貨", "決済通貨",
    "取引通貨対JPYレート", "決済通貨対JPYレート",
    "決済代金", "取引量", "手数料通貨", "手数料", "備考",
]

# wallet_tracker の tx_type → クリプトリンク取引種別
TX_TYPE_MAP: dict = {
    "SEND":                 "送付",
    "RECEIVE":              "預入",
    "DEX_SWAP":             "売却",
    "SWAP":                 "売却",
    "STAKE":                "送付",
    "UNSTAKE":              "預入",
    "REWARD":               "ボーナス",
    "ADD_LIQUIDITY":        "送付",
    "REMOVE_LIQUIDITY":     "預入",
    "NFT_PURCHASE":         "購入",
    "NFT_TRANSFER":         "送付",   # direction=IN のとき 預入 に補正
    "AIRDROP":              "預入",
    "SELF_TRANSFER":        "送付",
    "CONTRACT_INTERACTION": "送付",
    "UNKNOWN":              "送付",
}

# direction=IN のとき取引種別を 預入 に補正するタイプ
_RECEIVE_OVERRIDE = {
    "NFT_TRANSFER",
    "CONTRACT_INTERACTION",
    "UNKNOWN",
}

# 国外取引扱いにするネットワーク名（小文字）
FOREIGN_NETWORKS = {"bitcoin", "avalanche", "base", "polygon"}


# ──────────────────────────────────────────────────────────────
# ヘルパー
# ──────────────────────────────────────────────────────────────

def _map_tx_type(tx_type, direction):
    kind = TX_TYPE_MAP.get(tx_type.upper(), "送付")
    if direction.upper() == "IN" and tx_type.upper() in _RECEIVE_OVERRIDE:
        kind = "預入"
    return kind


def _parse_jst(date_val):
    """date フィールド（文字列 or datetime）を JST の datetime に変換する。"""
    if isinstance(date_val, datetime):
        dt = date_val
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=JST)
        return dt.astimezone(JST)

    date_str = str(date_val).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=JST)
            return dt.astimezone(JST)
        except ValueError:
            continue
    return None


# ──────────────────────────────────────────────────────────────
# メイン関数
# ──────────────────────────────────────────────────────────────

def export_to_cryptolink(transactions):
    """
    wallet_tracker.py が生成した取引レコードのリストを受け取り、
    クリプトリンク汎用フォーマットの CSV を output/ に出力する。

    Parameters
    ----------
    transactions : list[dict]
        各辞書に含まれるキー（最低限）:
        date, network, tx_hash, from, to, value,
        token_symbol, gas_fee, direction, tx_type, status

    Returns
    -------
    str
        出力した CSV ファイルのパス
    """
    timestamp = datetime.now(JST).strftime("%Y-%m-%d_%H%M%S")
    filename = f"cryptolink_{timestamp}.csv"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, filename)

    rows = []
    skipped = 0

    for tx in transactions:
        # FAILED / PENDING は除外
        status = str(tx.get("status", "SUCCESS")).upper()
        if status not in ("SUCCESS", ""):
            skipped += 1
            continue

        dt = _parse_jst(tx.get("date", ""))
        if dt:
            year    = str(dt.year)
            tx_date = f"{dt.month}/{dt.day}"
            tx_time = dt.strftime("%H:%M:%S")
        else:
            year = tx_date = tx_time = ""

        network   = str(tx.get("network", ""))
        tx_type   = str(tx.get("tx_type", "UNKNOWN"))
        direction = str(tx.get("direction", "OUT"))
        symbol    = str(tx.get("token_symbol", ""))
        value     = tx.get("value", "")
        gas_fee   = tx.get("gas_fee", "")

        is_foreign = "◯" if network.lower() in FOREIGN_NETWORKS else ""
        kind       = _map_tx_type(tx_type, direction)

        rows.append({
            "No":                   len(rows) + 1,
            "取引年":               year,
            "取引日":               tx_date,
            "取引時間":             tx_time,
            "取引所":               network,
            "国外取引":             is_foreign,
            "取引種別":             kind,
            "取引通貨":             symbol,
            "決済通貨":             "",   # レート情報なし → クリプトリンク側で自動取得
            "取引通貨対JPYレート":  "",   # 同上
            "決済通貨対JPYレート":  "",   # 同上
            "決済代金":             "",   # 同上
            "取引量":               value,
            "手数料通貨":           symbol if gas_fee else "",
            "手数料":               gas_fee if gas_fee else "",
            "備考":                 str(tx.get("tx_hash", "")),
        })

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(
        "クリプトリンク CSV 出力完了: %s (%d 件, %d 件スキップ)",
        output_path, len(rows), skipped,
    )
    return output_path
