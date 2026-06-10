"""把训练好的模型上传到 HuggingFace Hub(一次性备份用)。

用法:
    1. pip install huggingface_hub
    2. huggingface-cli login        # 粘贴你的 HF token(在 https://huggingface.co/settings/tokens 生成,要 write 权限)
    3. 修改下面的 HF_REPO 为你自己的仓库名,然后运行:
       python upload_models.py

仓库不存在会自动创建(默认 private 私有)。
"""
import os
from huggingface_hub import HfApi, create_repo

# ============ 改成你自己的 HF 仓库(用户名/仓库名)============
HF_REPO = os.environ.get("HF_MODELS_REPO", "tong10035/transformer_demo_models")
PRIVATE = True  # 私有仓库;想公开改成 False
# ===========================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 需要备份的「训练产出」模型目录(相对项目根的路径会原样保留到 HF 仓库里,
# 这样下载脚本能把文件放回完全相同的位置)。
# 注意:model/bert-base-chinese 不在这里 —— 它是官方预训练权重,下载脚本会直接从 HF 官方重新拉。
MODEL_DIRS = [
    "models/bert_cnn_news_classifier",
    "models/bert_textrnn_news_classifier",
    "models/textcnn_news_classifier",
    "models/textrnn_news_classifier",
    "model/models/bert_news_classifier",
    "model/models/albert_news_classifier",
]


def main():
    api = HfApi()
    create_repo(HF_REPO, repo_type="model", private=PRIVATE, exist_ok=True)
    print(f"目标仓库: {HF_REPO} (private={PRIVATE})\n")

    for rel in MODEL_DIRS:
        local = os.path.join(PROJECT_ROOT, rel)
        if not os.path.isdir(local):
            print(f"  跳过(本地不存在): {rel}")
            continue
        print(f"  上传 {rel} ...")
        api.upload_folder(
            folder_path=local,
            path_in_repo=rel,           # 原样保留相对路径
            repo_id=HF_REPO,
            repo_type="model",
            commit_message=f"upload {rel}",
        )
    print("\n完成。在 https://huggingface.co/{} 可以看到。".format(HF_REPO))


if __name__ == "__main__":
    main()
