# 🔗 Wallet Tracker (クリプト取引履歴トラッカー)

過去1年間のクリプト取引を取得し、日時付きで CSV にまとめるツールです。

## 対応ネットワーク

| ネットワーク | API | APIキー |
|---|---|---|
| **Base** | [Basescan](https://basescan.org) | 必要（無料） |
| **Polygon** | [Polygonscan](https://polygonscan.com) | 必要（無料） |
| **Avalanche** | [Routescan](https://routescan.io) | 必要（無料） |
| **Bitcoin** | [Blockstream.info](https://blockstream.info) | **不要** |

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

## 使い方

### 対話形式で実行（通常）

```bash
python wallet_tracker.py
```

各ネットワークのウォレットアドレスを順番に入力します。  
不要なネットワークは **Enter キーを押してスキップ** できます。

### ドライランテスト

APIキーを確認する前に動作テストしたい場合:

```bash
python wallet_tracker.py --dry-run
```

公開済みの有名アドレスを使ってAPIを呼び出し、CSV が生成されることを確認します。

## 出力 CSV フォーマット

`output/` フォルダに `transactions_YYYY-MM-DD_HHMMSS.csv` として保存されます。  
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
| `status` | `SUCCESS` / `FAILED` / `PENDING` |

### tx_type 一覧

| 値 | 説明 |
|---|---|
| `SEND` | 通常送金 |
| `RECEIVE` | 通常受取 |
| `SWAP` | DEX スワップ |
| `STAKE` | ステーキング入金 |
| `UNSTAKE` | ステーキング出金 |
| `REWARD` | ステーキング報酬・ボーナス |
| `ADD_LIQUIDITY` | 流動性追加 |
| `REMOVE_LIQUIDITY` | 流動性削除 |
| `NFT_PURCHASE` | NFT 購入 |
| `AIRDROP` | エアドロップ |
| `CONTRACT_INTERACTION` | その他コントラクト操作 (approve 等) |
| `UNKNOWN` | 不明 |

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
│   └── tx_classifier.py     ← 取引タイプ分類
├── exporters/
│   └── csv_exporter.py      ← CSV 出力
├── output/                  ← 生成された CSV (自動作成)
├── logs/                    ← ログファイル (自動作成)
├── requirements.txt
├── .env.example
└── .gitignore
```

## 注意事項

- EVM 系 API は 1 リクエストあたり最大 10,000 件の制限があります。  
  10,000 件を超える場合は自動的にページネーションします。
- APIキーの無料プランはレート制限があります（通常 5 calls/sec 以内）。  
  このツールは自動的に待機時間を入れています。
- `.env` ファイルは **絶対に Git にコミットしない** でください（`.gitignore` で除外済み）。
