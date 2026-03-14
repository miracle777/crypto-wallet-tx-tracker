# 🔗 Wallet Tracker (クリプト取引履歴トラッカー)

過去1年間のクリプト取引を取得し、日時付きで CSV にまとめるツールです。  
**DEX SWAP / NFT 取引 / 自己送金** を自動判定し、**Cryptact 向け CSV** も同時出力します。

## 対応ネットワーク

| ネットワーク | API | APIキー |
|---|---|---|
| **Base** | [Basescan](https://basescan.org) | 必要（無料） |
| **Polygon** | [Polygonscan](https://polygonscan.com) | 必要（無料） |
| **Avalanche** | [Routescan](https://routescan.io) | 必要（無料） |
| **Bitcoin** | [Blockstream.info](https://blockstream.info) | **不要** |

---

## セットアップ

### 1. Python 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. APIキーの設定

`.env.example` をコピーして `.env` を作成し、各 API キーを設定してください。

```bash
cp .env.example .env
```

`.env` ファイルを編集:
```
BASESCAN_API_KEY=xxxxxxxxxxxxxxxxxxxx
POLYGONSCAN_API_KEY=xxxxxxxxxxxxxxxxxxxx
ROUTESCAN_API_KEY=xxxxxxxxxxxxxxxxxxxx
```

#### APIキーの取得方法

| サービス | 取得先URL |
|---|---|
| Basescan | https://basescan.org/myapikey |
| Polygonscan | https://polygonscan.com/myapikey |
| Routescan | https://routescan.io/ |

いずれも **無料** で取得できます。

---

## 使い方

### 対話形式で実行（通常）

```bash
python wallet_tracker.py
```

各ネットワークのウォレットアドレスを順番に入力します。  
不要なネットワークは **Enter キーを押してスキップ** できます。

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

複数のウォレットを所有している場合、`config/wallets.json` に登録するだけで  
ウォレット間の送金を自動的に `SELF_TRANSFER` として判定します。

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
cripto/
├── wallet_tracker.py        ← メインプログラム
├── fetchers/
│   ├── evm_fetcher.py       ← EVM 共通基底クラス
│   ├── base_fetcher.py      ← Base チェーン
│   ├── polygon_fetcher.py   ← Polygon
│   ├── avalanche_fetcher.py ← Avalanche
│   └── bitcoin_fetcher.py   ← Bitcoin (Blockstream API)
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
- `.env` ファイルは **絶対に Git にコミットしない** でください（`.gitignore` で除外済み）。
- `config/wallets.json` の内容は秘密情報ではありませんが、プライバシーに注意してください。
