# 介護職員等処遇改善加算 申請支援システム

## クイックスタート

### 1. Djangoをインストール
```bash
pip install Django
```

### 2. データベースを作成
```bash
python manage.py migrate
```

### 3. サンプルデータを投入
```bash
python load_sample_data.py
```

### 4. サーバーを起動
```bash
python manage.py runserver
```

### 5. アクセス
- システムトップ: http://127.0.0.1:8000/
- 管理画面: http://127.0.0.1:8000/admin/

## 管理者アカウントの作成

```bash
python manage.py createsuperuser
```

## 主な機能

- ✅ 事業所・職員管理
- ✅ 職位階層の定義
- ✅ 号級賃金テーブル構築支援
- ✅ 地域相場に基づく賃金提案

## システム要件

- Python 3.8以上
- Django 5.2以上

## トラブルシューティング

### ポート8000が使用中の場合
```bash
python manage.py runserver 8001
```

### データベースをリセット
```bash
del db.sqlite3     # Windowsの場合
rm db.sqlite3      # Mac/Linuxの場合
python manage.py migrate
python load_sample_data.py
```
