"""
dex_addresses.py
================
既知の DEX ルーター / アグリゲーターコントラクトアドレス定数。

対応DEX:
  - Uniswap V2 / V3
  - PancakeSwap V2 / V3
  - TraderJoe V1 / V2
  - SushiSwap
  - QuickSwap (Polygon)
  - Pangolin (Avalanche)
  - BaseSwap / Aerodrome (Base)
  - 1inch (マルチチェーン)
  - Curve
  - Balancer
  - 0x Protocol

全アドレスは lowercase で統一しています。
"""

# ──────────────────────────────────────────────────────────────
# Uniswap
# ──────────────────────────────────────────────────────────────
UNISWAP_V2_ROUTER   = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
UNISWAP_V3_ROUTER   = "0xe592427a0aece92de3edee1f18e0157c05861564"
UNISWAP_V3_ROUTER2  = "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45"
UNISWAP_PERMIT2     = "0x000000000022d473030f116ddee9f6b43ac78ba3"

# ──────────────────────────────────────────────────────────────
# PancakeSwap (BSC / Polygon / Base)
# ──────────────────────────────────────────────────────────────
PANCAKESWAP_V2_ROUTER = "0x10ed43c718714eb63d5aa57b78b54704e256024e"  # BSC
PANCAKESWAP_V3_ROUTER = "0x13f4ea83d0bd40e75c8222255bc855a974568dd4"  # BSC V3
PANCAKESWAP_POLYGON   = "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"  # Polygon (SushiSwap互換)

# ──────────────────────────────────────────────────────────────
# TraderJoe (Avalanche / Arbitrum)
# ──────────────────────────────────────────────────────────────
TRADERJOE_V1_ROUTER = "0x60ae616a2155ee3d9a68541ba4544862310933d4"  # Avalanche V1
TRADERJOE_V2_ROUTER = "0xb4315e873dBcf96Ffd0acd8EA43f689D8c20fB30".lower()  # Avalanche V2

# ──────────────────────────────────────────────────────────────
# SushiSwap (マルチチェーン共通)
# ──────────────────────────────────────────────────────────────
SUSHISWAP_ROUTER         = "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f"  # Ethereum
SUSHISWAP_POLYGON_ROUTER = "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"  # Polygon

# ──────────────────────────────────────────────────────────────
# QuickSwap (Polygon)
# ──────────────────────────────────────────────────────────────
QUICKSWAP_ROUTER = "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff"

# ──────────────────────────────────────────────────────────────
# Pangolin (Avalanche)
# ──────────────────────────────────────────────────────────────
PANGOLIN_ROUTER = "0xe54ca86531e17ef3616d22ca28b0d458b6c89106"

# ──────────────────────────────────────────────────────────────
# Base チェーン
# ──────────────────────────────────────────────────────────────
BASESWAP_ROUTER  = "0x327df1e6de05895d2ab08513aadd9313fe3d26d8"
AERODROME_ROUTER = "0x8c1a3cf8f83074169fe5d7ad50b978e1cdda1ebb"

# ──────────────────────────────────────────────────────────────
# 1inch (マルチチェーン)
# ──────────────────────────────────────────────────────────────
ONEINCH_V3 = "0x11111112542d85b3ef69ae05771c2dccff4faa26"
ONEINCH_V4 = "0x1111111254fb6c44bac0bed2854e76f90643097d"
ONEINCH_V5 = "0x1111111254eeb25477b68fb85ed929f73a960582"

# ──────────────────────────────────────────────────────────────
# Curve
# ──────────────────────────────────────────────────────────────
CURVE_ROUTER = "0x99a58482bd75cbab83b27ec03ca68ff489b5788f"

# ──────────────────────────────────────────────────────────────
# 全DEXルーターアドレスセット (lower case) - 分類に使用
# ──────────────────────────────────────────────────────────────
ALL_DEX_ROUTERS: dict[str, str] = {
    # Uniswap
    UNISWAP_V2_ROUTER:   "Uniswap V2",
    UNISWAP_V3_ROUTER:   "Uniswap V3",
    UNISWAP_V3_ROUTER2:  "Uniswap V3 Router2",
    UNISWAP_PERMIT2:     "Uniswap Permit2",
    # PancakeSwap
    PANCAKESWAP_V2_ROUTER: "PancakeSwap V2",
    PANCAKESWAP_V3_ROUTER: "PancakeSwap V3",
    PANCAKESWAP_POLYGON:   "PancakeSwap (Polygon)",
    # TraderJoe
    TRADERJOE_V1_ROUTER: "TraderJoe V1",
    TRADERJOE_V2_ROUTER: "TraderJoe V2",
    # SushiSwap
    SUSHISWAP_ROUTER:         "SushiSwap",
    SUSHISWAP_POLYGON_ROUTER: "SushiSwap (Polygon)",
    # QuickSwap
    QUICKSWAP_ROUTER: "QuickSwap",
    # Pangolin
    PANGOLIN_ROUTER: "Pangolin",
    # Base
    BASESWAP_ROUTER:  "BaseSwap",
    AERODROME_ROUTER: "Aerodrome",
    # 1inch
    ONEINCH_V3: "1inch V3",
    ONEINCH_V4: "1inch V4",
    ONEINCH_V5: "1inch V5",
    # Curve
    CURVE_ROUTER: "Curve Router",
}
