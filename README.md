# Wallet Tracker (クリプト取引履歴トラッカー)

過去1年間のクリプト取引を取得し、日時付きで CSV にまとめるツールです。

EVMチェーンとBitcoinに対応し、複数ネットワークの取引履歴を統合してCSV出力します。

## 対応ネットワーク

| ネットワーク | API | APIキー |
|---|---|---|
| Base | Etherscan API V2 | 必要（無料） |
| Polygon | Etherscan API V2 | 必要（無料） |
| Avalanche | Routescan | 任意（無料枠あり） |
| Bitcoin | Blockstream.info | 不要 |

Base と Polygon は Etherscan API V2 の共通APIキーを使用します。

## セットアップ

### 1 Python依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2 APIキーの設定

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

`.env` を編集

```env
ETHERSCAN_API_KEY=xxxxxxxxxxxxxxxx
ROUTESCAN_API_KEY=xxxxxxxxxxxxxxxx
```

`ROUTESCAN_API_KEY` は空欄でも動作します（無料枠利用）。

### APIキーの取得方法

#### Etherscan API（Base / Polygon）

`https://etherscan.io/myapikey`

#### Routescan API（Avalanche）

`https://routescan.io/documentation`

## 使い方

### 対話形式で実行

```bash
python wallet_tracker.py
```

各ネットワークのウォレットアドレスを順番に入力します。  
不要なネットワークは Enter キーでスキップできます。

### ドライランテスト

APIキー設定前に動作確認する場合

```bash
python wallet_tracker.py --dry-run
```

公開ウォレットアドレスを使用してAPIテストを行います。

## 出力CSVフォーマット

`output` フォルダに

`transactions_YYYY-MM-DD_HHMMSS.csv`

として保存されます。  
Excelで直接開ける UTF-8 BOM 付きです。

| 列名 | 内容 |
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

### tx_type 一覧

- SEND
- RECEIVE
- SWAP
- STAKE
- UNSTAKE
- REWARD
- ADD_LIQUIDITY
- REMOVE_LIQUIDITY
- NFT_PURCHASE
- AIRDROP
- CONTRACT_INTERACTION
- UNKNOWN

## ファイル構成

```
cripto/

wallet_tracker.py
メインプログラム

fetchers/

evm_fetcher.py
base_fetcher.py
polygon_fetcher.py
avalanche_fetcher.py
bitcoin_fetcher.py

classifiers/

tx_classifier.py

exporters/

csv_exporter.py

output/
生成CSV

logs/
ログ

requirements.txt

.env.example

.gitignore
```

## 注意事項

- EVM API は 1リクエスト最大 10000件の制限があります。
  - 件数が多い場合はページネーションで自動取得します。
- Etherscan API の無料プランは 5 requests / sec 程度の制限があります。
  - このツールはレート制限を考慮し待機時間を入れています。
- `.env` ファイルは 絶対に Git にコミットしないでください。
  - `.gitignore` により除外されています。
