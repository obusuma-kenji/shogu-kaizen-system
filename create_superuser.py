#!/usr/bin/env python
"""
スーパーユーザー自動作成スクリプト
環境変数からユーザー情報を読み取り、スーパーユーザーを作成します
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shogu_kaizen_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 環境変数から管理者情報を取得
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123456')

# スーパーユーザーが存在しない場合のみ作成
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'✅ スーパーユーザー「{username}」を作成しました')
else:
    print(f'ℹ️ スーパーユーザー「{username}」は既に存在します')
