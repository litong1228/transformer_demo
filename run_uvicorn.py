import os
import sys
from pathlib import Path

# === C 盘空间不足应急:把所有临时缓存重定向到 E 盘 ===
_BASE = Path(__file__).parent.resolve()
_TMP = _BASE / '.runtime_cache'
_TMP.mkdir(exist_ok=True)
for k in ('TMPDIR', 'TEMP', 'TMP'):
    os.environ[k] = str(_TMP)
os.environ.setdefault('HF_HOME', str(_TMP / 'huggingface'))
os.environ.setdefault('TRANSFORMERS_CACHE', str(_TMP / 'huggingface' / 'transformers'))
os.environ.setdefault('TORCH_HOME', str(_TMP / 'torch'))
os.environ.setdefault('XDG_CACHE_HOME', str(_TMP / 'xdg'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')

# 导入uvicorn和Django的ASGI应用
import uvicorn
from news_project.asgi import application

# 运行服务器
if __name__ == "__main__":
    print("启动Uvicorn服务器...")
    uvicorn.run(application, host="127.0.0.1", port=8080, log_level="info")
