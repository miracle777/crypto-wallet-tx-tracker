"""
dex_classifier.py
=================
DEX SWAP 自動判定モジュール。

constants/dex_addresses.py で定義されたルーターアドレスと
既存の METHOD_SIGNATURES を組み合わせて DEX_SWAP を判定します。

対応DEX:
  - Uniswap V2 / V3
  - PancakeSwap V2 / V3
  - TraderJoe V1 / V2
  - SushiSwap / QuickSwap / Pangolin
  - BaseSwap / Aerodrome
  - 1inch / Curve

使い方:
    from classifiers.dex_classifier import classify_as_dex_swap
    result = classify_as_dex_swap(tx)   # "DEX_SWAP" or None
"""

import logging
from typing import Optional

from constants.dex_addresses import ALL_DEX_ROUTERS

logger = logging.getLogger(__name__)

# Swap 系メソッドID (tx_classifier.py の METHOD_SIGNATURES からスワップ関連を抽出)
DEX_SWAP_METHOD_IDS: set[str] = {
    # Uniswap V2 系
    "0x38ed1739",  # swapExactTokensForTokens
    "0x7ff36ab5",  # swapExactETHForTokens
    "0x18cbafe5",  # swapExactTokensForETH
    "0xfb3bdb41",  # swapETHForExactTokens
    "0x5c11d795",  # swapExactTokensForTokensSupportingFeeOnTransferTokens
    "0xb6f9de95",  # swapExactETHForTokensSupportingFeeOnTransferTokens
    "0x791ac947",  # swapExactTokensForETHSupportingFeeOnTransferTokens
    # Uniswap V3 系
    "0x414bf389",  # exactInputSingle
    "0xc04b8d59",  # exactInput
    "0x04e45aaf",  # exactInputSingle (new)
    "0xdb3e2198",  # exactOutputSingle
    "0xf28c0498",  # exactOutput
    # Balancer
    "0x2646478b",  # swap
    "0x52bbbe29",  # queryBatchSwap
    # 0x Protocol
    "0xd9627aa4",  # sellToUniswap
    # Curve
    "0xf7fcd384",  # swapExactOut
    "0x3df02124",  # exchange
    "0xa6417ed6",  # exchange_underlying
    # 1inch
    "0x44d73b0d",  # swapExactIn
    "0xe449022e",  # uniswapV3Swap
    "0x12aa3caf",  # swap (1inch aggregator)
    "0x0502b1c5",  # unoswap
}


def classify_as_dex_swap(tx: dict) -> Optional[str]:
    """
    トランザクションが DEX スワップかどうか判定します。

    判定ロジック:
      1. to アドレスが既知DEXルーターなら DEX_SWAP
      2. input data のメソッドID がスワップシグネチャなら DEX_SWAP
      3. 該当しなければ None

    Args:
        tx: Etherscan 互換 API から取得したトランザクション辞書
            (_source, to, input, functionName キーを参照)

    Returns:
        "DEX_SWAP" または None
    """
    source    = tx.get("_source", "normal")
    to_addr   = (tx.get("to") or "").lower()
    from_addr = (tx.get("from") or "").lower()
    input_data = tx.get("input", "0x") or "0x"
    func_name  = (tx.get("functionName") or "").lower()

    # ERC-20 転送の場合: from または to が DEX ルーターなら SWAP
    if source == "tokentx":
        if from_addr in ALL_DEX_ROUTERS or to_addr in ALL_DEX_ROUTERS:
            dex_name = ALL_DEX_ROUTERS.get(from_addr) or ALL_DEX_ROUTERS.get(to_addr)
            logger.debug("DEX_SWAP (tokentx) 検出: %s", dex_name)
            return "DEX_SWAP"
        return None

    # 内部トランザクションは DEX 判定しない
    if source == "internal":
        return None

    # 通常トランザクション
    method_id = input_data[:10].lower() if len(input_data) >= 10 else "0x"

    # ルーターアドレス一致
    if to_addr in ALL_DEX_ROUTERS:
        dex_name = ALL_DEX_ROUTERS[to_addr]
        logger.debug("DEX_SWAP (router) 検出: %s", dex_name)
        return "DEX_SWAP"

    # メソッドID一致
    if method_id in DEX_SWAP_METHOD_IDS:
        logger.debug("DEX_SWAP (method_id) 検出: %s", method_id)
        return "DEX_SWAP"

    # functionName キーワード判定 (フォールバック)
    swap_keywords = ("swap", "exchange", "uniswap", "trade")
    if any(kw in func_name for kw in swap_keywords):
        logger.debug("DEX_SWAP (funcname) 検出: %s", func_name)
        return "DEX_SWAP"

    return None
