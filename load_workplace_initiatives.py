#!/usr/bin/env python
"""職場環境等要件の取り組み項目をデータベースに投入"""
import os
import sys
import django

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shogu_kaizen_system.settings')
django.setup()

from plans.models import WorkplaceInitiative

def load_workplace_initiatives():
    print("職場環境等要件の取り組み項目を投入しています...")
    
    # 既存のデータを削除
    WorkplaceInitiative.objects.all().delete()
    
    initiatives = [
        # 資質の向上
        ('qualification', '1-1', '介護職員等への研修の実施（外部研修への派遣を含む）'),
        ('qualification', '1-2', '介護職員等への資格取得支援の実施'),
        ('qualification', '1-3', '職員の能力評価の制度化'),
        ('qualification', '1-4', 'ICT・介護ロボットやAI・センサーの活用による業務改善'),
        
        # 労働環境・処遇の改善
        ('work_style', '2-1', '雇用管理改善のための制度整備（賃金制度の明確化等）'),
        ('work_style', '2-2', '労働時間の短縮に向けた取り組み'),
        ('work_style', '2-3', '有給休暇取得促進のための取り組み'),
        ('work_style', '2-4', '育児・介護との両立支援制度の導入'),
        ('work_style', '2-5', 'ハラスメント対策の実施'),
        ('work_style', '2-6', '職場環境の整備（休憩室・更衣室の改善等）'),
        
        # やりがい・働きがいの醸成  
        ('balance', '3-1', 'ミーティング等による職場内コミュニケーションの円滑化'),
        ('balance', '3-2', '地域包括ケアの一員としてのモチベーション向上の取り組み'),
        ('balance', '3-3', 'キャリアパスの明示等による将来展望の提示'),
        ('balance', '3-4', '表彰制度等の実施による働きがいの向上'),
    ]
    
    for category, item_number, description in initiatives:
        WorkplaceInitiative.objects.create(
            category=category,
            item_number=item_number,
            description=description
        )
        print(f"  ✓ [{item_number}] {description[:40]}...")
    
    print(f"\n✅ {len(initiatives)}件の取り組み項目を投入しました！")

if __name__ == '__main__':
    load_workplace_initiatives()
