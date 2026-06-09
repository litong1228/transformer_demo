import pandas as pd
import numpy as np
import time
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, \
    confusion_matrix
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import torch
import torch.nn as nn
import torch.nn.functional as F
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import warnings
import argparse

warnings.filterwarnings('ignore')

# ============= 模型路径配置 =============
MODEL_CHOICES = {
    'bert': 'model/bert-base-chinese',
    'albert': 'model/albert-chinese-chinese',
    'bert_cnn': 'model/bert-base-chinese',
    'textcnn': 'model/bert-base-chinese',  # TextCNN使用相同的tokenizer
    'textrnn': 'model/bert-base-chinese',  # TextRNN使用相同的tokenizer
    'bert_textrnn': 'model/bert-base-chinese',  # BERT + TextRNN
}


# ============= BERT_TextRNN 模型定义 =============
class BertTextRNNForClassification(nn.Module):
    """BERT + TextRNN 混合模型"""

    def __init__(self, bert_model_name, num_labels,
                 hidden_dim=128, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        from transformers import AutoModel

        # BERT编码器
        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.hidden_size = self.bert.config.hidden_size  # BERT隐藏层维度: 768

        # TextRNN层（使用LSTM）
        self.lstm = nn.LSTM(
            input_size=self.hidden_size,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )

        # 池化层（最大值池化 + 平均池化，捕捉更多信息）
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)

        # 全连接层
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(lstm_output_dim * 2, num_labels)  # *2 因为拼接了最大池化和平均池化
        self.loss_fn = nn.CrossEntropyLoss()
        self.num_labels = num_labels

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        # BERT编码: (batch, seq_len) -> (batch, seq_len, hidden_size)
        bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = bert_outputs.last_hidden_state  # (batch, seq_len, 768)

        # LSTM层: (batch, seq_len, 768) -> (batch, seq_len, hidden_dim*2)
        lstm_out, (hidden, cell) = self.lstm(sequence_output)

        # 调整维度用于池化: (batch, seq_len, hidden_dim*2) -> (batch, hidden_dim*2, seq_len)
        lstm_out = lstm_out.permute(0, 2, 1)

        # 池化操作
        max_pooled = self.max_pool(lstm_out).squeeze(-1)  # (batch, hidden_dim*2)
        avg_pooled = self.avg_pool(lstm_out).squeeze(-1)  # (batch, hidden_dim*2)

        # 拼接最大池化和平均池化的结果
        pooled = torch.cat([max_pooled, avg_pooled], dim=1)  # (batch, hidden_dim*4)

        # Dropout + 分类
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)

        return {'loss': loss, 'logits': logits}


# ============= TextRNN 模型定义 =============
class TextRNNForClassification(nn.Module):
    """TextRNN文本分类模型 - 使用LSTM + 池化"""

    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_labels,
                 num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()

        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        # LSTM层
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )

        # 池化层（最大值池化 + 平均池化，捕捉更多信息）
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)

        # 全连接层
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(lstm_output_dim * 2, num_labels)  # *2 因为拼接了最大池化和平均池化
        self.loss_fn = nn.CrossEntropyLoss()
        self.num_labels = num_labels

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        # 词嵌入: (batch, seq_len) -> (batch, seq_len, embedding_dim)
        embedded = self.embedding(input_ids)

        # LSTM前向传播: (batch, seq_len, embedding_dim) -> (batch, seq_len, hidden_dim*2)
        lstm_out, (hidden, cell) = self.lstm(embedded)

        # 调整维度用于池化: (batch, seq_len, hidden_dim*2) -> (batch, hidden_dim*2, seq_len)
        lstm_out = lstm_out.permute(0, 2, 1)

        # 池化操作
        max_pooled = self.max_pool(lstm_out).squeeze(-1)  # (batch, hidden_dim*2)
        avg_pooled = self.avg_pool(lstm_out).squeeze(-1)  # (batch, hidden_dim*2)

        # 拼接最大池化和平均池化的结果
        pooled = torch.cat([max_pooled, avg_pooled], dim=1)  # (batch, hidden_dim*4)

        # Dropout + 分类
        pooled = self.dropout(pooled)
        logits = self.classifier(pooled)

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)

        return {'loss': loss, 'logits': logits}


