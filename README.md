# tsumitatetoko-gmo
サービス終了した「[つみたてとこ](https://tsumitatetoko.com/)」の代わりにGMOコインでBTCのDCA (YCA)を行うBot

## 機能
- GMOコインでのBTC定額購入機能 (cronなどでの定期実行を想定)
- Line Notifyでの購入・エラー通知機能

## 設定ファイル
```
API_KEY=YOUR_API_KEY # GMOコインのAPIキー
SECRET_KEY=YOUR_SECRET_KEY # GMOコインのAPIシークレットキー
LOT=0 # 円建ての購入金額
ACCESS_TOKEN=YOUR_LINE_NOTIFY_ACCESS_TOKEN  # LINE Notifyのアクセストークン
```
- 各APIキーの取得方法
  - [GMOコイン](https://coin.z.com/jp/member/api)
    - ログイン後、`暗号資産`→`API`→`APIキーを新規追加`から以下の項目を許可
      - 資産: `余力情報を取得`
      - トレード: `注文`
  - [LINE Notify](https://notify-bot.line.me/my/)
    - ログイン後、マイページから`アクセストークンの発行(開発者向け)`→`トークンを発行する`

## セットアップ
設定ファイルの編集
```
cp .env.sample .env
nano .env
```
依存環境のインストール
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
スクリプトの実行
```
python main.py
```
