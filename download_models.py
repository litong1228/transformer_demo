"""一键拉取项目所需的全部模型,放回代码期望的目录。

clone 项目后运行:
    1. pip install huggingface_hub
    2. python download_models.py
       (若你的 HF 备份仓库是私有的,先 huggingface-cli login)

它会:
  - 从你的备份仓库拉回 6 个训练好的分类器 -> models/ 和 model/models/
  - 从 HuggingFace 官方拉回 bert-base-chinese -> model/bert-base-chinese/
"""
import os
from huggingface_hub import snapshot_download

# ============ 改成你自己的 HF 仓库 ============
HF_REPO = os.environ.get("HF_MODELS_REPO", "tong10035/transformer_demo_models")
# ============================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    # 1) 训练产出的分类器 —— 仓库里已按相对路径存放,local_dir 设为项目根即可原位还原
    print(f"从 {HF_REPO} 拉取训练好的模型 ...")
    snapshot_download(
        repo_id=HF_REPO,
        repo_type="model",
        local_dir=PROJECT_ROOT,
    )

    # 2) 官方预训练 bert-base-chinese —— 只拉 PyTorch/safetensors 需要的文件,跳过 TF/Flax 省 ~850MB
    print("从官方拉取 bert-base-chinese ...")
    snapshot_download(
        repo_id="bert-base-chinese",
        repo_type="model",
        local_dir=os.path.join(PROJECT_ROOT, "model", "bert-base-chinese"),
        allow_patterns=[
            "config.json",
            "vocab.txt",
            "tokenizer*.json",
            "tokenizer_config.json",
            "special_tokens_map.json",
            "model.safetensors",
        ],
    )

    print("\n全部就绪,现在可以正常运行项目了。")


if __name__ == "__main__":
    main()
