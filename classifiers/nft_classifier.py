"""
nft_classifier.py
=================
NFT 取引判定モジュール。

ERC-721 / ERC-1155 のメソッドシグネチャと
既知 NFT マーケットプレイスアドレスを組み合わせて
NFT_PURCHASE / NFT_TRANSFER を判定します。

対応マーケット:
  - OpenSea (Seaport V1.1 / V1.4 / V1.5, Wyvern, Conduit)
  - Blur / Blur Blend
  - LooksRare V1 / V2
  - X2Y2
  - Rarible

使い方:
    from classifiers.nft_classifier import classify_as_nft
    result = classify_as_nft(tx)   # "NFT_PURCHASE" / "NFT_TRANSFER" / None
"""

import logging
from typing import Optional

from constants.nft_marketplaces import (
    ALL_NFT_MARKETPLACES,
    ALL_NFT_METHOD_IDS,
    ERC721_METHOD_IDS,
    ERC1155_METHOD_IDS,
)

logger = logging.getLogger(__name__)


def classify_as_nft(tx: dict) -> Optional[str]:
    """
    トランザクションが NFT 取引かどうか判定します。

    判定ロジック:
      1. to アドレスが既知 NFT マーケットプレイスなら NFT_PURCHASE
      2. input data のメソッドID が ERC-721/1155 転送なら:
         - from または to が既知マーケットプレイス → NFT_PURCHASE
         - それ以外 → NFT_TRANSFER
      3. tokenSymbol ヒューリスティック (nft_type フィールド参照)
      4. 該当しなければ None

    Args:
        tx: Etherscan 互換 API から取得したトランザクション辞書

    Returns:
        "NFT_PURCHASE" / "NFT_TRANSFER" / None
    """
    source     = tx.get("_source", "normal")
    to_addr    = (tx.get("to") or "").lower()
    from_addr  = (tx.get("from") or "").lower()
    input_data = tx.get("input", "0x") or "0x"
    func_name  = (tx.get("functionName") or "").lower()

    method_id = input_data[:10].lower() if len(input_data) >= 10 else "0x"

    # ── ERC-721/1155 トークン転送 (nfttx) ─────────────────────
    # Etherscan で action=tokennfttx として取得される場合
    if source == "nfttx":
        if from_addr in ALL_NFT_MARKETPLACES or to_addr in ALL_NFT_MARKETPLACES:
            market = ALL_NFT_MARKETPLACES.get(from_addr) or ALL_NFT_MARKETPLACES.get(to_addr)
            logger.debug("NFT_PURCHASE (nfttx+marketplace) 検出: %s", market)
            return "NFT_PURCHASE"
        logger.debug("NFT_TRANSFER (nfttx) 検出")
        return "NFT_TRANSFER"

    # ── 内部トランザクションは NFT 判定しない ─────────────────
    if source == "internal":
        return None

    # ── 通常トランザクション ─────────────────────────────────
    # to アドレスが NFT マーケットプレイス
    if to_addr in ALL_NFT_MARKETPLACES:
        market = ALL_NFT_MARKETPLACES[to_addr]
        logger.debug("NFT_PURCHASE (marketplace) 検出: %s", market)
        return "NFT_PURCHASE"

    # ERC-721/1155 メソッドID
    if method_id in ALL_NFT_METHOD_IDS:
        # マーケットプレイス経由かどうかで NFT_PURCHASE / NFT_TRANSFER を区別
        if from_addr in ALL_NFT_MARKETPLACES or to_addr in ALL_NFT_MARKETPLACES:
            return "NFT_PURCHASE"
        return "NFT_TRANSFER"

    # functionName キーワード判定 (フォールバック)
    nft_keywords = ("transferfrom", "safetransferfrom", "mintto", "safemint", "fulfillbasicorder")
    if any(kw in func_name for kw in nft_keywords):
        if from_addr in ALL_NFT_MARKETPLACES or to_addr in ALL_NFT_MARKETPLACES:
            return "NFT_PURCHASE"
        return "NFT_TRANSFER"

    # ── ERC-20 転送 (tokentx) ─────────────────────────────────
    # tokenID フィールドがある = ERC-721 トークン転送
    if source == "tokentx":
        token_id = tx.get("tokenID") or tx.get("tokenId")
        if token_id is not None:
            if from_addr in ALL_NFT_MARKETPLACES or to_addr in ALL_NFT_MARKETPLACES:
                return "NFT_PURCHASE"
            return "NFT_TRANSFER"

    return None
