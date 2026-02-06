from playwright.sync_api import sync_playwright
import time
import re
import pandas as pd

def crawl_stock_data(url,output):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome",headless=True)
        page = browser.new_page() 
        try:
            # 导航到页面
            page.goto(url)
            time.sleep(5)
            # 尝试找到股票表格
            tables = page.query_selector_all("#mainResultTable table")
            print(f"找到 {len(tables)} 个表格")
            
            # 查找包含股票数据的表格（表头和表体）
            body_table = None
            
            for i, table in enumerate(tables):
                table_class = table.get_attribute("class") or ""
                table_id = table.get_attribute("id") or ""
                
                print(f"表格 {i}: class='{table_class}', id='{table_id}'")
                
                # 识别表头和表体
                if "el-table__body" in table_class:
                    body_table = table
                    print(f"已确认表体表格: 表格 {i}")
            
            if not body_table:
                print("未找到包含股票数据的表体表格")
                return
            
            print(f"已找到完整的股票数据表格（表头+表体")
            
            # 提取股票数据
            stocks = []
            # 从表体表格中提取数据行
            rows = body_table.query_selector_all("tr")
            print(f"在表体表格中找到 {len(rows)} 行数据")
            
            for row_idx, row in enumerate(rows):
                try:
                    cells = row.query_selector_all("td")
                    # 提取股票代码（第3列）
                    code = cells[2].inner_text().strip()
                    # 提取股票名称（第4列）
                    name = cells[3].inner_text().strip()
                    # 提取股票名称（第7列）
                    cell_content = cells[6].inner_html().strip()
                    # 使用正则表达式提取以%结尾的浮点型字符串
                    match = re.search(r'\d+(\.\d+)?%', cell_content)
                    dividend_yield = match.group(0) if match else ''
     
                    stocks.append({
                        "代码": code,
                        "名称": name,
                        "股息率": dividend_yield
                    })
                    # print(f"已提取: {code} - {name} - 股息率: {dividend_yield}")
                except Exception as e:
                    print(f"提取行 {row_idx} 数据时出错: {e}")
                    continue
            
            # 将数据保存到XLSX文件
            if stocks:
                # 创建DataFrame
                df = pd.DataFrame(stocks)
                # 保存为XLSX文件
                df.to_excel(output, index=False, engine='openpyxl')
                print(f"\n数据已保存到 {output}，共 {len(stocks)} 条记录")
            else:
                print("没有提取到任何股票数据")
                
        except Exception as e:
            print(f"爬虫执行出错: {e}")
        finally:
            # 关闭浏览器
            browser.close()

if __name__ == "__main__":
    # 默认参数
    default_url = "https://xuangu.eastmoney.com/Result?id=xc0eb93c162c0700f71e"
    default_output = "../../strategies/data/wfg_sh.xlsx"
    crawl_stock_data(default_url, default_output)