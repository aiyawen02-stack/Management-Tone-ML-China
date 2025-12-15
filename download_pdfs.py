import pandas as pd
import requests
import os
import time
import random

# =================配置区域=================
# 1. 读取上一名为生成的 CSV 文件名
INPUT_CSV = 'annual_report_links_full.csv'

# 2. 设置 PDF 保存的文件夹名称
SAVE_DIR = 'pdf_reports'


# =========================================

def download_pdf(url, save_path):
    """
    下载单个 PDF 文件的函数
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # 发送请求，设置超时为 30 秒
        response = requests.get(url, headers=headers, stream=True, timeout=30)

        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"下载失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载出错: {e}")
        return False


if __name__ == "__main__":
    # 1. 检查 CSV 文件是否存在
    if not os.path.exists(INPUT_CSV):
        print(f"错误：找不到 {INPUT_CSV} 文件！请先运行上一步的爬虫代码。")
        exit()

    # 2. 创建保存 PDF 的文件夹
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
        print(f"已创建文件夹: {SAVE_DIR}")

    # 3. 读取链接列表
    print("正在读取下载列表...")
    df = pd.read_csv(INPUT_CSV)
    total_files = len(df)
    print(f"共读取到 {total_files} 个待下载文件。")

    # 4. 开始循环下载
    success_count = 0

    for index, row in df.iterrows():
        stock_code = str(row['StockCode']).zfill(6)  # 补全代码为6位
        publish_date = row['PublishDate']
        pdf_url = row['PDF_Link']

        # 构建文件名: 股票代码_发布日期.pdf (例如: 000001_2023-03-15.pdf)
        file_name = f"{stock_code}_{publish_date}.pdf"
        save_path = os.path.join(SAVE_DIR, file_name)

        # 进度提示
        print(f"[{index + 1}/{total_files}] 处理: {file_name} ...", end="")

        # 检查是否已存在（断点续传功能）
        if os.path.exists(save_path):
            print(" [已存在，跳过]")
            success_count += 1
            continue

        # 执行下载
        if download_pdf(pdf_url, save_path):
            print(" [下载成功]")
            success_count += 1
        else:
            print(" [失败]")

        # 随机休眠，避免对服务器造成压力
        time.sleep(random.uniform(0.5, 1.5))

    print("\n" + "=" * 30)
    print(f"任务结束！成功下载: {success_count}/{total_files}")
    print(f"文件保存在: {os.path.abspath(SAVE_DIR)}")
    print("=" * 30)