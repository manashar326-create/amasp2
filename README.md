# Amazon 商品監視スクリプト

このスクリプトは指定した Amazon 商品ページを定期的にチェックし、入荷が検出されたら SMTP 経由でメール通知を送ります。

セットアップ

1. 依存パッケージをインストール:

```bash
python -m pip install -r requirements.txt
```

2. `.env.example` をコピーして `.env` を作成し、`PRODUCT_URL` と SMTP 設定を編集します。

```bash
copy .env.example .env
```

3. スクリプトを実行:

```bash
python main.py
```

注意
- Amazon のページ構造や地域によりキーワードが変わるため、必要に応じて `.env` のキーワードを調整してください。
- SMTP の資格情報は安全に管理してください（環境変数やアプリパスワードを推奨）。
