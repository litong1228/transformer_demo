import pandas as pd
import numpy as np
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import LabelEncoder
import os


# ============= FastText 模型定义 =============
class FastText(nn.Module):
    """
    FastText文本分类模型
    核心思想：词嵌入 + 平均池化
    """

    def __init__(self, vocab_size, embedding_dim, num_classes, dropout=0.5):
        super(FastText, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(embedding_dim, num_classes)

    def forward(self, x):
        # 词嵌入: (batch, seq_len) -> (batch, seq_len, embedding_dim)
        embedded = self.embedding(x)

        # 平均池化: 对所有词向量取平均
        # (batch, seq_len, embedding_dim) -> (batch, embedding_dim)
        pooled = torch.mean(embedded, dim=1)

        # Dropout + 分类
        pooled = self.dropout(pooled)
        logits = self.fc(pooled)

        return logits


# 加载处理后的数据
def load_processed_data():
    train_data = pd.read_csv('data/processed/train.csv')
    val_data = pd.read_csv('data/processed/val.csv')
    test_data = pd.read_csv('data/processed/test.csv')

    # 标签编码（字符标签映射成数字编码）
    label_encoder = LabelEncoder()
    label_encoder.fit(train_data['label'])

    train_labels = label_encoder.transform(train_data['label'])
    val_labels = label_encoder.transform(val_data['label'])
    test_labels = label_encoder.transform(test_data['label'])

    return train_data['text'], val_data['text'], test_data['text'], \
        train_labels, val_labels, test_labels, label_encoder


# 基准模型1：TF-IDF + 逻辑回归
def train_tfidf_logreg(X_train, y_train):
    # 特征提取
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 1))
    X_train_tfidf = vectorizer.fit_transform(X_train)

    # 训练模型
    start_time = time.time()
    model = LogisticRegression(max_iter=100, n_jobs=-1)
    model.fit(X_train_tfidf, y_train)
    train_time = time.time() - start_time

    return model, vectorizer, train_time


# 基准模型2：TF-IDF + SVM
def train_tfidf_svm(X_train, y_train):
    # 特征提取
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 1))
    X_train_tfidf = vectorizer.fit_transform(X_train)

    # 训练模型
    start_time = time.time()
    from sklearn.svm import LinearSVC
    model = LinearSVC(C=1.0, max_iter=100, dual=True)
    model.fit(X_train_tfidf, y_train)
    train_time = time.time() - start_time

    return model, vectorizer, train_time


