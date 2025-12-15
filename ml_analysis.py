import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =================配置区域=================
FILE_TONE = 'tone_results.csv'
FILE_FINANCE = 'financial_data_real.csv'
# =========================================

# 解决画图中文乱码
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def winsorize_series(series, limits=(0.01, 0.01)):
    q_low = series.quantile(limits[0])
    q_high = series.quantile(1 - limits[1])
    return series.clip(lower=q_low, upper=q_high)


def run_ml_analysis():
    # 1. 读取数据
    if not os.path.exists(FILE_TONE) or not os.path.exists(FILE_FINANCE):
        print("错误：数据文件缺失")
        return

    df_tone = pd.read_csv(FILE_TONE)
    df_fin = pd.read_csv(FILE_FINANCE)

    # 格式统一
    df_fin['StockCode'] = df_fin['StockCode'].astype(str).apply(lambda x: x.split('.')[-1])
    df_tone['StockCode'] = df_tone['StockCode'].astype(str).str.zfill(6)

    df_merge = pd.merge(df_fin, df_tone, on=['StockCode', 'Year'], how='inner')

    # 2. 数据准备
    vars_list = ['ROE', 'Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']
    data = df_merge.dropna(subset=vars_list).copy()

    for col in vars_list:
        data[col] = winsorize_series(data[col])

    X = data[['Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']]
    y = data['ROE']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. 模型竞技
    results = []

    # OLS
    ols = LinearRegression()
    ols.fit(X_train, y_train)
    y_pred_ols = ols.predict(X_test)
    results.append({
        'Model': 'OLS Regression (Baseline)',
        'R-squared': round(r2_score(y_test, y_pred_ols), 3),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, y_pred_ols)), 3),
        'MAE': round(mean_absolute_error(y_test, y_pred_ols), 3)
    })

    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    results.append({
        'Model': 'Random Forest',
        'R-squared': round(r2_score(y_test, y_pred_rf), 3),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, y_pred_rf)), 3),
        'MAE': round(mean_absolute_error(y_test, y_pred_rf), 3)
    })

    # Gradient Boosting
    gbr = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gbr.fit(X_train, y_train)
    y_pred_gbr = gbr.predict(X_test)
    results.append({
        'Model': 'Gradient Boosting',
        'R-squared': round(r2_score(y_test, y_pred_gbr), 3),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, y_pred_gbr)), 3),
        'MAE': round(mean_absolute_error(y_test, y_pred_gbr), 3)
    })

    # 4. 保存 Table 3
    df_results = pd.DataFrame(results)

    # === 关键：保存为 CSV ===
    df_results.to_csv('table3_ml_performance.csv', index=False, encoding='utf-8-sig')

    print("\n" + "=" * 20 + " Table 3: Model Performance " + "=" * 20)
    print(df_results)
    print("\n【成功】Table 3 已保存为: table3_ml_performance.csv")
    print("你可以直接复制里面的数据到 Word！")

    # 5. 生成图片
    importance = rf.feature_importances_  # 这里用随机森林的特征重要性
    feature_names = X.columns
    df_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importance})
    df_imp = df_imp.sort_values(by='Importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=df_imp, palette='viridis')
    plt.title('Figure 2: Feature Importance (Random Forest)', fontsize=15)
    plt.tight_layout()
    plt.savefig('Figure2_Feature_Importance.png', dpi=300)
    print("【成功】特征图已保存为: Figure2_Feature_Importance.png")


if __name__ == "__main__":
    run_ml_analysis()