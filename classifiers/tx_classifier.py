"""
tx_classifier.py
================
EVM / Bitcoin トランザクションの取引タイプ分類モジュール。
メソッドIDシグネチャと既知コントラクトアドレスを使って分類します。

取引タイプ一覧:
  SEND               - 通常送金 (OUT)
  RECEIVE            - 通常受取 (IN)
  SWAP               - DEXでのスワップ (レガシー互換)
  DEX_SWAP           - DEXでのスワップ (拡張判定)
  STAKE              - ステーキング入金
  UNSTAKE            - ステーキング出金
  REWARD             - ステーキング報酬・ボーナス受取
  ADD_LIQUIDITY      - 流動性追加
  REMOVE_LIQUIDITY   - 流動性削除
  NFT_PURCHASE       - NFT購入 (マーケットプレイス経由)
  NFT_TRANSFER       - NFT直接転送
  AIRDROP            - エアドロップ受取
  SELF_TRANSFER      - 自己ウォレット間送金 (税務対象外)
  CONTRACT_INTERACTION - その他コントラクト操作 (approveなど)
  UNKNOWN            - 不明

判定処理順序:
  1. SELF_TRANSFER   - 自己ウォレット判定 (config/wallets.json)
  2. DEX_SWAP        - DEX SWAP判定 (constants/dex_addresses.py)
  3. NFT_PURCHASE /  - NFT判定 (constants/nft_marketplaces.py)
     NFT_TRANSFER
  4. 既存ロジック    - SEND / RECEIVE / SWAP / STAKE / ...
"""

# ──────────────────────────────────────────────────────────────
# メソッドIDシグネチャ辞書
# (input dataの先頭10文字: "0x" + 4バイト hex)
# ──────────────────────────────────────────────────────────────
METHOD_SIGNATURES: dict[str, str] = {
    # ── Swap ──────────────────────────────────────────────────
    "0x38ed1739": "SWAP",   # swapExactTokensForTokens (Uniswap V2)
    "0x7ff36ab5": "SWAP",   # swapExactETHForTokens (Uniswap V2)
    "0x18cbafe5": "SWAP",   # swapExactTokensForETH (Uniswap V2)
    "0xfb3bdb41": "SWAP",   # swapETHForExactTokens (Uniswap V2)
    "0x5c11d795": "SWAP",   # swapExactTokensForTokensSupportingFeeOnTransferTokens
    "0xb6f9de95": "SWAP",   # swapExactETHForTokensSupportingFeeOnTransferTokens
    "0x791ac947": "SWAP",   # swapExactTokensForETHSupportingFeeOnTransferTokens
    "0x414bf389": "SWAP",   # exactInputSingle (Uniswap V3)
    "0xc04b8d59": "SWAP",   # exactInput (Uniswap V3)
    "0x04e45aaf": "SWAP",   # exactInputSingle V3 (new)
    "0xdb3e2198": "SWAP",   # exactOutputSingle (Uniswap V3)
    "0xf28c0498": "SWAP",   # exactOutput (Uniswap V3)
    "0x2646478b": "SWAP",   # swap (Balancer)
    "0x52bbbe29": "SWAP",   # queryBatchSwap (Balancer)
    "0xd9627aa4": "SWAP",   # sellToUniswap (0x Protocol)
    "0xf7fcd384": "SWAP",   # swapExactOut (Curve)
    "0x3df02124": "SWAP",   # exchange (Curve)
    "0xa6417ed6": "SWAP",   # exchange_underlying (Curve)
    "0x44d73b0d": "SWAP",   # swapExactIn (1inch v3)
    "0xe449022e": "SWAP",   # uniswapV3Swap (1inch)
    "0x12aa3caf": "SWAP",   # swap (1inch aggregator)
    "0x0502b1c5": "SWAP",   # unoswap (1inch)

    # ── Staking ───────────────────────────────────────────────
    "0xa694fc3a": "STAKE",       # stake(uint256)
    "0xb6b55f25": "STAKE",       # deposit(uint256)  ※LP staking
    "0x1249c58b": "STAKE",       # mint() ※一部ステーキング
    "0x47e7ef24": "STAKE",       # deposit(address, uint256)
    "0x9ebea88c": "STAKE",       # stakeWithPermit
    "0x2e1a7d4d": "UNSTAKE",     # withdraw(uint256)
    "0xe9fad8ee": "UNSTAKE",     # exit()
    "0x38d07436": "UNSTAKE",     # unstake(uint256)
    "0x441a3e70": "UNSTAKE",     # withdraw(uint256,uint256) ※MasterChef
    "0xbec7e006": "UNSTAKE",     # withdrawAndHarvest
    "0x3d18b912": "REWARD",      # getReward()
    "0x372500ab": "REWARD",      # claimRewards()
    "0x4e71d92d": "REWARD",      # claim()
    "0xab9c4b5d": "REWARD",      # harvest(uint256,address)  ※MasterChef
    "0xddc63262": "REWARD",      # harvestAll()
    "0x5f575529": "REWARD",      # claimYield()

    # ── Liquidity ─────────────────────────────────────────────
    "0xe8e33700": "ADD_LIQUIDITY",      # addLiquidity (Uniswap V2)
    "0xf305d719": "ADD_LIQUIDITY",      # addLiquidityETH (Uniswap V2)
    "0x4515cef3": "ADD_LIQUIDITY",      # add_liquidity (Curve)
    "0x0b4c7e4d": "ADD_LIQUIDITY",      # add_liquidity[2 coins] (Curve)
    "0x1a7a98e2": "ADD_LIQUIDITY",      # add_liquidity (Balancer)
    "0xbaa2abde": "REMOVE_LIQUIDITY",   # removeLiquidity (Uniswap V2)
    "0x02751cec": "REMOVE_LIQUIDITY",   # removeLiquidityETH (Uniswap V2)
    "0x5b36389c": "REMOVE_LIQUIDITY",   # remove_liquidity (Curve)
    "0x1a4d01d2": "REMOVE_LIQUIDITY",   # remove_liquidity_one_coin (Curve)
    "0x8f94b822": "REMOVE_LIQUIDITY",   # exitPool (Balancer)

    # ── NFT ───────────────────────────────────────────────────
    "0x23b872dd": "NFT_PURCHASE",   # transferFrom (ERC-721)
    "0x42842e0e": "NFT_PURCHASE",   # safeTransferFrom (ERC-721)
    "0xb88d4fde": "NFT_PURCHASE",   # safeTransferFrom+data (ERC-721)

    # ── Contract Interaction (承認など) ──────────────────────
    "0x095ea7b3": "CONTRACT_INTERACTION",  # approve (ERC-20)
    "0xd505accf": "CONTRACT_INTERACTION",  # permit (EIP-2612)
    "0xa22cb465": "CONTRACT_INTERACTION",  # setApprovalForAll (ERC-721)
}

