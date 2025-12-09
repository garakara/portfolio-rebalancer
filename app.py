import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.calculator import RebalanceCalculator

# ページ設定
st.set_page_config(
    page_title="投資リバランス支援ツール",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 投資リバランス支援ツール")
st.markdown("---")

# サイドバー
st.sidebar.header("⚙️ 設定")

# データ入力方法の選択
input_method = st.sidebar.radio(
    "データ入力方法",
    ["サンプルデータを使用", "手動入力", "CSVアップロード"]
)

# 初期データフレーム
if 'portfolio_df' not in st.session_state:
    st.session_state.portfolio_df = pd.DataFrame({
        '資産クラス': ['国内株式', '外国株式', '国内債券', '外国債券'],
        '現在額': [1000000, 800000, 500000, 300000],
        '目標配分': [25, 25, 25, 25]
    })

# データ入力
if input_method == "サンプルデータを使用":
    try:
        df = pd.read_csv('data/sample_portfolio.csv')
    except:
        df = st.session_state.portfolio_df
        
elif input_method == "手動入力":
    st.sidebar.subheader("ポートフォリオ入力")
    
    num_assets = st.sidebar.number_input("資産クラス数", 2, 10, 4)
    
    assets = []
    for i in range(num_assets):
        st.sidebar.markdown(f"**資産{i+1}**")
        col1, col2, col3 = st.sidebar.columns(3)
        
        with col1:
            name = st.text_input(f"名称{i+1}", f"資産{i+1}", key=f"name_{i}")
        with col2:
            amount = st.number_input(f"金額{i+1}", 0, 100000000, 1000000, 10000, key=f"amount_{i}")
        with col3:
            target = st.number_input(f"目標%{i+1}", 0, 100, 25, 1, key=f"target_{i}")
        
        assets.append({
            '資産クラス': name,
            '現在額': amount,
            '目標配分': target
        })
    
    df = pd.DataFrame(assets)
    
elif input_method == "CSVアップロード":
    uploaded_file = st.sidebar.file_uploader("CSVファイルを選択", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("ファイルを読み込みました!")
    else:
        df = st.session_state.portfolio_df
        st.sidebar.info("ファイルをアップロードしてください")

# 追加投資額
st.sidebar.markdown("---")
additional_investment = st.sidebar.number_input(
    "追加投資額 (円)",
    0, 10000000, 0, 10000,
    help="新たに投資する金額を入力"
)

# 計算
total_amount = df['現在額'].sum() + additional_investment
calc = RebalanceCalculator(df, target_total=total_amount)

# 現在配分を計算
df = calc.calculate_current_allocation()
df = calc.calculate_rebalance_amount()
summary = calc.get_summary()

# メイン表示エリア
tab1, tab2, tab3 = st.tabs(["📊 ダッシュボード", "📋 詳細データ", "💡 推奨案"])

# タブ1: ダッシュボード
with tab1:
    # サマリーメトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総資産", f"¥{summary['総資産']:,.0f}")
    
    with col2:
        st.metric("購入必要額", f"¥{summary['購入必要額']:,.0f}", 
                  delta=None if summary['購入必要額'] == 0 else "買い")
    
    with col3:
        st.metric("売却必要額", f"¥{summary['売却必要額']:,.0f}",
                  delta=None if summary['売却必要額'] == 0 else "売り")
    
    with col4:
        max_diff = df['現在配分'] - df['目標配分']
        max_deviation = max_diff.abs().max()
        st.metric("最大乖離", f"{max_deviation:.1f}%",
                  delta=f"{max_deviation:.1f}%" if max_deviation > 5 else None,
                  delta_color="inverse")
    
    st.markdown("---")
    
    # グラフ表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("現在の配分 vs 目標配分")
        
        # 棒グラフ(現在 vs 目標)
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='現在配分',
            x=df['資産クラス'],
            y=df['現在配分'],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='目標配分',
            x=df['資産クラス'],
            y=df['目標配分'],
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            barmode='group',
            yaxis_title='配分 (%)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("現在の資産配分")
        
        # 円グラフ
        fig = px.pie(
            df,
            values='現在額',
            names='資産クラス',
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)

# タブ2: 詳細データ
with tab2:
    st.subheader("📋 ポートフォリオ詳細")
    
    # データフレーム表示
    display_df = df.copy()
    display_df['現在額'] = display_df['現在額'].apply(lambda x: f"¥{x:,.0f}")
    display_df['目標額'] = display_df['目標額'].apply(lambda x: f"¥{x:,.0f}")
    display_df['差額'] = display_df['差額'].apply(lambda x: f"¥{x:,.0f}")
    display_df['現在配分'] = display_df['現在配分'].apply(lambda x: f"{x:.1f}%")
    display_df['目標配分'] = display_df['目標配分'].apply(lambda x: f"{x}%")
    
    st.dataframe(display_df, use_container_width=True)
    
    # CSV ダウンロード
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 CSVダウンロード",
        csv,
        "portfolio_rebalance.csv",
        "text/csv"
    )

# タブ3: 推奨案
with tab3:
    st.subheader("💡 リバランス推奨案")
    
    # 売却リスト
    sell_df = df[df['差額'] < 0].copy()
    if len(sell_df) > 0:
        st.markdown("### 🔴 売却推奨")
        for _, row in sell_df.iterrows():
            st.warning(
                f"**{row['資産クラス']}**: ¥{abs(row['差額']):,.0f} 売却\n\n"
                f"現在: ¥{row['現在額']:,.0f} ({row['現在配分']:.1f}%) → "
                f"目標: ¥{row['目標額']:,.0f} ({row['目標配分']}%)"
            )
    
    # 購入リスト
    buy_df = df[df['差額'] > 0].copy()
    if len(buy_df) > 0:
        st.markdown("### 🟢 購入推奨")
        for _, row in buy_df.iterrows():
            st.success(
                f"**{row['資産クラス']}**: ¥{row['差額']:,.0f} 購入\n\n"
                f"現在: ¥{row['現在額']:,.0f} ({row['現在配分']:.1f}%) → "
                f"目標: ¥{row['目標額']:,.0f} ({row['目標配分']}%)"
            )
    
    # バランス確認
    if len(sell_df) == 0 and len(buy_df) == 0:
        st.info("✅ ポートフォリオは目標配分と一致しています")
    
    # 実行ステップ
    if len(sell_df) > 0 or len(buy_df) > 0:
        st.markdown("---")
        st.markdown("### 📝 実行ステップ")
        
        step = 1
        for _, row in sell_df.iterrows():
            st.write(f"{step}. {row['資産クラス']}を ¥{abs(row['差額']):,.0f} 売却")
            step += 1
        
        for _, row in buy_df.iterrows():
            st.write(f"{step}. {row['資産クラス']}を ¥{row['差額']:,.0f} 購入")
            step += 1

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    💡 Tip: サイドバーから追加投資額を入力すると、
    新規資金を含めたリバランス案が表示されます
    </div>
    """,
    unsafe_allow_html=True
)