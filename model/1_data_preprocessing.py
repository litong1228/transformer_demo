import pandas as pd
import numpy as np
import os
import jieba
from sklearn.model_selection import train_test_split

# 定义标签名称
label_names = ['体育', '财经', '房产', '家居', '教育', '科技', '时尚', '时政', '游戏', '娱乐']
label2id = {label: idx for idx, label in enumerate(label_names)}
id2label = {idx: label for idx, label in enumerate(label_names)}

# 加载THUCNews数据集
def load_thucnews_data(data_dir):
    data = []
    for filename in ['cnews.train.txt', 'cnews.val.txt', 'cnews.test.txt']:
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    label, text = line.split('\t', 1)
                    data.append({'label': label, 'text': text})
    return pd.DataFrame(data)

# 创建更平衡的数据集（每类5000条）
def create_balanced_dataset(raw_data, samples_per_class=5000):
    balanced_data = []
    for label in label_names:
        class_data = raw_data[raw_data['label'] == label]
        sampled = class_data.sample(min(samples_per_class, len(class_data)))
        balanced_data.append(sampled)
    return pd.concat(balanced_data)

# 加载停用词
def load_stopwords(stopwords_path):
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set([line.strip() for line in f if line.strip()])
    return stopwords

# 主函数
def main():
    bert_output_dir = 'data/bert_processed'  # 用于 BERT：原始文本
    traditional_output_dir = 'data/processed'  # 用于传统模型：分词后文本
    # 加载数据
    data_dir = 'data/cnews'
    raw_data = load_thucnews_data(data_dir)
    print(f"原始数据大小: {len(raw_data)}")
    print(f"各类别分布: {raw_data['label'].value_counts()}")
    
    # 创建平衡数据集
    balanced_data = create_balanced_dataset(raw_data)
    print(f"平衡后数据大小: {len(balanced_data)}")
    print(f"平衡后各类别分布: {balanced_data['label'].value_counts()}")

    print("\n统一划分训练集、验证集、测试集...")
    train_df, temp_df = train_test_split(
        balanced_data,
        test_size=0.3,
        random_state=42,
        stratify=balanced_data['label']
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=42,
        stratify=temp_df['label']
    )

    print(f"训练集: {len(train_df)}, 验证集: {len(val_df)}, 测试集: {len(test_df)}")

    # 7. 保存 BERT 版本（原始文本，不做任何分词）
    print("\n保存 BERT 版本数据（原始文本）...")
    os.makedirs(bert_output_dir, exist_ok=True)
    train_df[['label', 'text']].to_csv(os.path.join(bert_output_dir, 'train.csv'), index=False, encoding='utf-8')
    val_df[['label', 'text']].to_csv(os.path.join(bert_output_dir, 'val.csv'), index=False, encoding='utf-8')
    test_df[['label', 'text']].to_csv(os.path.join(bert_output_dir, 'test.csv'), index=False, encoding='utf-8')

    # 8. 对传统模型版本进行分词和停用词过滤
    print("\n对传统模型版本进行 jieba 分词和停用词过滤...")
    stopwords = load_stopwords('./stopwords.txt')
    def preprocess_text_for_traditional(text):
        """对单条文本进行 jieba 分词 + 停用词过滤"""
        words = jieba.cut(str(text))
        filtered = [word for word in words if word.strip() and word not in stopwords]
        return ' '.join(filtered)

    # 应用预处理
    train_trad = train_df.copy()
    val_trad = val_df.copy()
    test_trad = test_df.copy()

    train_trad['text'] = train_trad['text'].apply(preprocess_text_for_traditional)
    val_trad['text'] = val_trad['text'].apply(preprocess_text_for_traditional)
    test_trad['text'] = test_trad['text'].apply(preprocess_text_for_traditional)

    # 9. 保存传统模型版本
    print("保存传统模型版本数据（分词后）...")
    os.makedirs(traditional_output_dir, exist_ok=True)
    train_trad.to_csv(os.path.join(traditional_output_dir, 'train.csv'), index=False, encoding='utf-8')
    val_trad.to_csv(os.path.join(traditional_output_dir, 'val.csv'), index=False, encoding='utf-8')
    test_trad.to_csv(os.path.join(traditional_output_dir, 'test.csv'), index=False, encoding='utf-8')
    
    print("数据预处理完成！")

if __name__ == "__main__":
    main()