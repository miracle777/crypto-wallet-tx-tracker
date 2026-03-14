# Wallet Tracker
クリプト取引履歴トラッカー

過去1年間のクリプト取引を取得し、日時付きで CSV にまとめるツールです。  
**DEX SWAP / NFT 取引 / 自己送金** を自動判定し、**Cryptact 向け CSV** も同時出力します。

## 対応ネットワーク

| Network | API | API Key |
|---|---|---|
| Ethereum | Etherscan API V2 | 必要（無料） |
| Polygon | Etherscan API V2 | 必要（無料） |
| Base | Blockscout API | **不要（無料）** |
| Avalanche | Routescan | 任意（無料枠あり） |
| Bitcoin | Blockstream API | 不要 |

---

## Etherscan APIについて

Etherscan API V2 は単一の API キーで複数チェーンに対応できます。

対応チェーンの例:

- Ethereum
- Polygon
- Arbitrum
- Optimism
- Scroll
- Linea

無料プランでは Ethereum / Polygon など主要チェーンを利用できます。
**Base は Etherscan V2 の無料プランでは非対応のため、Blockscout API を使用しています。**

そのためこのツールでは **API キーは利用者自身が設定する方式** を採用しています。

---

## Base ネットワークについて

Base は Etherscan API V2 の**無料プランでは利用不可**（有料プラン必須）であることが確認されています。
そのため Base のみ **[Blockscout](https://base.blockscout.com) の無料 API** を使用しています。

### Blockscout の特性

Blockscout は Etherscan 互換の API を無料・APIキー不要で提供しています。
ただし、取引数の多いアドレスではレスポンスが遅くなる場合があります。

タイムアウト時の動作：

| 項目 | 設定値 |
|---|---|
| タイムアウト | 60秒 |
| リトライ回数 | 1回 |
| 1アクションの最大待ち時間 | 約1分 |
| 3アクション合計の最大待ち時間 | 約3分 |

> [!NOTE]
> 取引数が少ない一般的なウォレットではタイムアウトは発生しません。
> 取引数が非常に多いアドレスではタイムアウトして 0 件になる場合があります。

---

---

## セットアップ

### 1. Python依存関係をインストール

```bash
pip install -r requirements.txt
```

### 2. APIキー設定

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

`.env` を編集:

```env
ETHERSCAN_API_KEY=xxxxxxxxxxxx
```

---

## APIキー取得方法

### Etherscan API V2 (1キーで全チェーン対応)

| 手順 | 内容 |
|---|---|
| 1 | [https://etherscan.io/register](https://etherscan.io/register) でアカウント登録 |
| 2 | [https://etherscan.io/apidashboard](https://etherscan.io/apidashboard) にアクセス |
| 3 | 「**Add**」→ App Name 入力 → 作成 |
| 4 | 発行されたキーを `.env` の `ETHERSCAN_API_KEY=` に設定 |

無料プラン: 5 calls/sec まで（個人利用には十分）。  
Bitcoin は APIキー不要（Blockstream.info を使用）。

---

---

## 使い方

### 通常実行

```bash
python wallet_tracker.py
```

各ネットワークのウォレットアドレスを順番に入力します。不要なネットワークは Enter キーでスキップできます。

### ドライランテスト

```bash
python wallet_tracker.py --dry-run
```

### オプション一覧

| オプション | 説明 |
|---|---|
| `--dry-run` | 公開アドレスで動作テスト |
| `--no-cryptact` | Cryptact CSV の出力をスキップ |

---

## 出力ファイル

`output/` フォルダに以下の2ファイルが生成されます。

### 通常 CSV (`transactions_YYYY-MM-DD_HHMMSS.csv`)

Excel で直接開ける UTF-8 BOM 付き形式です。

| 列名 | 内容 |
|---|---|
| `date` | 取引日時 (JST) |
| `network` | ネットワーク名 |
| `tx_hash` | トランザクションハッシュ |
| `from` | 送信元アドレス |
| `to` | 送信先アドレス |
| `value` | 送金額 |
| `token_symbol` | トークンシンボル (ETH, POL, AVAX, BTC など) |
| `gas_fee` | ガス手数料 (EVM のみ) |
| `direction` | `IN` (受取) / `OUT` (送金) |
| `tx_type` | 取引タイプ (下表参照) |
| `status` | `SUCCESS` / `FAILED` |

### Cryptact CSV (`cryptact_YYYY-MM-DD_HHMMSS.csv`)

[Cryptact](https://cryptact.com) にそのままアップロードできる形式です。  
FAILED 取引は自動的に除外されます。

| tx_type | Cryptact Action |
|---|---|
| `SELF_TRANSFER` | `TRANSFER` (税務対象外) |
| `DEX_SWAP` / `SWAP` | `TRADE` |
| `NFT_PURCHASE` | `BUY` |
| `NFT_TRANSFER` | `SEND` / `RECEIVE` (direction による) |
| `RECEIVE` / `REWARD` / `AIRDROP` | `RECEIVE` |
| `SEND` / `STAKE` / `ADD_LIQUIDITY` | `SEND` |
| `UNSTAKE` / `REMOVE_LIQUIDITY` | `RECEIVE` |
| その他 | `OTHERS` |

---

## tx_type 一覧

| 値 | 説明 |
|---|---|
| `SEND` | 通常送金 |
| `RECEIVE` | 通常受取 |
| `DEX_SWAP` | DEX スワップ (Uniswap / PancakeSwap / TraderJoe 等) |
| `SWAP` | DEX スワップ (レガシー互換) |
| `STAKE` | ステーキング入金 |
| `UNSTAKE` | ステーキング出金 |
| `REWARD` | ステーキング報酬・ボーナス |
| `ADD_LIQUIDITY` | 流動性追加 |
| `REMOVE_LIQUIDITY` | 流動性削除 |
| `NFT_PURCHASE` | NFT 購入 (OpenSea / Blur 等のマーケット経由) |
| `NFT_TRANSFER` | NFT 直接転送 |
| `AIRDROP` | エアドロップ |
| `SELF_TRANSFER` | 自己送金 (税務対象外) |
| `CONTRACT_INTERACTION` | その他コントラクト操作 (approve 等) |
| `UNKNOWN` | 不明 |

---

## 拡張機能

### DEX SWAP 自動解析

以下の DEX ルーターを自動検出します（全対応ネットワーク共通）:

| DEX | ネットワーク |
|---|---|
| Uniswap V2 / V3 | Ethereum / Base |
| PancakeSwap V2 / V3 | BSC / Polygon |
| TraderJoe V1 / V2 | Avalanche |
| SushiSwap | Ethereum / Polygon |
| QuickSwap | Polygon |
| Pangolin | Avalanche |
| BaseSwap / Aerodrome | Base |
| 1inch V3/V4/V5 | マルチチェーン |

ルーターアドレスの定義: [`constants/dex_addresses.py`](constants/dex_addresses.py)

### NFT 取引解析

以下のマーケットプレイスを自動検出します:

| マーケット | バージョン |
|---|---|
| OpenSea | Seaport V1.1 / V1.4 / V1.5, Wyvern V2/V2.1 |
| Blur | Exchange / Blend |
| LooksRare | V1 / V2 |
| X2Y2 | - |
| Rarible | - |

- マーケット経由 → `NFT_PURCHASE`
- 直接転送 → `NFT_TRANSFER`

マーケットアドレスの定義: [`constants/nft_marketplaces.py`](constants/nft_marketplaces.py)

### 自己ウォレット判定

複数のウォレットを所有している場合、`config/wallets.json.example` をコピーして `config/wallets.json` を作成し、アドレスを登録してください。

```bash
cp config/wallets.json.example config/wallets.json
```

`config/wallets.json` の編集（プライバシー保護のため Git 追跡対象外です）:

```json
{
  "addresses": [
    "0xabc...",
    "0xdef..."
  ]
}
```

- `from` と `to` の **両方** が登録アドレスである場合に `SELF_TRANSFER` と判定
- Cryptact 出力では `TRANSFER` として扱われ、**税務対象外**になります
- `config/wallets.json` が空の場合は既存の動作と完全に同じです

---

## ファイル構成

```
transactions_YYYY-MM-DD_HHMMSS.csv
```

Excel で直接開ける UTF-8 BOM 形式です。

---

## CSV列

| 列 | 内容 |
|---|---|
| date | 取引日時 (JST) |
| network | ネットワーク名 |
| tx_hash | トランザクションハッシュ |
| from | 送信元アドレス |
| to | 送信先アドレス |
| value | 送金額 |
| token_symbol | トークンシンボル |
| gas_fee | ガス手数料 |
| direction | IN / OUT |
| tx_type | 取引タイプ |
| status | SUCCESS / FAILED / PENDING |

---

## cryptact対応

税務ソフト cryptact 用 CSV も出力できます。

`output` フォルダ:

```
cryptact_YYYY-MM-DD_HHMMSS.csv
```

### 主な対応取引

- SEND
- RECEIVE
- SWAP
- REWARD
- NFT_PURCHASE
- UNKNOWN

---

## ディレクトリ構成

```
crypto/
├── wallet_tracker.py          # メインプログラム
├── fetchers/
│   ├── evm_fetcher.py         # EVM共通処理
│   ├── ethereum_fetcher.py    # Ethereum
│   ├── base_fetcher.py        # Base
│   ├── polygon_fetcher.py     # Polygon
│   ├── avalanche_fetcher.py   # Avalanche
│   └── bitcoin_fetcher.py     # Bitcoin
├── classifiers/
│   ├── tx_classifier.py     ← 取引タイプ分類 (メイン)
│   ├── dex_classifier.py    ← DEX SWAP 判定 [NEW]
│   ├── nft_classifier.py    ← NFT 取引判定 [NEW]
│   └── wallet_classifier.py ← 自己ウォレット判定 [NEW]
├── constants/
│   ├── dex_addresses.py     ← DEX ルーターアドレス定数 [NEW]
│   └── nft_marketplaces.py  ← NFT マーケットプレイスアドレス定数 [NEW]
├── exporters/
│   ├── csv_exporter.py      ← 通常 CSV 出力
│   └── cryptact_exporter.py ← Cryptact 形式 CSV 出力 [NEW]
├── config/
│   └── wallets.json         ← 自己ウォレットアドレス設定 [NEW]
├── examples/
│   ├── swap_example.json    ← DEX SWAP サンプル [NEW]
│   ├── nft_example.json     ← NFT 取引サンプル [NEW]
│   └── self_transfer_example.json ← 自己送金サンプル [NEW]
├── output/                  ← 生成された CSV (自動作成)
├── logs/                    ← ログファイル (自動作成)
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 注意事項

- EVM 系 API は 1 リクエストあたり最大 10,000 件の制限があります。  
  10,000 件を超える場合は自動的にページネーションします。
- APIキーの無料プランはレート制限があります（通常 5 calls/sec 以内）。  
  このツールは自動的に待機時間を入れています。
- `config/wallets.json` の内容は秘密情報ではありませんが、プライバシーに注意してください。

---

## ライセンス / License

### MIT License
このプロジェクトは **MIT ライセンス** のもとで公開されています。

- **商用利用可能**: 開発者（私）への許可なく、商用目的で利用・改変・配布していただいて構いません。
- **著作権表示**: 利用の際は [LICENSE](LICENSE) ファイルを同梱してください。
- **無保証**: 本ツールを使用して発生した損失（税務上のミス、API 料金の発生、資産の損失等）について、開発者は一切の責任を負いません。
