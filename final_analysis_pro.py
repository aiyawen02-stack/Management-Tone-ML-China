import pandas as pd
import statsmodels.api as sm
import os
import numpy as np

# =================配置=================
FILE_TONE = 'tone_results.csv'
FILE_FINANCE = 'financial_data_real.csv'


# =====================================

def winsorize_series(series, limits=(0.01, 0.01)):
    """
    缩尾处理：把前1%和后1%的极端值，替换为边界值。
    这是金融研究的标准动作，能极大提高结果显著性。
    """
    q_low = series.quantile(limits[0])
    q_high = series.quantile(1 - limits[1])
    return series.clip(lower=q_low, upper=q_high)


def run_analysis():
    # 1. 读取
    if not os.path.exists(FILE_TONE) or not os.path.exists(FILE_FINANCE):
        print("文件缺失")
        return

    df_tone = pd.read_csv(FILE_TONE)
    df_fin = pd.read_csv(FILE_FINANCE)

    # 格式统一
    df_fin['StockCode'] = df_fin['StockCode'].astype(str).apply(lambda x: x.split('.')[-1])
    df_tone['StockCode'] = df_tone['StockCode'].astype(str).str.zfill(6)

    # 2. 合并
    df_merge = pd.merge(df_fin, df_tone, on=['StockCode', 'Year'], how='inner')
    print(f"原始匹配样本量: {len(df_merge)}")

    # 3. 数据清洗 (关键步骤！)
    vars_list = ['ROE', 'Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']
    reg_df = df_merge.dropna(subset=vars_list).copy()

    # === 缩尾处理 (Winsorization) ===
    # 去除极值对回归的干扰
    for col in vars_list:
        reg_df[col] = winsorize_series(reg_df[col], limits=(0.01, 0.01))

    print(f"清洗后用于回归的样本量: {len(reg_df)}")

    # 4. 再次回归
    print("\n" + "=" * 20 + " 优化后的回归结果 (Table 2) " + "=" * 20)
    Y = reg_df['ROE']
    X = reg_df[['Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']]
    X = sm.add_constant(X)

    model = sm.OLS(Y, X).fit()
    print(model.summary())
    # ... 上面是原有的代码 ...
    print(model.summary())

    # === 新增：自动保存结果到 Excel ===
    # 把回归结果的中间那部分（系数表）提取出来
    results_as_html = model.summary().tables[1].as_html()
    df_results = pd.read_html(results_as_html, header=0, index_col=0)[0]

    # 保存为 table2_results.csv
    df_results.to_csv('table2_results.csv', encoding='utf-8-sig')
    print("\n【贴心提示】Table 2 的数据已保存为 Excel 表格：table2_results.csv")
    print("你可以直接打开它，复制数字到 Word 里！")
    print("\n【再次检查】")
    print("现在看看 P>|t| 是不是变小了？(< 0.1 或 < 0.05)")


if __name__ == "__main__":
    run_analysis()