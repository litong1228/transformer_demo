import os
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')

# 导入Django
import django
django.setup()

print(f"Django版本: {django.__version__}")
print("Django设置已加载")

# 尝试导入一些模型
try:
    from news.models import News, Category
    print("成功导入News和Category模型")
    
    # 尝试连接数据库
    category_count = Category.objects.count()
    news_count = News.objects.count()
    print(f"数据库中有 {category_count} 个分类和 {news_count} 条新闻")
    
except Exception as e:
    print(f"导入或数据库操作失败: {e}")
    import traceback
    traceback.print_exc()

print("测试完成")
