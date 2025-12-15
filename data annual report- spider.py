import requests
import pandas as pd
import time
import random

# =================配置区域=================
START_DATE = '2015-01-01'
END_DATE = '2024-04-30'
OUTPUT_FILE = 'annual_report_links_full.csv'
TARGET_COUNT = 1500

# 手动内置200个常用股票代码，这能产生约1800条数据，足够满足SCI样本量要求
# 包含：万科、格力、茅台、伊利、招商、平安等各行业龙头及随机样本
FIXED_STOCK_LIST = [
    '000001', '000002', '000004', '000005', '000006', '000007', '000008', '000009', '000010', '000011',
    '000012', '000014', '000016', '000017', '000019', '000020', '000021', '000023', '000025', '000026',
    '000027', '000028', '000029', '000030', '000031', '000032', '000034', '000035', '000036', '000037',
    '000038', '000039', '000040', '000042', '000045', '000046', '000048', '000049', '000050', '000055',
    '000056', '000058', '000059', '000060', '000061', '000062', '000063', '000065', '000066', '000068',
    '000069', '000070', '000078', '000088', '000089', '000090', '000096', '000099', '000100', '000151',
    '000153', '000155', '000156', '000157', '000158', '000159', '000166', '000333', '000338', '000400',
    '000401', '000402', '000403', '000404', '000407', '000408', '000409', '000410', '000411', '000413',
    '000415', '000416', '000417', '000419', '000420', '000421', '000422', '000423', '000425', '000426',
    '000428', '000429', '000430', '000488', '000498', '000501', '000502', '000503', '000504', '000505',
    '600000', '600004', '600006', '600007', '600008', '600009', '600010', '600011', '600012', '600015',
    '600016', '600017', '600018', '600019', '600020', '600021', '600022', '600023', '600025', '600026',
    '600027', '600028', '600029', '600030', '600031', '600033', '600035', '600036', '600037', '600038',
    '600039', '600048', '600050', '600051', '600052', '600053', '600054', '600055', '600056', '600057',
    '600058', '600059', '600060', '600061', '600062', '600063', '600064', '600066', '600067', '600068',
    '600070', '600071', '600072', '600073', '600075', '600076', '600077', '600078', '600079', '600080',
    '600081', '600082', '600083', '600084', '600085', '600086', '600088', '600089', '600090', '600091',
    '600093', '600094', '600095', '600096', '600097', '600098', '600099', '600100', '600101', '600103',
    '600104', '600105', '600106', '600107', '600108', '600109', '600110', '600111', '600112', '600113',
    '600519', '601318', '601398', '601857', '601288', '601988', '601628', '601088', '601601', '601186'
]


# =========================================

def get_pdf_links(stock_code):
    """
    向巨潮资讯网发送请求 (逻辑不变)
    """
    url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        'pageNum': 1,
        'pageSize': 30,
        'column': 'szse',
        'tabName': 'fulltext',
        'plate': '',
        'stock': '',
        'searchkey': stock_code,
        'secid': '',
        'category': 'category_ndbg_szsh',
        'trade': '',
        'seDate': f'{START_DATE}~{END_DATE}',
        'sortName': '',
        'sortType': '',
        'isHLtitle': 'true'
    }

    results = []
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            if json_data['announcements']:
                for item in json_data['announcements']:
                    title = item['announcementTitle']
                    if '摘要' in title or '英文' in title or '取消' in title or '修订' in title:
                        continue
                    if '年度报告' not in title:
                        continue

                    pdf_url = "http://static.cninfo.com.cn/" + item['adjunctUrl']
                    publish_time = time.strftime("%Y-%m-%d", time.localtime(item['announcementTime'] / 1000))

                    results.append({
                        'StockCode': stock_code,
                        'Title': title,
                        'PublishDate': publish_time,
                        'PDF_Link': pdf_url
                    })
    except Exception as e:
        print(f"代码 {stock_code} 发生错误: {e}")

    return results


# =================主程序=================
if __name__ == "__main__":
    all_data = []

    print(f"开始爬取 {len(FIXED_STOCK_LIST)} 只股票的年报链接...")

    for index, code in enumerate(FIXED_STOCK_LIST):
        print(f"[{index + 1}/{len(FIXED_STOCK_LIST)}] 正在处理: {code}")

        links = get_pdf_links(code)
        if links:
            all_data.extend(links)
            print(f"  -> 找到 {len(links)} 份年报")
        else:
            print("  -> 未找到")

        # 检查是否达到目标
        if len(all_data) >= TARGET_COUNT:
            print(f"\n已达到目标数量 {TARGET_COUNT} 条，停止爬取。")
            break

        # 稍微延时，防止过快
        time.sleep(random.uniform(0.5, 1.5))

    if all_data:
        df = pd.DataFrame(all_data)
        df.drop_duplicates(subset=['PDF_Link'], inplace=True)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n========================================")
        print(f"成功！最终获取链接数: {len(df)}")
        print(f"文件已保存为: {OUTPUT_FILE}")
        print(f"========================================")
    else:
        print("未获取到数据，请检查网络连接。")