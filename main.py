import pandas as pd
from src.calculator import RebalanceCalculator

def main():
    print("=" * 50)
    print("  投資リバランス支援ツール")
    print("=" * 50)
    print()
    
    # データ読み込み
    df = pd.read_csv('data/sample_portfolio.csv')
    
    print("【現在のポートフォリオ】")
    print(df)
    print()
    
    # 計算
    calc = RebalanceCalculator(df)
    
    # 現在配分
    df = calc.calculate_current_allocation()
    print("【現在の配分】")
    for _, row in df.iterrows():
        print(f"{row['資産クラス']:10s}: {row['現在配分']:5.1f}% (目標: {row['目標配分']}%)")
    print()
    
    # リバランス案
    df = calc.calculate_rebalance_amount()
    print("【リバランス推奨案】")
    print(df[['資産クラス', '現在額', '目標額', '差額', '売買']])
    print()
    
    # サマリー
    summary = calc.get_summary()
    print("【サマリー】")
    for key, value in summary.items():
        print(f"{key}: ¥{value:,.0f}")

if __name__ == "__main__":
    main()