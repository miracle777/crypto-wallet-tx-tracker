"""
csv_exporter.py
===============
取引レコードを CSV ファイルへエクスポートするモジュール。
Excel で開く際の文字化けを防ぐため UTF-8 BOM 付きで出力します。
"""

import csv
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

# CSV の列定義 (順序を保つ)
FIELDNAMES = [
    "date",
    "network",
    "tx_hash",
    "from",
    "to",
    "value",
    "token_symbol",
    "gas_fee",
    "direction",
    "tx_type",
    "status",
]

JST = timezone(timedelta(hours=9))


def export_to_csv(records: List[Dict], output_dir: str = "output") -> str:
    """
    取引レコードを CSV ファイルとして出力します。

    Args:
        records:    正規化済み取引レコードのリスト
        output_dir: 出力ディレクトリ (存在しない場合は自動作成)

    Returns:
        作成した CSV ファイルのパス文字列
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    now = datetime.now(tz=JST)
    filename = f"transactions_{now.strftime('%Y-%m-%d_%H%M%S')}.csv"
    filepath = os.path.join(output_dir, filename)

    # utf-8-sig = UTF-8 BOM 付き (Excel で直接開ける)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    logger.info("CSV エクスポート完了: %s (%d 件)", filepath, len(records))
    return filepath