# TextCNN模型定义
class TextCNN(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_classes, filter_sizes=[3, 4, 5], num_filters=128):
        super(TextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.convs = nn.ModuleList([
            nn.Conv2d(1, num_filters, (fs, embedding_dim)) for fs in filter_sizes
        ])
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(len(filter_sizes) * num_filters, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        x = x.unsqueeze(1)
        x = [torch.relu(conv(x)).squeeze(3) for conv in self.convs]
        x = [torch.max_pool1d(conv_out, conv_out.size(2)).squeeze(2) for conv_out in x]
        x = torch.cat(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        return x


# 文本数据集类
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=100):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        # 文本分词和编码
        tokens = text.split()[:self.max_length]
        token_ids = [self.tokenizer.get(word, 0) for word in tokens]
        token_ids = token_ids + [0] * (self.max_length - len(token_ids))

        return torch.tensor(token_ids), torch.tensor(label, dtype=torch.long)


# 构建词汇表
def build_vocab(texts, max_vocab_size=50000):
    word_counts = {}
    for text in texts:
        for word in text.split():
            word_counts[word] = word_counts.get(word, 0) + 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    vocab = {word: idx + 1 for idx, (word, _) in enumerate(sorted_words[:max_vocab_size])}
    vocab['<PAD>'] = 0

    return vocab


# 训练TextCNN模型
def train_textcnn(X_train, y_train, X_val, y_val):
    # 构建词汇表
    vocab = build_vocab(X_train)
    vocab_size = len(vocab)

    # 准备数据集
    train_dataset = TextDataset(X_train, y_train, vocab)
    val_dataset = TextDataset(X_val, y_val, vocab)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    # 初始化模型
    embedding_dim = 128
    num_classes = len(set(y_train))
    model = TextCNN(vocab_size, embedding_dim, num_classes)

    # 训练参数
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    # 训练模型
    start_time = time.time()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    best_val_acc = 0.0
    best_model = None

    for epoch in range(10):
        model.train()
        train_loss = 0.0
        for batch_texts, batch_labels in train_loader:
            batch_texts, batch_labels = batch_texts.to(device), batch_labels.to(device)

            optimizer.zero_grad()
            outputs = model(batch_texts)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # 验证
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for batch_texts, batch_labels in val_loader:
                batch_texts, batch_labels = batch_texts.to(device), batch_labels.to(device)
                outputs = model(batch_texts)
                _, predicted = torch.max(outputs.data, 1)
                val_total += batch_labels.size(0)
                val_correct += (predicted == batch_labels).sum().item()

        val_acc = val_correct / val_total
        print(f'Epoch {epoch + 1}, Train Loss: {train_loss / len(train_loader):.4f}, Val Acc: {val_acc:.4f}')

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model = model.state_dict()

    train_time = time.time() - start_time

    # 加载最佳模型
    model.load_state_dict(best_model)

    return model, vocab, train_time


# ============= 训练 FastText 模型 =============
def train_fasttext(X_train, y_train, X_val, y_val):
    """训练FastText模型"""
    # 构建词汇表
    vocab = build_vocab(X_train)
    vocab_size = len(vocab)

    # 准备数据集
    train_dataset = TextDataset(X_train, y_train, vocab)
    val_dataset = TextDataset(X_val, y_val, vocab)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    # 初始化模型
    embedding_dim = 128
    num_classes = len(set(y_train))
    model = FastText(vocab_size, embedding_dim, num_classes, dropout=0.5)

    # 训练参数
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    # 训练模型
    start_time = time.time()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    best_val_acc = 0.0
    best_model = None

    for epoch in range(10):
        model.train()
        train_loss = 0.0
        for batch_texts, batch_labels in train_loader:
            batch_texts, batch_labels = batch_texts.to(device), batch_labels.to(device)

            optimizer.zero_grad()
            outputs = model(batch_texts)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # 验证
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for batch_texts, batch_labels in val_loader:
                batch_texts, batch_labels = batch_texts.to(device), batch_labels.to(device)
                outputs = model(batch_texts)
                _, predicted = torch.max(outputs.data, 1)
                val_total += batch_labels.size(0)
                val_correct += (predicted == batch_labels).sum().item()

        val_acc = val_correct / val_total
        print(f'Epoch {epoch + 1}, Train Loss: {train_loss / len(train_loader):.4f}, Val Acc: {val_acc:.4f}')

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model = model.state_dict()

    train_time = time.time() - start_time

    # 加载最佳模型
    model.load_state_dict(best_model)
    print(f"\n最佳验证准确率: {best_val_acc:.4f}")

    return model, vocab, train_time


def evaluate_fasttext(model, vocab, X_test, y_test):
    """评估FastText模型"""
    start_time = time.time()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    y_pred = []
    with torch.no_grad():
        for text in X_test:
            tokens = text.split()[:100]
            token_ids = [vocab.get(word, 0) for word in tokens]
            token_ids = token_ids + [0] * (100 - len(token_ids))
            input_tensor = torch.tensor(token_ids).unsqueeze(0).to(device)
            output = model(input_tensor)
            _, predicted = torch.max(output.data, 1)
            y_pred.append(predicted.item())

    inference_time = time.time() - start_time

    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred, average='weighted'),
        'inference_time': inference_time
    }