# ============= TextCNN 模型定义 =============
class TextCNNForClassification(nn.Module):
    """纯CNN文本分类模型，不使用预训练BERT"""

    def __init__(self, vocab_size, embedding_dim, num_labels,
                 filter_sizes=[2, 3, 4], num_filters=128, dropout=0.3):
        super().__init__()

        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        # 多尺度卷积层
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim, out_channels=num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])

        # 池化层
        self.pool = nn.AdaptiveMaxPool1d(1)

        # 全连接层
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(num_filters * len(filter_sizes), num_labels)
        self.loss_fn = nn.CrossEntropyLoss()
        self.num_labels = num_labels

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        # 词嵌入: (batch, seq_len) -> (batch, seq_len, embedding_dim)
        embedded = self.embedding(input_ids)

        # 调整维度用于卷积: (batch, seq_len, embedding_dim) -> (batch, embedding_dim, seq_len)
        embedded = embedded.permute(0, 2, 1)

        # 卷积 + 池化
        conv_outputs = []
        for conv in self.convs:
            # 卷积: (batch, embedding_dim, seq_len) -> (batch, num_filters, seq_len - filter_size + 1)
            conv_out = F.relu(conv(embedded))
            # 池化: (batch, num_filters, seq_len) -> (batch, num_filters, 1)
            pooled = self.pool(conv_out).squeeze(-1)
            conv_outputs.append(pooled)

        # 拼接所有卷积核的输出
        combined = torch.cat(conv_outputs, dim=1)

        # Dropout + 分类
        combined = self.dropout(combined)
        logits = self.classifier(combined)

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)

        return {'loss': loss, 'logits': logits}


# ============= BERT_CNN 模型定义 =============
class BertCNNForClassification(nn.Module):
    def __init__(self, bert_model_name, num_labels, cnn_filters=128, kernel_sizes=[2, 3, 4]):
        super().__init__()
        from transformers import AutoModel
        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.hidden_size = self.bert.config.hidden_size

        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=self.hidden_size,
                      out_channels=cnn_filters,
                      kernel_size=k,
                      padding='same' if k % 2 == 0 else 'valid')
            for k in kernel_sizes
        ])

        self.pool = nn.AdaptiveMaxPool1d(1)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(cnn_filters * len(kernel_sizes), num_labels)
        self.loss_fn = nn.CrossEntropyLoss()
        self.num_labels = num_labels

    def forward(self, input_ids=None, attention_mask=None, labels=None, **kwargs):
        bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = bert_outputs.last_hidden_state.permute(0, 2, 1)

        cnn_outputs = []
        for conv in self.convs:
            conv_out = torch.relu(conv(sequence_output))
            pooled = self.pool(conv_out).squeeze(-1)
            cnn_outputs.append(pooled)

        combined = torch.cat(cnn_outputs, dim=1)
        combined = self.dropout(combined)
        logits = self.classifier(combined)

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)

        return {'loss': loss, 'logits': logits}


