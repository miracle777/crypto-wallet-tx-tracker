"""
wallet_tracker.py
=================
クリプト取引履歴トラッカー - メインエントリーポイント

対応ネットワーク:
  Base       - Basescan API (要APIキー)
  Polygon    - Polygonscan API (要APIキー)
  Avalanche  - Routescan API (要APIキー)
  Bitcoin    - Blockstream.info API (APIキー不要)

使い方:
  python wallet_tracker.py               # 対話形式で実行
  python wallet_tracker.py --dry-run     # サンプルアドレスでテスト実行
  python wallet_tracker.py --help        # ヘルプ表示
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from exporters.csv_exporter import export_to_csv
from exporters.cryptact_exporter import export_to_cryptact

# ──────────────────────────────────────────────────────────────
# ロギング設定
# ──────────────────────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/wallet_tracker.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# ドライラン用サンプルアドレス (公開アドレス)
# ──────────────────────────────────────────────────────────────
DRY_RUN_ADDRESSES = {
    "base":       "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # vitalik.eth
    "polygon":    "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "avalanche":  "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "bitcoin":    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",  # 公開デモアドレス
}

DIVIDER = "=" * 60


def _prompt_address(network: str, hint: str = "0x...") -> str:
    """ウォレットアドレスを対話入力 (空Enter でスキップ)。"""
    print(f"\n  {network.upper()}")
    return input(f"    アドレス ({hint}) [スキップ: Enter]: ").strip()


def _fetch_chain(network: str, address: str, api_key: str) -> list:
    """各チェーンのフェッチャーを呼び出し、取引レコードを返す。"""
    try:
        if network == "base":
            from fetchers.base_fetcher import BaseFetcher
            return BaseFetcher(api_key).fetch(address)

        elif network == "polygon":
            from fetchers.polygon_fetcher import PolygonFetcher
            return PolygonFetcher(api_key).fetch(address)

        elif network == "avalanche":
            from fetchers.avalanche_fetcher import AvalancheFetcher
            return AvalancheFetcher(api_key).fetch(address)

        elif network == "bitcoin":
            from fetchers.bitcoin_fetcher import BitcoinFetcher
            return BitcoinFetcher().fetch(address)

    except Exception as exc:
        logger.error("[%s] 取得エラー: %s", network, exc)
        print(f"  ❌ {network}: エラーが発生しました → {exc}")

    return []


def main() -> None:
    # ── 引数パース ─────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="クリプト取引履歴トラッカー - 過去1年間の取引をCSVに出力します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="サンプルアドレスで動作テストを行います (APIキー必要)",
    )
    parser.add_argument(
        "--no-cryptact",
        action="store_true",
        help="Cryptact 形式 CSV の出力をスキップします",
    )
    args = parser.parse_args()

    # ── 環境変数ロード ─────────────────────────────────────────
    load_dotenv()

    print(f"\n{DIVIDER}")
    print("  🔗 クリプト取引履歴トラッカー")
    print("  Base / Polygon / Avalanche / Bitcoin 対応")
    print(f"{DIVIDER}")

    # ── アドレス収集 ───────────────────────────────────────────
    if args.dry_run:
        print("\n  [DRY RUN] サンプルアドレスで実行します\n")
        addresses = DRY_RUN_ADDRESSES
    else:
        print("\n  各ネットワークのウォレットアドレスを入力してください。")
        print("  不要なネットワークは Enter でスキップできます。\n")
        addresses = {
            "base":      _prompt_address("Base",      "0x..."),
            "polygon":   _prompt_address("Polygon",   "0x..."),
            "avalanche": _prompt_address("Avalanche", "0x..."),
            "bitcoin":   _prompt_address("Bitcoin",   "bc1q..."),
        }

    active = {k: v for k, v in addresses.items() if v}
    if not active:
        print("\n❌  アドレスが入力されていません。終了します。")
        sys.exit(1)

    # ── APIキー確認 ───────────────────────────────────────────
    # Etherscan API V2: 1つのキーで Base / Polygon / Ethereum 等に対応
    etherscan_key = (
        os.getenv("ETHERSCAN_API_KEY", "")
        or os.getenv("BASESCAN_API_KEY", "")      # 後方互換フォールバック
        or os.getenv("POLYGONSCAN_API_KEY", "")   # 後方互換フォールバック
    )
    # Avalanche は Routescan (非 Etherscan) のため別キー管理
    routescan_key = (
        os.getenv("ROUTESCAN_API_KEY", "")
        or os.getenv("SNOWTRACE_API_KEY", "")     # 旧キー互換
    )
    api_keys = {
        "base":      etherscan_key,
        "polygon":   etherscan_key,
        "avalanche": routescan_key,
        "bitcoin":   "",  # 不要
    }

    # ── 取引取得 ───────────────────────────────────────────────
    print(f"\n  {len(active)} ネットワークの取引を取得中...\n")
    all_records: list = []
    summary: list[str] = []

    for network, address in active.items():
        if network != "bitcoin" and not api_keys[network]:
            msg = f"  ⚠️  {network.upper()}: APIキーが未設定のためスキップします"
            print(msg)
            logger.warning(msg)
            summary.append(f"  {'':2}{network:12} ⚠️  APIキー未設定 (スキップ)")
            continue

        records = _fetch_chain(network, address, api_keys[network])
        all_records.extend(records)
        count = len(records)
        icon = "✅" if count > 0 else "📭"
        print(f"  {icon} {network:12} {count:>6} 件")
        summary.append(f"  {icon} {network:12} {count:>6} 件")

    # ── CSV 出力 ───────────────────────────────────────────────
    if not all_records:
        print("\n⚠️  取引が見つかりませんでした。アドレスやAPIキーを確認してください。")
        sys.exit(0)

    all_records.sort(key=lambda r: r["date"], reverse=True)

    print(f"\n📄 CSV を出力中... (合計 {len(all_records)} 件)")
    csv_path = export_to_csv(all_records)

    # ── Cryptact CSV 出力 ──────────────────────────────────────
    cryptact_path = None
    if not args.no_cryptact:
        print("⏳ Cryptact CSV を出力中...")
        cryptact_path = export_to_cryptact(all_records)

    # ── 完了メッセージ ─────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("  ✅ 完了！")
    print(f"\n{'chr(10)'.join(summary)}")
    print(f"\n  📁 通常 CSV         : {csv_path}")
    if cryptact_path:
        print(f"  📁 Cryptact CSV   : {cryptact_path}")
    print(f"  📊 合計取引数   : {len(all_records)} 件")
    print(f"{DIVIDER}\n")


if __name__ == "__main__":
    main()
