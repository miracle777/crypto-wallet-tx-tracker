```markdown
# Wallet Tracker
クリプト取引履歴トラッカー

過去1年間のクリプト取引履歴を取得し、  
日時付きCSVとして出力するツールです。

複数ネットワークの取引を統合し、  
Excelや税務ソフトで分析できる形式で出力します。

CLIツールとして動作し、  
将来的にWebアプリ化を予定しています。

---

## 対応ネットワーク

| Network | API | API Key |
|---|---|---|
| Ethereum | Etherscan API V2 | 必要（無料） |
| Polygon | Etherscan API V2 | 必要（無料） |
| Base | Etherscan API V2 | 有料プラン推奨 |
| Avalanche | Routescan | 任意（無料枠あり） |
| Bitcoin | Blockstream API | 不要 |

Baseチェーンは Etherscan API V2 の free tier では制限がある場合があります。  
その場合は Etherscan の有料APIキーが必要です。

---

## セットアップ

### 1 Python依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2 APIキー設定

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

`.env` を編集

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

各ネットワークのウォレットアドレスを入力します。  
不要なネットワークは Enterキー でスキップできます。

### ドライランテスト

APIキーを設定する前に動作確認できます。

```bash
python wallet_tracker.py --dry-run
```

---

## 出力CSV

`output` フォルダに保存されます。

`transactions_YYYY-MM-DD_HHMMSS.csv`

Excelで開ける UTF-8 BOM形式 です。

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

税務ソフト cryptact 用CSVも出力できます。

`output` フォルダ:

`cryptact_YYYY-MM-DD_HHMMSS.csv`

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

wallet_tracker.py
メインプログラム

fetchers/

evm_fetcher.py
EVM共通取得

ethereum_fetcher.py
Ethereum

base_fetcher.py
Base

polygon_fetcher.py
Polygon

avalanche_fetcher.py
Avalanche

bitcoin_fetcher.py
Bitcoin

classifiers/

tx_classifier.py
取引分類

exporters/

csv_exporter.py
独自CSV

cryptact_exporter.py
cryptact CSV

output/
生成CSV

logs/
ログ

requirements.txt
.env.example
.gitignore
```

---

## 注意事項

- Etherscan APIは 1リクエスト最大10000件です。  
  取引数が多い場合はページネーションで取得します。
- Etherscan free tier は 約5 requests/sec です。  
  このツールはレート制限を考慮して待機します。
- `.env` ファイルは絶対にGitへコミットしないでください。
```
