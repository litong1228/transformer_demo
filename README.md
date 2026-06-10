# 基于 Transformer 的新闻分类网站

一个 Django 新闻门户网站,集成了多种文本分类模型(BERT / ALBERT / TextCNN / TextRNN 及其组合),
可对新闻文本进行 **10 类中文新闻分类**(体育、娱乐、家居、房产、教育、时尚、时政、游戏、科技、财经)。

> 本科毕业设计项目。前台是新闻浏览站点,后台带站内管理 + 文本分类工具。

---

## ✨ 功能

- **新闻门户**:首页、分类列表、详情、搜索、评论、图片代理
- **用户系统**:注册 / 登录、收藏(书签)、个人资料、头像上传、改密码
- **文本分类**:
  - 单条文本在线分类(可切换 6 种模型,默认 `BERT-CNN`)
  - 批量分类(上传文件)、结果导出、历史记录
  - 提供 REST 接口 `/classify/text/api/`
- **管理后台**:
  - 站内管理 `/manage/`(新闻、分类、用户的增删改查)
  - Django Admin `/admin/`(SimpleUI 美化主题)

---

## 🧰 技术栈

| 层 | 技术 |
|----|----|
| 后端 | Django 4.2、Django REST framework |
| 数据库 | MySQL 8(`utf8mb4`) |
| 模型 | PyTorch + HuggingFace Transformers(`bert-base-chinese` 微调) |
| 前端 | Django 模板 + 静态资源,Admin 使用 SimpleUI |
| 采集 | requests 爬虫(`spider.py`) |

---

## 📦 环境要求

- Python 3.9 ~ 3.11
- MySQL 8.x(本地或远程)
- (可选)NVIDIA GPU + CUDA —— 没有也能跑,自动回退 CPU

---

## 🚀 快速开始

### 1. 拉代码 & 装依赖

```bash
git clone git@github.com:litong1228/transformer_demo.git
cd transformer_demo

python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

> **`mysqlclient` 装不上?**(Windows 常见)有两种办法:
> - 直接 `pip install mysqlclient` 失败时,从
>   [非官方 wheel](https://www.lfd.uci.edu/~gohlke/pythonlibs/) 下对应版本安装;
> - 或改用纯 Python 驱动:`pip install pymysql`,然后在 `news_project/__init__.py` 顶部加:
>   ```python
>   import pymysql
>   pymysql.install_as_MySQLdb()
>   ```

### 2. 下载模型权重(必需)

模型权重**不在 Git 仓库里**(单文件几百 MB,超 GitHub 限制),备份在 HuggingFace Hub。
详见 [`MODELS.md`](MODELS.md)。

```bash
python download_models.py     # 私有仓库需先 huggingface-cli login
```

它会自动把 6 个分类器 + 官方 `bert-base-chinese` 放回代码期望的目录。

### 3. 建数据库

在 MySQL 里建一个库(默认配置见 `news_project/settings.py`):

```sql
CREATE DATABASE news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> 默认连接参数:`root` / `123456` / `localhost:3306`。
> 和你本机不一致就改 `news_project/settings.py` 里的 `DATABASES`。

### 4. 初始化表结构 & 导入数据

```bash
python manage.py migrate                 # 建表
python manage.py createsuperuser         # 建管理员账号(用于 /admin)
```

导入示例新闻数据(二选一):

```bash
# 方式 A:从清洗好的 CSV 导入
python import_news.py

# 方式 B:直接导入数据库快照
#   mysql -u root -p news_db < db.sql
```

### 5. 启动

```bash
# 方式 A:Django 开发服务器(最常用)
python manage.py runserver        # http://127.0.0.1:8000

# 方式 B:Uvicorn(ASGI)
python run_uvicorn.py             # http://127.0.0.1:8080
```

打开浏览器访问对应地址即可。

| 入口 | 地址 |
|----|----|
| 网站首页 | `/` |
| 文本分类 | `/classify/text/` |
| 站内管理 | `/manage/` |
| Django Admin | `/admin/` |

---

## 📁 目录结构

```
Transormer_demo/
├── manage.py                 # Django 入口
├── run_uvicorn.py            # 用 Uvicorn(ASGI)启动
├── news_project/             # 项目配置(settings / urls / asgi / wsgi)
├── news/                     # 新闻 app:浏览、搜索、评论、站内管理(manage_views)
├── classifier/               # 分类 app:在线分类、批量、历史
│   └── model_loader.py       # 模型注册表 + 加载逻辑(MODEL_REGISTRY)
├── accounts/                 # 用户 app:登录注册、收藏、资料、头像
├── static/                   # 静态资源
│
├── model/
│   ├── bert-base-chinese/    # 官方预训练权重(download 脚本拉取)
│   └── models/               # 微调模型:bert / albert  ←─┐
├── models/                   # 微调模型:bert_cnn / bert_textrnn  │ 权重不在 git,
│                             #          textcnn / textrnn        │ 由 download_models.py 还原
│
├── download_models.py        # 一键下载模型权重 ◀── clone 后必跑
├── upload_models.py          # 训练出新模型后重新备份
├── MODELS.md                 # 模型备份说明
│
├── spider.py                 # 新闻爬虫
├── data_clean.py             # 数据清洗
├── import_news.py            # CSV → 数据库
├── plot.py                   # 训练曲线可视化
├── clean.csv / db.sql        # 示例数据 / 数据库快照
└── requirements.txt
```

---

## 🤖 可用的分类模型

在 `/classify/text/` 页面可切换;由 `classifier/model_loader.py` 的 `MODEL_REGISTRY` 定义。

| 模型 ID | 名称 | 说明 |
|--------|------|------|
| `bert_cnn` | BERT-CNN | **默认模型** |
| `bert_textrnn` | BERT-TextRNN | BERT + 双向 RNN |
| `bert` | BERT | 标准 BERT 微调 |
| `albert` | ALBERT | 轻量版 BERT |
| `textcnn` | TextCNN | 词向量 + CNN |
| `textrnn` | TextRNN | 词向量 + RNN |

> 设备选择:默认有 GPU 用 GPU,否则 CPU。可用环境变量覆盖:
> `CLASSIFIER_DEVICE=cpu|cuda|auto`

---

## 🔁 完整复现清单

```bash
git clone git@github.com:litong1228/transformer_demo.git
cd transformer_demo
python -m venv .venv && .\.venv\Scripts\Activate.ps1   # Win
pip install -r requirements.txt
python download_models.py            # 拉模型
# 建好 MySQL 库 news_db 后:
python manage.py migrate
python manage.py createsuperuser
python import_news.py                # 或 mysql ... < db.sql
python manage.py runserver
```

---

## ⚠️ 说明

- `settings.py` 里的 `SECRET_KEY`、数据库密码均为开发用默认值,**生产环境请替换并关闭 `DEBUG`**。
- 模型权重、训练数据、虚拟环境均不纳入 Git,克隆后按上文步骤还原。
