import pandas as pd

class RebalanceCalculator:
    def __init__(self, portfolio_df, target_total=None):
        self.df = portfolio_df
        self.target_total = target_total or portfolio_df['現在額'].sum()
    
    def calculate_current_allocation(self):
        """現在の配分を計算"""
        total = self.df['現在額'].sum()
        self.df['現在配分'] = (self.df['現在額'] / total * 100).round(2)
        return self.df
    
    def calculate_rebalance_amount(self):
        """リバランス必要額を計算"""
        total = self.target_total
        
        # 目標金額
        self.df['目標額'] = (self.df['目標配分'] / 100 * total).round(0)
        
        # 差額
        self.df['差額'] = self.df['目標額'] - self.df['現在額']
        
        # 売買区分
        self.df['売買'] = self.df['差額'].apply(
            lambda x: '買い' if x > 0 else ('売り' if x < 0 else '-')
        )
        
        return self.df
    
    def get_summary(self):
        """サマリー情報"""
        total_buy = self.df[self.df['差額'] > 0]['差額'].sum()
        total_sell = abs(self.df[self.df['差額'] < 0]['差額'].sum())
        
        return {
            '総資産': self.target_total,
            '購入必要額': total_buy,
            '売却必要額': total_sell,
            '誤差': total_buy - total_sell
        }