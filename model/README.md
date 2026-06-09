
## 项目结构

```
Transformer_demo1/
├── 1_data_preprocessing.py      # 第1集：数据预处理
├── 2_traditional_models.py      # 第2集：传统模型对比
├── 3_transformer_models.py      # 第3集：Transformer模型
├── 4_model_optimization.py      # 第4集：模型优化
├── 5_visualization.py           # 第5集：可视化分析
├── 6_web_app.py                 # 第6集：Web应用
├── data/                        # 数据集目录
│   ├── cnews/                   # THUCNews数据集
│   ├── processed/               # 处理后的数据
│   └── stopwords.txt            # 停用词表
├── models/                      # 模型保存目录
├── results/                     # 实验结果目录
├── visualizations/              # 可视化结果目录
├── requirements.txt             # 依赖包
└── README.md                    # 项目说明
```

## 数据集

使用THUCNews数据集的10个核心类别：
- 体育、财经、房产、家居、教育、科技、时尚、时政、游戏、娱乐

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行步骤

### 1. 数据预处理
```bash
python 1_data_preprocessing.py
```

### 2. 传统模型训练与评估
```bash
python 2_traditional_models.py
```

### 3. Transformer模型训练与评估
```bash
python 3_transformer_models.py
```

