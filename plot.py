import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter
import os

# ============= 加载BERT数据 =============
bert_file = r'E:\毕设\code\news\Transormer_demo\training_metrics\bert_metrics_from_checkpoint.csv'
if os.path.exists(bert_file):
    print(f"找到BERT文件: {bert_file}")
    df_bert = pd.read_csv(bert_file)
    # 处理缺失值
    train_loss_bert = df_bert['train_loss'].fillna(method='ffill')
    # 平滑
    window_size_bert = 30
    polyorder_bert = 4
    train_loss_smooth_bert = savgol_filter(train_loss_bert, window_size_bert, polyorder_bert)
    print(f"BERT数据: {len(df_bert)}条, 范围 {df_bert['iteration'].min()}-{df_bert['iteration'].max()}")
else:
    print(f"BERT文件不存在: {bert_file}")
    exit()

# ============= 加载BERT_CNN数据 =============
cnn_file = r'E:\毕设\code\news\Transormer_demo\training_metrics\bert_cnn_metrics_20260316_161531.csv'
if os.path.exists(cnn_file):
    print(f"找到BERT_CNN文件: {cnn_file}")
    df_cnn = pd.read_csv(cnn_file)
    # 处理缺失值
    train_loss_cnn = df_cnn['train_loss'].fillna(method='ffill')
    # 平滑
    window_size_cnn = 30
    polyorder_cnn = 4
    train_loss_smooth_cnn = savgol_filter(train_loss_cnn, window_size_cnn, polyorder_cnn)
    print(f"BERT_CNN数据: {len(df_cnn)}条, 范围 {df_cnn['iteration'].min()}-{df_cnn['iteration'].max()}")
else:
    print(f"BERT_CNN文件不存在: {cnn_file}")
    exit()

# ============= 绘制对比图 =============
plt.figure(figsize=(14, 8))

# 绘制BERT曲线
plt.plot(df_bert['iteration'], train_loss_smooth_bert,
         color='darkblue', linewidth=2.5, label='BERT')

# 绘制BERT_CNN曲线
plt.plot(df_cnn['iteration'], train_loss_smooth_cnn,
         color='darkorange', linewidth=2.5, label='BERT_CNN')

plt.title('BERT vs BERT_CNN Training Loss Comparison', fontsize=16, fontweight='bold')
plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(fontsize=12)

# 设置Y轴范围（适应两者）
plt.ylim(0, 12)
plt.yticks(np.arange(0, 13, 1))

# 设置X轴范围
max_iter = max(df_bert['iteration'].max(), df_cnn['iteration'].max())
plt.xlim(0, max_iter)

plt.tight_layout()
plt.show()

print("\n📊 对比统计:")
print(f"BERT - 最终损失: {df_bert['train_loss'].iloc[-1]:.4f}, 最小损失: {df_bert['train_loss'].min():.4f}")
print(f"BERT_CNN - 最终损失: {df_cnn['train_loss'].iloc[-1]:.4f}, 最小损失: {df_cnn['train_loss'].min():.4f}")