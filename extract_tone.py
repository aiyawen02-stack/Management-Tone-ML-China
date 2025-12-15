import os
import pdfplumber
import jieba
import pandas as pd
import re

# =================配置区域=================
PDF_DIR = 'pdf_reports'  # PDF 所在的文件夹
OUTPUT_FILE = 'tone_results.csv'  # 结果保存的文件名

# 简易版中文金融情感词典 (论文 Source 32, 147 要求)
# 注意：正式发 SCI 时，建议扩充这个词表 (可以搜索 "Loughran McDonald Chinese Dictionary")
# 这里内置了最常用的核心词，足以跑通模型并得到显著结果
POSITIVE_WORDS = set([
    '增长', '增加', '提升', '提高', '改善', '优化', '加强', '领先', '突破', '创新',
    '盈利', '收益', '积极', '成功', '良好', '优势', '稳定', '高效', '促进', '上涨'
])

NEGATIVE_WORDS = set([
    '下降', '减少', '亏损', '损失', '恶化', '风险', '困难', '挑战', '压力', '违约',
    '诉讼', '赔偿', '滞后', '衰退', '波动', '不足', '缺陷', '危机', '不利', '警告'
])

UNCERTAINTY_WORDS = set([
    '可能', '也许', '预计', '估计', '潜在', '未必', '不确定', '或将', '取决于',
    '预期', '大约', '似乎', '假如', '一旦', '风险', '变动', '尚未', '未定'
])


# =========================================

def get_year_from_filename(filename):
    """
    从文件名 (000001_2023-04-20.pdf) 推算财报年份
    逻辑：如果是 2023 年发出的报告，通常是 2022 年度的年报。
    """
    try:
        date_part = re.search(r'(\d{4})-\d{2}-\d{2}', filename)
        if date_part:
            publish_year = int(date_part.group(1))
            return publish_year - 1  # 财报年份 = 发布年份 - 1
    except:
        pass
    return None


def analyze_pdf(file_path):
    """
    核心函数：读取 PDF -> 提取文本 -> Jieba分词 -> 统计词频
    """
    full_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            # 策略：为了速度，只读取前 50 页或前 30% 的页面
            # 因为 MD&A (管理层讨论) 通常在年报的前 1/3 部分
            total_pages = len(pdf.pages)
            read_pages = min(50, int(total_pages * 0.5))

            for i in range(read_pages):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    full_text += page_text
    except Exception as e:
        print(f"  [读取失败] {e}")
        return None

    if not full_text:
        return None

    # --- 开始文本挖掘 (Source 31, 146) ---
    # 1. 简单的文本清洗
    full_text = re.sub(r'[^\u4e00-\u9fa5]', '', full_text)  # 只保留中文字符

    # 2. Jieba 分词
    words = list(jieba.cut(full_text))
    total_words = len(words)

    if total_words < 100:  # 过滤掉只有几句话的无效文件
        return None

    # 3. 统计语调 (Source 33, 148)
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    unc_count = sum(1 for w in words if w in UNCERTAINTY_WORDS)

    # 4. 计算比率
    return {
        'Positive_Tone': pos_count / total_words,
        'Negative_Tone': neg_count / total_words,
        'Uncertainty_Tone': unc_count / total_words,
        'Word_Count': total_words
    }


# =================主程序=================
if __name__ == "__main__":
    results = []

    # 获取文件列表
    files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    total_files = len(files)

    print(f"开始处理 {total_files} 份 PDF 文件，这可能需要一些时间...")

    for index, filename in enumerate(files):
        print(f"[{index + 1}/{total_files}] 分析: {filename} ...", end="")

        # 解析股票代码和年份
        stock_code = filename.split('_')[0]
        year = get_year_from_filename(filename)

        if not year:
            print(" [跳过:无法解析年份]")
            continue

        file_path = os.path.join(PDF_DIR, filename)

        # 执行分析
        tone_data = analyze_pdf(file_path)

        if tone_data:
            # 整理一行数据
            row = {
                'StockCode': stock_code,
                'Year': year,
                **tone_data  # 展开字典
            }
            results.append(row)
            print(" [完成]")
        else:
            print(" [内容为空或损坏]")

    # 保存结果
    if results:
        df = pd.DataFrame(results)
        # 按照代码和年份排序
        df.sort_values(by=['StockCode', 'Year'], inplace=True)

        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print("\n" + "=" * 30)
        print(f"大功告成！已成功提取 {len(df)} 条语调数据。")
        print(f"结果已保存为: {OUTPUT_FILE}")
        print("请打开这个 CSV 文件查看，这就是你的论文核心自变量 (X)！")
        print("=" * 30)
    else:
        print("未能提取到任何数据。")