# ──────────────────────────────────────────────────────────────
# 既知のスワップルーター/アグリゲーターアドレス (lowercase)
# ──────────────────────────────────────────────────────────────
KNOWN_SWAP_CONTRACTS: dict[str, str] = {
    # Uniswap
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2 Router",
    "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap V3 Router",
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "Uniswap V3 Router2",
    "0x000000000022d473030f116ddee9f6b43ac78ba3": "Uniswap Permit2",
    # 1inch
    "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch V5",
    "0x1111111254fb6c44bac0bed2854e76f90643097d": "1inch V4",
    "0x11111112542d85b3ef69ae05771c2dccff4faa26": "1inch V3",
    # SushiSwap
    "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f": "SushiSwap Router",
    # Curve
    "0x99a58482bd75cbab83b27ec03ca68ff489b5788f": "Curve Router",
    # Polygon specific
    "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff": "QuickSwap Router",
    "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506": "SushiSwap (Polygon)",
    # Avalanche specific
    "0x60ae616a2155ee3d9a68541ba4544862310933d4": "TraderJoe Router",
    "0xe54ca86531e17ef3616d22ca28b0d458b6c89106": "Pangolin Router",
    "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch V5 (AVAX)",
    # Base specific
    "0x327df1e6de05895d2ab08513aadd9313fe3d26d8": "BaseSwap Router",
    "0x8c1a3cf8f83074169fe5d7ad50b978e1cdda1ebb": "Aerodrome Router",
}

# ──────────────────────────────────────────────────────────────
# 既知のステーキング/レンディングプロトコルアドレス (lowercase)
# ──────────────────────────────────────────────────────────────
KNOWN_STAKING_CONTRACTS: dict[str, str] = {
    # Lido
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": "Lido stETH",
    "0x889edc2edab5f40e902b864ad4d7ade8e412f9b1": "Lido Withdrawal Queue",
    # Aave V3
    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": "Aave V3 Pool (ETH)",
    "0x794a61358d6845594f94dc1db02a252b5b4814ad": "Aave V3 Pool (Polygon/AVAX)",
    "0xe50fa9b3c56ffb159cb0fca61f5c855d866d523b": "Aave V3 Pool (Avalanche)",
    # Compound V3
    "0xc3d688b66703497daa19211eedff47f25384cdc3": "Compound V3 USDC",
    "0xa17581a9e3356d9a858b789d68b4d866e593ae94": "Compound V3 WETH",
    # Rocket Pool
    "0xdd3f50f8a6cafbe9b31a427582963f465e745af8": "Rocket Pool",
    # Synthetix
    "0xfeb06d3e6e647679fb44bae4d33a5da2a2ec5c83": "Synthetix Staking",
    # Yearn
    "0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e": "Yearn YFI Vault",
    # Curve Gauges (some)
    "0x72e158d38dbd50a483501c24f792bdaaa3e7d55c": "Curve Gauge",
}

