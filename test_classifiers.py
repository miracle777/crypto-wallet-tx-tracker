"""分類ロジック動作確認スクリプト"""
import json
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from classifiers.dex_classifier import classify_as_dex_swap
from classifiers.nft_classifier import classify_as_nft
from classifiers.wallet_classifier import WalletClassifier

results = []

# ── DEX SWAP テスト ──────────────────────────────────────────
with open("examples/swap_example.json", encoding="utf-8") as f:
    tx = json.load(f)
result = classify_as_dex_swap(tx)
ok = result == "DEX_SWAP"
results.append(ok)
print(f"[DEX SWAP]   期待: DEX_SWAP    結果: {result}  -> {'OK' if ok else 'NG'}")

# ── NFT テスト ───────────────────────────────────────────────
with open("examples/nft_example.json", encoding="utf-8") as f:
    tx = json.load(f)
result = classify_as_nft(tx)
ok = result == "NFT_PURCHASE"
results.append(ok)
print(f"[NFT]        期待: NFT_PURCHASE 結果: {result}  -> {'OK' if ok else 'NG'}")

# ── 自己送金テスト ────────────────────────────────────────────
tmp_path = Path("examples") / "_temp_wallets.json"
try:
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({
            "addresses": [
                "0xabc1234567890abcdef1234567890abcdef123456",
                "0xdef1234567890abcdef1234567890abcdef123456",
            ]
        }, f)
    wc = WalletClassifier(tmp_path)
    with open("examples/self_transfer_example.json", encoding="utf-8") as f:
        tx = json.load(f)
    result = wc.is_self_transfer(tx["from"], tx["to"])
    ok = result is True
    results.append(ok)
    print(f"[SELF]       期待: True         結果: {result}  -> {'OK' if ok else 'NG'}")
finally:
    if tmp_path.exists():
        tmp_path.unlink()

# ── 結果サマリー ──────────────────────────────────────────────
print()
passed = sum(results)
total = len(results)
print(f"テスト結果: {passed}/{total} 件 PASS")
sys.exit(0 if all(results) else 1)
