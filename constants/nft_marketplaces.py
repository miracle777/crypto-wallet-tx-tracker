"""
nft_marketplaces.py
===================
既知の NFT マーケットプレイスコントラクトアドレス定数。

対応マーケット:
  - OpenSea (Seaport / Conduit / Wyvern)
  - Blur
  - LooksRare
  - X2Y2
  - Rarible

ERC-721 / ERC-1155 メソッドシグネチャも定義します。
全アドレスは lowercase で統一しています。
"""

# ──────────────────────────────────────────────────────────────
# OpenSea
# ──────────────────────────────────────────────────────────────
OPENSEA_SEAPORT_1_1  = "0x00000000006c3852cbef3e08e8df289169ede581"
OPENSEA_SEAPORT_1_4  = "0x00000000000001ad428e4906ae43d8f9852d0dd6"
OPENSEA_SEAPORT_1_5  = "0x00000000000000adc04c56bf30ac9d3c0aaf14dc"
OPENSEA_CONDUIT      = "0x1e0049783f008a0085193e00003d00cd54003c71"
OPENSEA_WYVERN_V2    = "0x7f268357a8c2552623316e2562d90e642bb538e5"
OPENSEA_WYVERN_V2_1  = "0x7be8076f4ea4a4ad08075c2508e481d6c946d12b"

# ──────────────────────────────────────────────────────────────
# Blur
# ──────────────────────────────────────────────────────────────
BLUR_EXCHANGE       = "0x000000000000ad05ccc4f10045630fb830b95127"
BLUR_BLEND          = "0x29469395eaf6f95920e59f858042f0e28d98a20b"

# ──────────────────────────────────────────────────────────────
# LooksRare
# ──────────────────────────────────────────────────────────────
LOOKSRARE_V1 = "0x59728544b08ab483533076417fbbb2fd0b17ce3a"
LOOKSRARE_V2 = "0x0000000000e655fae4d56241588680f86e3b2377"

# ──────────────────────────────────────────────────────────────
# X2Y2
# ──────────────────────────────────────────────────────────────
X2Y2_EXCHANGE = "0x74312363e45dcaba76c59ec49a13aa114034c39b"

# ──────────────────────────────────────────────────────────────
# Rarible
# ──────────────────────────────────────────────────────────────
RARIBLE_EXCHANGE = "0x9757f2d2b135150bbeb65308d4a91804107cd8d6"

# ──────────────────────────────────────────────────────────────
# ERC-721 / ERC-1155 メソッドシグネチャ (method ID: 先頭10文字)
# ──────────────────────────────────────────────────────────────
ERC721_METHOD_IDS: set[str] = {
    "0x23b872dd",  # transferFrom(address,address,uint256)
    "0x42842e0e",  # safeTransferFrom(address,address,uint256)
    "0xb88d4fde",  # safeTransferFrom(address,address,uint256,bytes)
}

ERC1155_METHOD_IDS: set[str] = {
    "0xf242432a",  # safeTransferFrom(address,address,uint256,uint256,bytes) ERC-1155
    "0x2eb2c2d6",  # safeBatchTransferFrom ERC-1155
}

ALL_NFT_METHOD_IDS: set[str] = ERC721_METHOD_IDS | ERC1155_METHOD_IDS

# Transfer イベントシグネチャ (keccak256)
ERC721_TRANSFER_TOPIC  = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ERC1155_TRANSFER_TOPIC = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"

# ──────────────────────────────────────────────────────────────
# 全NFTマーケットプレイスセット (lowercase) - 分類に使用
# ──────────────────────────────────────────────────────────────
ALL_NFT_MARKETPLACES: dict[str, str] = {
    # OpenSea
    OPENSEA_SEAPORT_1_1: "OpenSea (Seaport 1.1)",
    OPENSEA_SEAPORT_1_4: "OpenSea (Seaport 1.4)",
    OPENSEA_SEAPORT_1_5: "OpenSea (Seaport 1.5)",
    OPENSEA_CONDUIT:     "OpenSea Conduit",
    OPENSEA_WYVERN_V2:   "OpenSea (Wyvern V2)",
    OPENSEA_WYVERN_V2_1: "OpenSea (Wyvern V2.1)",
    # Blur
    BLUR_EXCHANGE: "Blur Exchange",
    BLUR_BLEND:    "Blur Blend",
    # LooksRare
    LOOKSRARE_V1: "LooksRare V1",
    LOOKSRARE_V2: "LooksRare V2",
    # X2Y2
    X2Y2_EXCHANGE: "X2Y2",
    # Rarible
    RARIBLE_EXCHANGE: "Rarible",
}
