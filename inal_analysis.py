import pandas as pd
import statsmodels.api as sm
import os

# =================配置区域=================
FILE_TONE = 'tone_results.csv'  # X: 你的语调数据
FILE_FINANCE = 'financial_data_real.csv'  # Y: 你的财务数据 (Baostock版)


# =========================================

def run_analysis():
    # 1. 读取数据
    if not os.path.exists(FILE_TONE) or not os.path.exists(FILE_FINANCE):
        print("错误：找不到数据文件，请检查文件名！")
        return

    print("正在读取数据...")
    df_tone = pd.read_csv(FILE_TONE)
    df_fin = pd.read_csv(FILE_FINANCE)

    # 2. 关键：统一股票代码格式
    # 语调数据可能是 "000001"，财务数据可能是 "sz.000001"
    # 我们统一只保留 6 位数字
    df_fin['StockCode'] = df_fin['StockCode'].astype(str).apply(lambda x: x.split('.')[-1])
    df_tone['StockCode'] = df_tone['StockCode'].astype(str).str.zfill(6)

    # 3. 数据合并 (Merge)
    # 只有当 "股票代码" 和 "年份" 都对得上时，才拼在一起
    df_merge = pd.merge(df_fin, df_tone, on=['StockCode', 'Year'], how='inner')

    print(f"\n【合并成功】最终有效样本量: {len(df_merge)} 条")

    if len(df_merge) < 100:
        print("警告：匹配到的数据太少，请检查两张表的年份是否重合。")
        return

    # 4. 描述性统计 (Table 1) - 对应论文 Source 13, 160
    print("\n" + "=" * 20 + " Table 1: Descriptive Statistics " + "=" * 20)
    # 选取论文核心变量
    vars_list = ['ROE', 'Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']
    # .describe() 会自动计算均值、标准差、最大最小值
    desc_table = df_merge[vars_list].dropna().describe().T[['count', 'mean', 'std', 'min', 'max']]
    print(desc_table)

    # 5. 回归分析 (Table 2) - 对应论文 Source 13, 162
    print("\n" + "=" * 20 + " Table 2: Regression Results (OLS) " + "=" * 20)

    # 剔除空值
    reg_df = df_merge.dropna(subset=vars_list)

    # 定义模型：ROE = Intercept + Positive + Negative + Leverage + Growth
    # 注意：因为之前的 Baostock 简易版没算 ROA，这里我们直接回归真实的 ROE
    Y = reg_df['ROE']
    X = reg_df[['Positive_Tone', 'Negative_Tone', 'Leverage', 'Growth']]
    X = sm.add_constant(X)  # 添加常数项

    # 运行回归
    model = sm.OLS(Y, X).fit()

    # 打印结果
    print(model.summary())

    print("\n" + "=" * 30)
    print("【如何解读这个结果？(发 SCI 必看)】")
    print("请看 Table 2 中 'Positive_Tone' 这一行，往右看 'P>|t|' 这一列：")
    print("👉 如果值 < 0.1，这就叫'显著'！(带*)")
    print("👉 如果值 < 0.05，那就是'非常显著'！(带**)")
    print("👉 如果 'coef' 是正数，说明积极语调能预测更好的 ROE！")
    print("=" * 30)


if __name__ == "__main__":
    run_analysis()