def train_fasttext_only():
    """只训练FastText模型"""
    print("=" * 70)
    print("🔰 FastText 模型训练")
    print("=" * 70)

    # 创建目录
    os.makedirs('./results', exist_ok=True)

    # 加载数据
    print("\n📂 加载数据...")
    X_train, X_val, X_test, y_train, y_val, y_test, label_encoder = load_processed_data()

    print(f"\n📊 数据统计:")
    print(f"  训练集: {len(X_train)} 条")
    print(f"  验证集: {len(X_val)} 条")
    print(f"  测试集: {len(X_test)} 条")
    print(f"  类别数: {len(label_encoder.classes_)}")

    # 训练FastText
    print("\n" + "=" * 70)
    print("📌 训练 FastText 模型...")
    print("=" * 70)
    fasttext_model, fasttext_vocab, fasttext_time = train_fasttext(X_train, y_train, X_val, y_val)

    # 评估模型
    print("\n📊 评估 FastText 模型...")
    results = evaluate_fasttext(fasttext_model, fasttext_vocab, X_test, y_test)

    # 打印结果
    print("\n" + "=" * 70)
    print("📊 FastText 模型评估结果：")
    print("=" * 70)
    print(f"准确率: {results['accuracy']:.4f} ({results['accuracy'] * 100:.2f}%)")
    print(f"F1分数: {results['f1']:.4f}")
    print(f"训练时间: {fasttext_time:.2f}秒")
    print(f"推理时间: {results['inference_time']:.2f}秒")

    # 保存结果
    results_df = pd.DataFrame([results])
    results_df['train_time'] = fasttext_time
    results_df.to_csv('./results/fasttext_results.csv', index=False)
    print("\n✅ 结果已保存到: ./results/fasttext_results.csv")

    return fasttext_model, fasttext_vocab, label_encoder


# 统一评估框架
def evaluate_all_models(models_dict, X_test, y_test):
    results = {}

    for name, (model, vectorizer_or_vocab) in models_dict.items():
        start_time = time.time()

        if name in ['TF-IDF+LogReg', 'TF-IDF+SVM']:
            # TF-IDF模型评估
            vectorizer = vectorizer_or_vocab
            X_test_tfidf = vectorizer.transform(X_test)
            y_pred = model.predict(X_test_tfidf)
        else:
            # TextCNN模型评估
            vocab = vectorizer_or_vocab
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.to(device)
            model.eval()

            y_pred = []
            with torch.no_grad():
                for text in X_test:
                    tokens = text.split()[:100]
                    token_ids = [vocab.get(word, 0) for word in tokens]
                    token_ids = token_ids + [0] * (100 - len(token_ids))
                    input_tensor = torch.tensor(token_ids).unsqueeze(0).to(device)
                    output = model(input_tensor)
                    _, predicted = torch.max(output.data, 1)
                    y_pred.append(predicted.item())

        inference_time = time.time() - start_time

        results[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred, average='weighted'),
            'inference_time': inference_time
        }

    return pd.DataFrame(results)


# 主函数（训练所有模型）
def main():
    # 加载数据
    X_train, X_val, X_test, y_train, y_val, y_test, label_encoder = load_processed_data()

    # 训练TF-IDF + 逻辑回归
    print("训练TF-IDF + 逻辑回归模型...")
    logreg_model, logreg_vectorizer, logreg_time = train_tfidf_logreg(X_train, y_train)

    # 训练TF-IDF + SVM
    print("训练TF-IDF + SVM模型...")
    svm_model, svm_vectorizer, svm_time = train_tfidf_svm(X_train, y_train)

    # 训练TextCNN
    print("训练TextCNN模型...")
    textcnn_model, textcnn_vocab, textcnn_time = train_textcnn(X_train, y_train, X_val, y_val)

    # 构建模型字典
    models_dict = {
        'TF-IDF+LogReg': (logreg_model, logreg_vectorizer),
        'TF-IDF+SVM': (svm_model, svm_vectorizer),
        'TextCNN': (textcnn_model, textcnn_vocab)
    }

    # 评估所有模型
    print("评估所有模型...")
    results = evaluate_all_models(models_dict, X_test, y_test)

    # 添加训练时间
    results.loc['train_time'] = {
        'TF-IDF+LogReg': logreg_time,
        'TF-IDF+SVM': svm_time,
        'TextCNN': textcnn_time
    }

    print("模型评估结果：")
    print(results)

    # 保存结果
    results.to_csv('results/traditional_models_results.csv')

    print("传统模型训练和评估完成！")


if __name__ == "__main__":
    import sys

    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--fasttext':
        # 只训练FastText
        train_fasttext_only()
    else:
        # 默认运行原有主函数（训练所有模型）
        main()