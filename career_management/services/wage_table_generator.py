from facility_management.models import Facility
from ..models import Position

# 地域の賃金相場データ（サンプル）
REGIONAL_WAGE_BENCHMARKS = {
    '東京都': {'care_staff_avg': 320000},
    '大阪府': {'care_staff_avg': 290000},
    'default': {'care_staff_avg': 270000}
}

class WageTableGenerator:
    """賃金テーブル自動生成サービス"""
    def __init__(self, facility: Facility):
        self.facility = facility

    def get_regional_wage_benchmark(self) -> dict:
        """事業所の所在地から地域の賃金相場を取得する"""
        address = self.facility.provider.address
        for prefecture, benchmark in REGIONAL_WAGE_BENCHMARKS.items():
            if prefecture in address:
                return benchmark
        return REGIONAL_WAGE_BENCHMARKS['default']

    def generate_optimized_wage_table(self, position: Position) -> dict:
        """職位に応じた最適な賃金テーブル案を生成する"""
        benchmark = self.get_regional_wage_benchmark()
        base_avg = benchmark['care_staff_avg']

        # 職位レベルに応じて基本給を傾斜配分
        level_multipliers = {1: 0.8, 2: 0.95, 3: 1.1, 4: 1.25, 5: 1.4}
        multiplier = level_multipliers.get(position.level, 1.0)
        
        start_salary = int(base_avg * multiplier)
        
        return {
            'base_salary_start': start_salary,
            'step_raise_amount': 2000,
            'max_steps': 30,
            'qualification_allowance': 5000 * position.level,
            'position_allowance': int(start_salary * 0.05 * (position.level - 1)),
        }