# ============= 指标记录器 =============
class MetricsRecorder:
    def __init__(self, save_dir='./training_metrics'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

        self.iterations = []
        self.train_losses = []
        self.train_accs = []
        self.val_losses = []
        self.val_accs = []
        self.learning_rates = []

    def add_train_metrics(self, step, loss, acc, lr=None):
        self.iterations.append(step)
        self.train_losses.append(loss)
        self.train_accs.append(acc)
        if lr is not None:
            self.learning_rates.append(lr)

    def add_val_metrics(self, val_loss, val_acc):
        self.val_losses.append(val_loss)
        self.val_accs.append(val_acc)

    def save_to_csv(self, model_name):
        # 确保所有列表长度一致
        max_len = len(self.iterations)
        val_losses_padded = self.val_losses + [None] * (max_len - len(self.val_losses))
        val_accs_padded = self.val_accs + [None] * (max_len - len(self.val_accs))
        lr_padded = self.learning_rates + [None] * (max_len - len(self.learning_rates))

        df = pd.DataFrame({
            'iteration': self.iterations,
            'train_loss': self.train_losses,
            'train_accuracy': self.train_accs,
            'val_loss': val_losses_padded,
            'val_accuracy': val_accs_padded,
            'learning_rate': lr_padded
        })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'{self.save_dir}/{model_name}_metrics_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"📊 指标已保存到: {filename}")
        return filename


# ============= 回调函数 =============
from transformers import TrainerCallback


class MetricsCallback(TrainerCallback):
    def __init__(self, recorder, eval_dataset, model, tokenizer, record_interval=10):
        self.recorder = recorder
        self.eval_dataset = eval_dataset
        self.model = model
        self.tokenizer = tokenizer
        self.record_interval = record_interval
        self.last_eval_step = 0
        self.current_step = 0
        self.current_batch_logits = None
        self.current_batch_labels = None

    def on_step_end(self, args, state, control, model=None, inputs=None, outputs=None, **kwargs):
        """每个step结束时调用，保存当前batch的信息"""
        if outputs is not None:
            if isinstance(outputs, dict):
                self.current_batch_logits = outputs.get('logits')
            else:
                self.current_batch_logits = outputs.logits if hasattr(outputs, 'logits') else None

            if inputs is not None and 'labels' in inputs:
                self.current_batch_labels = inputs['labels']

    def on_log(self, args, state, control, logs=None, **kwargs):
        """每个logging step调用"""
        if logs and 'loss' in logs:
            self.current_step = state.global_step
            lr = logs.get('learning_rate', None)

            # 计算训练准确率
            train_acc = 0.0
            if self.current_batch_logits is not None and self.current_batch_labels is not None:
                predictions = torch.argmax(self.current_batch_logits, dim=-1)
                train_acc = accuracy_score(
                    self.current_batch_labels.cpu().numpy(),
                    predictions.cpu().numpy()
                )

            # 每record_interval步记录一次
            if self.current_step % self.record_interval == 0:
                self.recorder.add_train_metrics(
                    self.current_step,
                    logs['loss'],
                    train_acc,
                    lr
                )

                # 每50步进行一次验证评估
                if self.current_step % 50 == 0:
                    self._evaluate_on_validation()

    def _evaluate_on_validation(self):
        """在验证集上评估 - 修复设备问题"""
        try:
            # 使用全部验证集的一个子集（500条）以提高速度
            val_size = min(500, len(self.eval_dataset))
            val_subset = self.eval_dataset.select(range(val_size))

            all_preds = []
            all_labels = []
            total_loss = 0

            batch_size = 32

            # ============= 修复1：正确获取设备 =============
            device = next(self.model.parameters()).device
            # ============================================

            for i in range(0, len(val_subset), batch_size):
                end_idx = min(i + batch_size, len(val_subset))
                batch = val_subset[i:end_idx]

                input_ids = torch.tensor(batch['input_ids']).to(device)
                attention_mask = torch.tensor(batch['attention_mask']).to(device)
                labels = torch.tensor(batch['label']).to(device)

                with torch.no_grad():
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

                    if isinstance(outputs, dict):
                        total_loss += outputs['loss'].item() * (end_idx - i)
                        logits = outputs['logits']
                    else:
                        total_loss += outputs.loss.item() * (end_idx - i)
                        logits = outputs.logits

                    preds = torch.argmax(logits, dim=-1)
                    all_preds.extend(preds.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())

            avg_loss = total_loss / len(val_subset)
            accuracy = accuracy_score(all_labels, all_preds)

            self.recorder.add_val_metrics(avg_loss, accuracy)
            print(f"\n📊 验证 at step {self.current_step}: Val Loss={avg_loss:.4f}, Val Acc={accuracy:.4f}")

        except Exception as e:
            print(f"⚠️ 验证评估失败: {e}")
            import traceback
            traceback.print_exc()


# ============= 数据加载 =============
def load_processed_data():
    train_data = pd.read_csv('model/data/bert_processed/train.csv')
    val_data = pd.read_csv('model/data/bert_processed/val.csv')
    test_data = pd.read_csv('model/data/bert_processed/test.csv')

    label_encoder = LabelEncoder()
    label_encoder.fit(train_data['label'])

    train_labels = label_encoder.transform(train_data['label'])
    val_labels = label_encoder.transform(val_data['label'])
    test_labels = label_encoder.transform(test_data['label'])

    print("\n📌 标签编码映射:")
    for i, class_name in enumerate(label_encoder.classes_):
        print(f"  {class_name} -> {i}")

    return train_data, val_data, test_data, train_labels, val_labels, test_labels, label_encoder


def prepare_dataset(data, labels, tokenizer, max_length=128):
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=max_length)

    dataset = Dataset.from_dict({'text': data['text'].tolist(), 'label': labels.tolist()})
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    return {'accuracy': accuracy, 'f1': f1}


