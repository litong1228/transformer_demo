import pandas as pd
import numpy as np
import time
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import torch
import joblib

# 使用更轻量的中文预训练模型
MODEL_CHOICES = {
    'bert': './bert-base-chinese',
    'albert': './albert_chinese_base',  # 参数少，训练快
}

# 加载处理后的数据
def load_processed_data():
    train_data = pd.read_csv('data/bert_processed/train.csv')
    val_data = pd.read_csv('data/bert_processed/val.csv')
    test_data = pd.read_csv('data/bert_processed/test.csv')
    
    # 标签编码
    label_encoder = LabelEncoder()
    label_encoder.fit(train_data['label'])
    
    train_labels = label_encoder.transform(train_data['label'])
    val_labels = label_encoder.transform(val_data['label'])
    test_labels = label_encoder.transform(test_data['label'])

    for i, class_name in enumerate(label_encoder.classes_):
        print(f"{class_name} -> {i}")

    return train_data, val_data, test_data, \
           train_labels, val_labels, test_labels, label_encoder

# 准备数据集
def prepare_dataset(data, labels, tokenizer, max_length=128):
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=max_length)
    
    dataset = Dataset.from_dict({'text': data['text'].tolist(), 'label': labels.tolist()})
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset

# 计算评估指标
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average='weighted')
    return {'accuracy': accuracy, 'f1': f1}

# 新闻分类器类
class NewsClassifier:
    def __init__(self, model_name='albert'):
        self.model_name = model_name
        self.model_path = MODEL_CHOICES[model_name]
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = None
        self.label_encoder = None
    
    def train(self, train_data, train_labels, val_data, val_labels, label_encoder):
        self.label_encoder = label_encoder
        num_labels = len(label_encoder.classes_)
        
        # 加载模型
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path,
            num_labels=num_labels
        )
        
        # 准备数据集 - 增加序列长度以捕获更多上下文
        max_length = 256 if self.model_name == 'albert' else 512
        train_dataset = prepare_dataset(train_data, train_labels, self.tokenizer, max_length=max_length)
        val_dataset = prepare_dataset(val_data, val_labels, self.tokenizer, max_length=max_length)

        # 计算总训练步数用于warmup
        num_train_examples = len(train_dataset)
        per_device_batch_size = 8 if self.model_name == 'albert' else 4
        gradient_accumulation_steps = 4
        num_train_epochs = 1
        total_steps = (num_train_examples // (per_device_batch_size * gradient_accumulation_steps)) * num_train_epochs
        warmup_steps = int(0.1 * total_steps)
        
        # 训练参数 - 优化后的配置
        training_args = TrainingArguments(
            output_dir=f'./results/{self.model_name}',
            eval_strategy='epoch',
            save_strategy='epoch',
            learning_rate=3e-5 if self.model_name == 'albert' else 2e-5,
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
            logging_steps=100,
            fp16=True,
        )
        
        # 创建Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
        )
        
        # 训练
        start_time = time.time()
        trainer.train()
        train_time = time.time() - start_time
        
        return train_time
    
    def predict(self, text):
        max_length = 256 if self.model_name == 'albert' else 512
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
        return self.label_encoder.inverse_transform(predictions.numpy())[0]
    
    def save_model(self, path):
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        # 保存label_encoder以便后续使用
        if self.label_encoder is not None:
            joblib.dump(self.label_encoder, f'{path}/label_encoder.pkl')
            print(f"Label encoder已保存到: {path}/label_encoder.pkl")
    
    def load_model(self, path):
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)

# 评估Transformer模型
def evaluate_transformer_model(model, test_data, test_labels):
    start_time = time.time()
    
    # 准备测试数据集 - 使用与训练相同的max_length
    max_length = 256 if model.model_name == 'albert' else 512
    test_dataset = prepare_dataset(test_data, test_labels, model.tokenizer, max_length=max_length)
    
    # 创建Trainer进行评估
    trainer = Trainer(
        model=model.model,
        compute_metrics=compute_metrics,
        args=TrainingArguments(output_dir='./results', report_to='none', per_device_eval_batch_size=8 if model.model_name == 'albert' else 4)
    )
    
    # 评估
    eval_result = trainer.evaluate(test_dataset)
    
    inference_time = time.time() - start_time
    
    return {
        'accuracy': eval_result['eval_accuracy'],
        'f1': eval_result['eval_f1'],
        'inference_time': inference_time
    }

# 主函数
def main():
    # 加载数据
    train_data, val_data, test_data, train_labels, val_labels, test_labels, label_encoder = load_processed_data()
    
    # 训练BERT模型
    print("训练BERT模型...")
    bert_classifier = NewsClassifier(model_name='bert')
    bert_train_time = bert_classifier.train(train_data, train_labels, val_data, val_labels, label_encoder)
    
    # 训练ALBERT模型
    print("训练ALBERT模型...")
    albert_classifier = NewsClassifier(model_name='albert')
    albert_train_time = albert_classifier.train(train_data, train_labels, val_data, val_labels, label_encoder)
    
    # 评估模型
    print("评估BERT模型...")
    bert_results = evaluate_transformer_model(bert_classifier, test_data, test_labels)
    bert_results['train_time'] = bert_train_time
    
    print("评估ALBERT模型...")
    albert_results = evaluate_transformer_model(albert_classifier, test_data, test_labels)
    albert_results['train_time'] = albert_train_time
    
    # 保存结果
    results = pd.DataFrame({
        'BERT-base': bert_results,
        'ALBERT': albert_results
    })
    
    print("Transformer模型评估结果：")
    print(results)
    
    # 保存结果
    results.to_csv('results/transformer_models_results.csv')
    
    # 保存模型
    bert_classifier.save_model('./models/bert_news_classifier')
    albert_classifier.save_model('./models/albert_news_classifier')
    
    print("Transformer模型训练和评估完成！")

if __name__ == "__main__":
    main()