import pandas as pd

df = pd.read_csv('xinwen.csv', names=['新闻标题', '新闻内容', '新闻地址', '新闻时间', '新闻作者', '图片', '类型'])

df = df.drop_duplicates()
df = df.dropna(subset="新闻内容")
df.to_csv('clean.csv', index=False)