# ============= 新闻分类器类 =============
class NewsClassifier:
    def __init__(self, model_name='albert'):
        self.model_name = model_name
        self.model_path = MODEL_CHOICES[model_name]
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = None
        self.label_encoder = None
        self.recorder = MetricsRecorder()
        self.is_bert_cnn = (model_name == 'bert_cnn')
        self.is_textcnn = (model_name == 'textcnn')
        self.is_textrnn = (model_name == 'textrnn')
        self.is_bert_textrnn = (model_name == 'bert_textrnn')
        self.training_completed = False

    def train(self, train_data, train_labels, val_data, val_labels, label_encoder, resume_from_checkpoint=None):
        self.label_encoder = label_encoder
        num_labels = len(label_encoder.classes_)

        # 准备数据集（所有模型使用相同的tokenizer）
        max_length = 256 if self.model_name in ['albert', 'bert_cnn', 'textcnn', 'textrnn', 'bert_textrnn'] else 512
        train_dataset = prepare_dataset(train_data, train_labels, self.tokenizer, max_length=max_length)
        val_dataset = prepare_dataset(val_data, val_labels, self.tokenizer, max_length=max_length)

        # 加载模型
        if self.is_bert_textrnn:
            print(f"  📦 加载 BERT_TextRNN 模型（BERT + LSTM + 池化）")
            self.model = BertTextRNNForClassification(
                bert_model_name=self.model_path,
                num_labels=num_labels,
                hidden_dim=128,
                num_layers=2,
                dropout=0.3,
                bidirectional=True
            )
            # BERT_TextRNN训练参数
            learning_rate = 2e-5  # BERT部分需要小学习率
            per_device_batch_size = 8
            gradient_accumulation_steps = 4
            num_train_epochs = 3
            fp16 = True  # 使用混合精度加速

        elif self.is_textrnn:
            print(f"  📦 加载 TextRNN 模型（LSTM + 池化）")
            vocab_size = self.tokenizer.vocab_size
            embedding_dim = 256  # 词向量维度
            hidden_dim = 128  # LSTM隐藏层维度
            self.model = TextRNNForClassification(
                vocab_size=vocab_size,
                embedding_dim=embedding_dim,
                hidden_dim=hidden_dim,
                num_labels=num_labels,
                num_layers=2,
                dropout=0.3,
                bidirectional=True
            )
            # TextRNN训练参数
            learning_rate = 1e-3
            per_device_batch_size = 32
            gradient_accumulation_steps = 2
            num_train_epochs = 10  # TextRNN需要更多epoch
            fp16 = False  # TextRNN不需要混合精度

        elif self.is_textcnn:
            print(f"  📦 加载 TextCNN 模型（纯CNN）")
            vocab_size = self.tokenizer.vocab_size
            embedding_dim = 256
            self.model = TextCNNForClassification(
                vocab_size=vocab_size,
                embedding_dim=embedding_dim,
                num_labels=num_labels,
                filter_sizes=[2, 3, 4],
                num_filters=128,
                dropout=0.3
            )
            learning_rate = 1e-3
            per_device_batch_size = 32
            gradient_accumulation_steps = 2
            num_train_epochs = 10
            fp16 = False

        elif self.is_bert_cnn:
            print(f"  📦 加载 BERT_CNN 模型")
            self.model = BertCNNForClassification(
                bert_model_name=self.model_path,
                num_labels=num_labels,
                cnn_filters=128,
                kernel_sizes=[2, 3, 4]
            )
            learning_rate = 2e-5
            per_device_batch_size = 8
            gradient_accumulation_steps = 4
            num_train_epochs = 3
            fp16 = True

        else:
            # BERT或ALBERT
            print(f"  📦 加载 {self.model_name.upper()} 模型")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path,
                num_labels=num_labels
            )
            learning_rate = 3e-5 if self.model_name == 'albert' else 2e-5
            per_device_batch_size = 8 if self.model_name == 'albert' else 4
            gradient_accumulation_steps = 4
            num_train_epochs = 3
            fp16 = True

        # 计算训练参数
        num_train_examples = len(train_dataset)
        total_steps = (num_train_examples // (per_device_batch_size * gradient_accumulation_steps)) * num_train_epochs
        warmup_steps = int(0.1 * total_steps)

        # 训练参数
        training_args = TrainingArguments(
            output_dir=f'./results/{self.model_name}',
            eval_strategy='steps',
            eval_steps=50,
            save_strategy='steps',
            save_steps=500,
            logging_steps=10,
            learning_rate=learning_rate,
            per_device_train_batch_size=per_device_batch_size,
            per_device_eval_batch_size=per_device_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            num_train_epochs=num_train_epochs,
            weight_decay=0.01,
            warmup_steps=warmup_steps,
            load_best_model_at_end=True,
            metric_for_best_model='accuracy',
            greater_is_better=True,
            save_total_limit=2,
            report_to='none',
            disable_tqdm=False,
            fp16=fp16,
            remove_unused_columns=False,
            logging_dir='./logs',
        )

        # 创建Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
            callbacks=[MetricsCallback(
                self.recorder,
                val_dataset,
                self.model,
                self.tokenizer,
                record_interval=10
            )]
        )

        # 训练
        print(f"\n🚀 开始训练 {self.model_name.upper()} 模型...")
        start_time = time.time()

        # 根据是否有resume_from_checkpoint参数决定是否恢复训练
        if resume_from_checkpoint:
            print(f"🔄 从检查点恢复训练: {resume_from_checkpoint}")
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        else:
            trainer.train()

        train_time = time.time() - start_time

        # 保存指标
        csv_file = self.recorder.save_to_csv(self.model_name)
        print(f"✅ 训练完成，指标已保存到: {csv_file}")

        self.training_completed = True
        return train_time

    def save_model(self, path):
        """保存模型"""
        os.makedirs(path, exist_ok=True)

        if self.is_bert_textrnn:
            torch.save(self.model.state_dict(), f'{path}/pytorch_model.bin')
            config = {
                'model_type': 'bert_textrnn',
                'num_labels': len(self.label_encoder.classes_),
                'hidden_dim': 128,
                'num_layers': 2,
                'dropout': 0.3,
                'bidirectional': True,
                'bert_model_name': self.model_path
            }
            joblib.dump(config, f'{path}/config.pkl')
            self.tokenizer.save_pretrained(path)
            print(f"✅ BERT_TextRNN 模型已保存到: {path}")

        elif self.is_textrnn:
            torch.save(self.model.state_dict(), f'{path}/pytorch_model.bin')
            config = {
                'model_type': 'textrnn',
                'num_labels': len(self.label_encoder.classes_),
                'vocab_size': self.tokenizer.vocab_size,
                'embedding_dim': 256,
                'hidden_dim': 128,
                'num_layers': 2,
                'dropout': 0.3,
                'bidirectional': True
            }
            joblib.dump(config, f'{path}/config.pkl')
            self.tokenizer.save_pretrained(path)
            print(f"✅ TextRNN 模型已保存到: {path}")

        elif self.is_textcnn:
            torch.save(self.model.state_dict(), f'{path}/pytorch_model.bin')
            config = {
                'model_type': 'textcnn',
                'num_labels': len(self.label_encoder.classes_),
                'vocab_size': self.tokenizer.vocab_size,
                'embedding_dim': 256,
                'filter_sizes': [2, 3, 4],
                'num_filters': 128,
                'dropout': 0.3
            }
            joblib.dump(config, f'{path}/config.pkl')
            self.tokenizer.save_pretrained(path)
            print(f"✅ TextCNN 模型已保存到: {path}")

        elif self.is_bert_cnn:
            torch.save(self.model.state_dict(), f'{path}/pytorch_model.bin')
            config = {
                'model_type': 'bert_cnn',
                'num_labels': len(self.label_encoder.classes_),
                'cnn_filters': 128,
                'kernel_sizes': [2, 3, 4],
                'bert_model_name': self.model_path
            }
            joblib.dump(config, f'{path}/config.pkl')
            self.tokenizer.save_pretrained(path)
            print(f"✅ BERT_CNN 模型已保存到: {path}")

        else:
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            print(f"✅ {self.model_name.upper()} 模型已保存到: {path}")

        if self.label_encoder is not None:
            joblib.dump(self.label_encoder, f'{path}/label_encoder.pkl')
            print(f"✅ 标签编码器已保存到: {path}/label_encoder.pkl")

    def evaluate(self, test_data, test_labels):
        """评估模型并生成详细报告"""
        print(f"\n🔍 开始评估 {self.model_name.upper()} 模型...")
        start_time = time.time()

        max_length = 256 if self.model_name in ['albert', 'bert_cnn', 'textcnn', 'textrnn', 'bert_textrnn'] else 512
        test_dataset = prepare_dataset(test_data, test_labels, self.tokenizer, max_length=max_length)

        device = next(self.model.parameters()).device
        print(f"📟 使用设备: {device}")

        all_predictions = []
        all_labels = []

        batch_size = 32
        for i in range(0, len(test_dataset), batch_size):
            batch = test_dataset[i:i + batch_size]

            input_ids = torch.tensor(batch['input_ids']).to(device)
            attention_mask = torch.tensor(batch['attention_mask']).to(device)
            labels = torch.tensor(batch['label']).to(device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

                if isinstance(outputs, dict):
                    logits = outputs['logits']
                else:
                    logits = outputs.logits

                predictions = torch.argmax(logits, dim=-1)
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        # 计算指标
        accuracy = accuracy_score(all_labels, all_predictions)

        # 生成详细的分类报告
        class_names = self.label_encoder.classes_
        report = classification_report(
            all_labels,
            all_predictions,
            target_names=class_names,
            digits=4
        )

        # 绘制混淆矩阵
        self.plot_confusion_matrix(all_labels, all_predictions, class_names)

        inference_time = time.time() - start_time

        # 打印详细报告
        print("\n" + "=" * 60)
        print("📋 每个类别的详细指标:")
        print("=" * 60)
        print(report)
        print("=" * 60)
        print(f"🎯 总体准确率: {accuracy:.4f} ({accuracy * 100:.2f}%)")
        print(f"⏱️ 推理时间: {inference_time:.2f}秒")

        # 保存报告到文件
        os.makedirs('./results', exist_ok=True)
        report_path = f'./results/{self.model_name}_classification_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 分类报告已保存到: {report_path}")

        return {
            'accuracy': accuracy,
            'inference_time': inference_time,
            'predictions': all_predictions,
            'true_labels': all_labels
        }

    def plot_confusion_matrix(self, y_true, y_pred, labels, save_dir='./confusion_matrices'):
        """绘制混淆矩阵"""
        os.makedirs(save_dir, exist_ok=True)

        cm = confusion_matrix(y_true, y_pred)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        fig, axes = plt.subplots(1, 2, figsize=(20, 8))

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 数值混淆矩阵
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=labels, yticklabels=labels, ax=axes[0])
        axes[0].set_title(f'{self.model_name.upper()} - Confusion Matrix (Counts)', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Predicted Label', fontsize=12)
        axes[0].set_ylabel('True Label', fontsize=12)
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].tick_params(axis='y', rotation=45)

        # 比例混淆矩阵
        sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='YlOrRd',
                    xticklabels=labels, yticklabels=labels, ax=axes[1])
        axes[1].set_title(f'{self.model_name.upper()} - Confusion Matrix (Proportions)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Predicted Label', fontsize=12)
        axes[1].set_ylabel('True Label', fontsize=12)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].tick_params(axis='y', rotation=45)

        plt.suptitle(f'{self.model_name.upper()} Classification Results', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'{save_dir}/{self.model_name}_confusion_matrix_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 混淆矩阵已保存到: {filename}")
        plt.close()


# ============= 主函数 =============
def main():
    print("=" * 70)
    print("🔰 开始模型训练与评估")
    print("=" * 70)

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='bert_cnn',
                        choices=['bert', 'albert', 'bert_cnn', 'textcnn', 'textrnn', 'bert_textrnn', 'all'],
                        help='选择要训练的模型')
    parser.add_argument('--no-prompt', action='store_true', help='直接全部训练')
    # 添加断点续训参数
    parser.add_argument('--resume_from_checkpoint', type=str, default=None,
                        help='从指定检查点恢复训练，可以是True（自动找最新）或具体路径（如./results/bert/checkpoint-750）')
    args = parser.parse_args()

    # 确定要训练的模型
    if args.model == 'all':
        models_to_train = ['bert', 'albert', 'bert_cnn', 'textcnn', 'textrnn', 'bert_textrnn']
    else:
        models_to_train = [args.model]
    print(f"\n🎯 将训练模型: {models_to_train}")

    # 显示是否从检查点恢复
    if args.resume_from_checkpoint:
        print(f"🔄 将从检查点恢复训练: {args.resume_from_checkpoint}")

    # 创建目录
    for dir_name in ['./training_metrics', './models', './results', './confusion_matrices', './logs']:
        os.makedirs(dir_name, exist_ok=True)

    # 加载数据
    train_data, val_data, test_data, train_labels, val_labels, test_labels, label_encoder = load_processed_data()

    print(f"\n📊 数据统计:")
    print(f"  训练集: {len(train_data)} 条")
    print(f"  验证集: {len(val_data)} 条")
    print(f"  测试集: {len(test_data)} 条")
    print(f"  类别数: {len(label_encoder.classes_)}")

    all_results = {}
    model_configs = {
        'bert': {'name': 'BERT', 'color': '🔵'},
        'albert': {'name': 'ALBERT', 'color': '🟢'},
        'bert_cnn': {'name': 'BERT_CNN', 'color': '🟠'},
        'textcnn': {'name': 'TextCNN', 'color': '🟣'},
        'textrnn': {'name': 'TextRNN', 'color': '🔴'},
        'bert_textrnn': {'name': 'BERT_TextRNN', 'color': '🟡'}
    }

    for i, model_key in enumerate(models_to_train):
        model_info = model_configs[model_key]
        print("\n" + "=" * 70)
        print(f"{model_info['color']} [{i + 1}/{len(models_to_train)}] 训练 {model_info['name']} 模型...")
        print("=" * 70)

        # 训练新模型
        classifier = NewsClassifier(model_name=model_key)
        # 传递resume_from_checkpoint参数
        train_time = classifier.train(
            train_data,
            train_labels,
            val_data,
            val_labels,
            label_encoder,
            resume_from_checkpoint=args.resume_from_checkpoint
        )

        # 保存模型
        model_save_path = f'./models/{model_key}_news_classifier'
        classifier.save_model(model_save_path)

        # 评估模型
        results = classifier.evaluate(test_data, test_labels)
        results['train_time'] = train_time
        all_results[model_info['name']] = results

        # 如果不是最后一个模型，询问是否继续
        if i < len(models_to_train) - 1 and not args.no_prompt:
            next_model = model_configs[models_to_train[i + 1]]['name']
            user_input = input(f"\n⏸️ 继续训练 {next_model}? (y/n): ").lower()
            if user_input != 'y':
                print("🛑 训练已暂停")
                break

    # 输出结果对比
    if len(all_results) > 0:
        print("\n" + "=" * 70)
        print("📊 模型评估结果：")
        print("=" * 70)
        for model_name, results in all_results.items():
            train_time = results.get('train_time', 0)
            print(
                f"{model_name}: 准确率={results['accuracy']:.4f}, 训练时间={train_time:.2f}s, 推理时间={results.get('inference_time', 0):.2f}s")

    print("\n✅ 程序执行完成！")


if __name__ == "__main__":
    main()