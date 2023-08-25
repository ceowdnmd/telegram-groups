import requests
import sqlite3
from tqdm import tqdm

# 获取数据
url = "https://combot.org/api/chart/all?limit=0&offset=0"
response = requests.get(url)
data = response.json()

# 连接或创建 SQLite 数据库
connection = sqlite3.connect('groups.db')
cursor = connection.cursor()

# 创建表
create_table_query = '''
CREATE TABLE IF NOT EXISTS global (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang TEXT,
    num TEXT,
    title TEXT,
    uid TEXT
)
'''
cursor.execute(create_table_query)

# 初始化批量插入列表和批次大小
batch_insert_list = []
batch_size = 500  # 设置批次大小

# 循环遍历数据并插入批量列表
with tqdm(total=len(data)) as pbar:
    for index, entry in enumerate(data):
        l_value = entry.get("l", "")
        s_value = entry.get("s", "")
        t_value = entry.get("t", "")
        u_value = entry.get("u", "")

        formatted_member_count = f"{float(s_value) / 1000:.2f}"

        # 将值添加到批量插入列表中
        batch_insert_list.append((l_value, formatted_member_count, t_value, u_value))
        
        # 当批量插入列表达到批次大小时，执行插入操作并更新进度条
        if len(batch_insert_list) == batch_size or index == len(data) - 1:
            insert_query = "INSERT INTO global (lang, num, title, uid) VALUES (?, ?, ?, ?)"
            cursor.executemany(insert_query, batch_insert_list)
            connection.commit()
            
            batch_insert_list = []  # 清空批量插入列表

        pbar.update(1)  # 更新进度条

# 关闭连接
cursor.close()
connection.close()