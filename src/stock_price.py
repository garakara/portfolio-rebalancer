import yfinance as yf
import pandas as pd

def get_stock_price(ticker):
    """株価を取得"""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    
    if len(hist) > 0:
        return hist['Close'].iloc[-1]
    return None

def get_portfolio_value(holdings):
    """
    holdings: [{'ticker': '1306.T', 'shares': 100}, ...]
    """
    total = 0
    details = []
    
    for holding in holdings:
        price = get_stock_price(holding['ticker'])
        if price:
            value = price * holding['shares']
            total += value
            details.append({
                'ticker': holding['ticker'],
                'shares': holding['shares'],
                'price': price,
                'value': value
            })
    
    return total, pd.DataFrame(details)

def calculate_risk_metrics(df):
    """リスク指標を計算"""
    
    # 集中度(ハーフィンダール指数)
    concentrations = (df['現在配分'] / 100) ** 2
    hhi = concentrations.sum()
    
    # 分散度(0-1, 1に近いほど分散)
    diversification = 1 - hhi
    
    return {
        'ハーフィンダール指数': hhi,
        '分散度': diversification,
        '評価': 'よく分散' if diversification > 0.7 else '集中気味'
    }

# 使用例
if __name__ == "__main__":
    holdings = [
        {'ticker': '1306.T', 'shares': 100},  # TOPIX連動ETF
        {'ticker': '^N225', 'shares': 10}     # 日経225
    ]
    
    total, df = get_portfolio_value(holdings)
    print(f"総資産: ¥{total:,.0f}")
    print(df)