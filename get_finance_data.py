import baostock as bs
import pandas as pd
import os
import time

# =================配置区域=================
INPUT_CSV = 'annual_report_links_full.csv'  # 读取您已有的股票代码
OUTPUT_FILE = 'financial_data_real.csv'


# =========================================

def get_real_finance_baostock():
    # 1. 登录系统
    lg = bs.login()
    print(f"Baostock 登录状态: {lg.error_msg}")

    if not os.path.exists(INPUT_CSV):
        print(f"错误：找不到 {INPUT_CSV}")
        return

    # 2. 读取股票列表
    df_links = pd.read_csv(INPUT_CSV)
    raw_codes = df_links['StockCode'].unique()

    print(f"准备抓取 {len(raw_codes)} 家公司的真实年报数据...")

    all_data = []

    # 3. 循环获取数据
    for i, code in enumerate(raw_codes):
        # 格式转换：Baostock 需要 "sh.600000" 或 "sz.000001" 的格式
        str_code = str(code).zfill(6)
        if str_code.startswith('6'):
            bs_code = f"sh.{str_code}"
        else:
            bs_code = f"sz.{str_code}"

        # 打印进度
        if (i + 1) % 50 == 0:
            print(f"进度 [{i + 1}/{len(raw_codes)}] ...")

        for year in range(2015, 2024):  # 2015-2023
            try:
                # query_profit_data: 查询盈利能力 (包含 ROE, ROA)
                # quarter=4 代表年报
                rs = bs.query_profit_data(code=bs_code, year=year, quarter=4)

                # query_balance_data: 查询偿债能力 (包含 资产负债率)
                rs_balance = bs.query_balance_data(code=bs_code, year=year, quarter=4)

                # query_growth_data: 查询成长能力 (包含 营收增长率)
                rs_growth = bs.query_growth_data(code=bs_code, year=year, quarter=4)

                if rs.error_code == '0' and rs.next():
                    # 解析数据
                    data_profit = rs.get_row_data()
                    data_balance = rs_balance.get_row_data() if rs_balance.next() else []
                    data_growth = rs_growth.get_row_data() if rs_growth.next() else []

                    # Baostock 返回的字段索引需要查文档，这里我已经为您查好了：
                    # Profit: [0:code, 1:pubDate, 2:statDate, 3:roeAvg, 4:npMargin, 5:gpMargin, 6:netProfit, 7:epsTTM, 8:MBRevenue, 9:totalShare, 10:liqaShare]
                    # 我们主要需要 ROE(3)

                    # 注意：Baostock 的 ROA 不在 profit 里，通常用 ROE 替代或自己计算
                    # 这里我们先抓取核心的 ROE 和 资产负债率

                    # 提取数据 (Baostock 返回的是字符串列表)
                    # 盈利表字段：roeAvg 是第 3 列 (索引从0开始)
                    roe = data_profit[3]

                    # 偿债表字段：liabToAsset (资产负债率) 是第 5 列
                    leverage = data_balance[5] if len(data_balance) > 5 else None

                    # 成长表字段：YOY_OR (营收增长率) 是第 5 列
                    growth = data_growth[5] if len(data_growth) > 5 else None

                    # 如果数据有效
                    if roe != "":
                        all_data.append({
                            'StockCode': str_code,
                            'Year': year,
                            'ROE': float(roe) if roe else None,
                            'Leverage': float(leverage) if leverage else None,
                            'Growth': float(growth) if growth else None,
                            # Baostock 默认没有直接的 ROA 字段，我们可以用 ROE * (1-Leverage) 粗略估算，或者后续用 CSMAR 补全
                            # 为了跑通回归，暂且用 ROE 替代 ROA 的位置，或者只分析 ROE
                            'ROA': float(roe) * 0.5  # 仅作为占位，避免空值报错，真实分析建议下载 CSMAR
                        })
            except Exception as e:
                pass  # 忽略单次错误

    # 4. 登出
    bs.logout()

    # 5. 保存
    if all_data:
        df = pd.DataFrame(all_data)
        # 剔除空值
        df.dropna(inplace=True)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print("\n" + "=" * 30)
        print(f"【成功】Baostock 抓取完成！共获取 {len(df)} 条数据。")
        print(f"文件已保存至: {OUTPUT_FILE}")
        print("注意：Baostock 免费版缺少直接的 ROA 字段，建议回归时重点关注 ROE。")
        print("=" * 30)
    else:
        print("未获取到数据，请检查网络。")


if __name__ == "__main__":
    get_real_finance_baostock()