# Wallet Tracker
クリプト取引履歴トラッカー

Wallet Tracker は、ウォレットアドレスから過去のクリプト取引履歴を取得し、日時付き CSV として出力するツールです。

複数ブロックチェーンの取引履歴を統合し、Excel や税務ソフト（cryptact 等）で分析できる形式で保存できます。

現在は CLI ツールとして動作します。将来的に Web アプリ版の公開を予定しています。

---

## 対応ネットワーク

| Network | API | API Key |
|---|---|---|
| Ethereum | Etherscan API V2 | 必要（無料） |
| Polygon | Etherscan API V2 | 必要（無料） |
| Base | Etherscan API V2 | 有料プラン推奨 |
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
- Base
- Scroll
- Linea

無料プランでは Ethereum / Polygon など主要チェーンを利用できます。Base など一部チェーンは有料 API プランが必要になる場合があります。

そのためこのツールでは **API キーは利用者自身が設定する方式** を採用しています。

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
ROUTESCAN_API_KEY=
```

`ROUTESCAN_API_KEY` は空欄でも動作します。

---

## APIキー取得方法

### Etherscan API
`https://etherscan.io/myapikey`

### Routescan API
`https://routescan.io/documentation`

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

API キーを設定する前に動作確認できます。公開ウォレットアドレスを使い、CSV 出力テストを行います。

---

## 出力CSV

`output` フォルダに保存されます。

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
│   └── tx_classifier.py       # 取引分類
├── exporters/
│   ├── csv_exporter.py        # 独自CSV出力
│   └── cryptact_exporter.py   # cryptact CSV出力
├── output/                    # 生成CSV
├── logs/                      # ログ
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 注意事項

- Etherscan API は 1 リクエスト最大 10000 件です。取引数が多い場合は自動ページネーションで取得します。
- Etherscan Free Plan は約 5 requests/sec です。このツールはレート制限を考慮して待機時間を入れています。
- `.env` ファイルは絶対に Git にコミットしないでください。`.gitignore` により除外されています。

---

## OSSポリシー

このツールは **利用者自身の API キー** を使用する設計です。

理由:

- API コストをユーザー側で管理できる
- 無料プラン / 有料プランどちらにも対応できる
- OSS として公開しやすい
