import os
import django
import pandas as pd
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
django.setup()

from news.models import News, Category


def import_news_data(csv_file='clean.csv'):
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"读取到 {len(df)} 条新闻数据")
        
        imported_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                title = str(row.get('新闻标题', '')).strip()
                content = str(row.get('新闻内容', '')).strip()
                source = str(row.get('新闻地址', '')).strip()
                author = str(row.get('新闻作者', '')).strip()
                image_url = str(row.get('图片', '')).strip()
                category_name = str(row.get('类型', '')).strip()
                publish_time_str = str(row.get('新闻时间', '')).strip()
                
                if not title or not content:
                    print(f"跳过第 {index + 1} 行：标题或内容为空")
                    skipped_count += 1
                    continue
                
                if News.objects.filter(title=title).exists():
                    print(f"跳过第 {index + 1} 行：标题已存在")
                    skipped_count += 1
                    continue
                
                category = None
                if category_name:
                    category, created = Category.objects.get_or_create(name=category_name)
                
                publish_time = None
                if publish_time_str and publish_time_str != 'nan':
                    try:
                        publish_time = pd.to_datetime(publish_time_str)
                    except Exception as e:
                        print(f"第 {index + 1} 行时间解析错误: {e}")
                
                news = News(
                    title=title,
                    content=content,
                    source=source if source else None,
                    author=author if author else None,
                    image_url=image_url if image_url else None,
                    category=category,
                    publish_time=publish_time
                )
                news.save()
                imported_count += 1
                print(f"成功导入第 {index + 1} 行: {title[:30]}...")
                
            except Exception as e:
                print(f"第 {index + 1} 行导入错误: {e}")
                skipped_count += 1
        
        print(f"\n导入完成！")
        print(f"成功导入: {imported_count} 条")
        print(f"跳过: {skipped_count} 条")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {csv_file}")
    except Exception as e:
        print(f"导入过程中发生错误: {e}")


if __name__ == '__main__':
    import_news_data()