# ──────────────────────────────────────────────────────────────
# 既知のエアドロップ配布コントラクトアドレス (lowercase)
# ──────────────────────────────────────────────────────────────
KNOWN_AIRDROP_CONTRACTS: dict[str, str] = {
    "0x090d4613473dee047c3f2706764f49e0821d256e": "Uniswap Airdrop",
    "0x04f0fd3cd7f354b6f6672e8f407bb0e2b31e7423": "ENS Airdrop",
}


# 新サブモジュールをインポート (循環インポート回避のためここで)
from classifiers.wallet_classifier import get_wallet_classifier
from classifiers.dex_classifier import classify_as_dex_swap
from classifiers.nft_classifier import classify_as_nft


def classify_evm_tx(tx: dict, address: str, network: str) -> str:
    """
    EVM トランザクションの取引タイプを分類します。

    Args:
        tx:      Etherscan 互換 API から取得したトランザクション辞書
                 (_source キーで 'normal' / 'tokentx' / 'internal' を識別)
        address: 分析対象のウォレットアドレス
        network: ネットワーク名 (base / polygon / avalanche)

    Returns:
        取引タイプ文字列
    """
    addr       = address.lower()
    to_addr    = (tx.get("to") or "").lower()
    from_addr  = (tx.get("from") or "").lower()
    input_data = tx.get("input", "0x") or "0x"
    func_name  = (tx.get("functionName") or "").lower()
    source     = tx.get("_source", "normal")

    method_id = input_data[:10].lower() if len(input_data) >= 10 else "0x"

    # ── [1] 自己ウォレット判定 (SELF_TRANSFER) ─────────────────
    # config/wallets.json が設定されていれば、自己送金を最優先で判定
    wc = get_wallet_classifier()
    if wc.is_self_transfer(from_addr, to_addr):
        return "SELF_TRANSFER"

    # ── [2] DEX SWAP 判定 ──────────────────────────────────────
    dex_result = classify_as_dex_swap(tx)
    if dex_result:
        return dex_result

    # ── [3] NFT 判定 ───────────────────────────────────────────
    nft_result = classify_as_nft(tx)
    if nft_result:
        return nft_result

    # ── [4] 既存ロジック ──────────────────────────────────────
    # ── ERC-20 トークン転送 (tokentx) ─────────────────────────
    if source == "tokentx":
        contract_addr = tx.get("contractAddress", "").lower()
        if to_addr == addr:
            if from_addr in KNOWN_STAKING_CONTRACTS or contract_addr in KNOWN_STAKING_CONTRACTS:
                return "REWARD"
            if from_addr in KNOWN_AIRDROP_CONTRACTS:
                return "AIRDROP"
            if from_addr in KNOWN_SWAP_CONTRACTS or contract_addr in KNOWN_SWAP_CONTRACTS:
                return "SWAP"
            return "RECEIVE"
        elif from_addr == addr:
            if to_addr in KNOWN_SWAP_CONTRACTS:
                return "SWAP"
            return "SEND"
        return "CONTRACT_INTERACTION"

    # ── 内部トランザクション (internal) ────────────────────────
    if source == "internal":
        if to_addr == addr:
            if from_addr in KNOWN_STAKING_CONTRACTS:
                return "REWARD"
            return "RECEIVE"
        return "CONTRACT_INTERACTION"

    # ── 通常トランザクション (normal) ─────────────────────────
    if from_addr == addr:
        # 自分が送信者
        if method_id in METHOD_SIGNATURES:
            return METHOD_SIGNATURES[method_id]
        if to_addr in KNOWN_SWAP_CONTRACTS:
            return "SWAP"
        if to_addr in KNOWN_STAKING_CONTRACTS:
            if any(k in func_name for k in ("stake", "deposit", "supply", "lock")):
                return "STAKE"
            if any(k in func_name for k in ("withdraw", "unstake", "exit", "unlock")):
                return "UNSTAKE"
            if any(k in func_name for k in ("claim", "reward", "harvest", "collect")):
                return "REWARD"
        if not input_data or input_data == "0x":
            return "SEND"
        if to_addr:
            return "CONTRACT_INTERACTION"
        return "SEND"

    elif to_addr == addr:
        # 自分が受信者
        return "RECEIVE"

    return "UNKNOWN"


def classify_bitcoin_tx(tx: dict, address: str) -> str:
    """
    Bitcoin トランザクションの取引タイプを分類します。
    Bitcoin は UTXO モデルのため SEND / RECEIVE のみです。

    Args:
        tx:      Blockstream API からのトランザクション辞書
        address: 分析対象の Bitcoin アドレス

    Returns:
        "SEND" または "RECEIVE"
    """
    # inputs に自分のアドレスがあれば SEND
    for vin in tx.get("vin", []):
        if vin.get("prevout", {}).get("scriptpubkey_address") == address:
            return "SEND"
    # outputs に自分のアドレスがあれば RECEIVE
    for vout in tx.get("vout", []):
        if vout.get("scriptpubkey_address") == address:
            return "RECEIVE"
    return "UNKNOWN"
