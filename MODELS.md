# 模型文件说明

模型权重**不放在 Git 仓库**里(单个文件就有几百 MB,超过 GitHub 100MB 限制),
而是备份在 HuggingFace Hub。clone 完代码后需要单独下载。

## 一键下载

```bash
pip install huggingface_hub
python download_models.py      # 私有仓库需先 huggingface-cli login
```

脚本会自动把所有模型放回下面这些代码期望的目录:

```
model/
├── bert-base-chinese/          # 官方预训练权重(脚本从 HF 官方拉取)
└── models/
    ├── bert_news_classifier/
    └── albert_news_classifier/
models/
├── bert_cnn_news_classifier/   # 默认模型,必需
├── bert_textrnn_news_classifier/
├── textcnn_news_classifier/
└── textrnn_news_classifier/
```

## 备份仓库

- HuggingFace 仓库:`litong1228/transformer_demo_models`（如有变动，同时改 `download_models.py` 和 `upload_models.py` 里的 `HF_REPO`）

## 重新备份(训练出新模型后)

```bash
huggingface-cli login          # 需要 write 权限的 token
python upload_models.py
```

## 完整复现流程

```bash
git clone git@github.com:litong1228/transformer_demo.git
cd transformer_demo
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python download_models.py
# 然后正常启动项目
```
