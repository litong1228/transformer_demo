import os
import joblib

# torch / transformers 加载失败(如 Windows pagefile 不足)时,不阻塞 Django 启动。
# 真正用模型时再报错。
_TORCH_IMPORT_ERROR = None
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from transformers import (
        BertTokenizer,
        AlbertForSequenceClassification,
        BertForSequenceClassification,
        AutoModel,
    )
    _TORCH_AVAILABLE = True
except Exception as _e:
    _TORCH_IMPORT_ERROR = _e
    _TORCH_AVAILABLE = False
    # 提供桩对象, 让模块顶层的 class 定义不报 NameError
    class _StubModule:
        class Module: pass
        Embedding = Conv1d = LSTM = AdaptiveMaxPool1d = AdaptiveAvgPool1d = Dropout = Linear = ModuleList = object
    torch = _StubModule()
    torch.nn = _StubModule()
    nn = _StubModule()
    F = _StubModule()
    BertTokenizer = AlbertForSequenceClassification = BertForSequenceClassification = AutoModel = None

# ============ Paths ============
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
HF_MODELS_DIR = os.path.join(project_root, 'model', 'models')
CUSTOM_MODELS_DIR = os.path.join(project_root, 'models')
BERT_BASE_PATH = os.path.join(project_root, 'model', 'bert-base-chinese')

DEFAULT_LABEL_MAP = {
    0: '体育', 1: '娱乐', 2: '家居', 3: '房产', 4: '教育',
    5: '时尚', 6: '时政', 7: '游戏', 8: '科技', 9: '财经',
}


# ============ Custom architecture definitions ============
# 与 model/3_transformer_models.py 一致

class TextCNNForClassification(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_labels,
                 filter_sizes=(2, 3, 4), num_filters=128, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim, out_channels=num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        self.pool = nn.AdaptiveMaxPool1d(1)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(num_filters * len(filter_sizes), num_labels)

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        embedded = self.embedding(input_ids).permute(0, 2, 1)
        conv_outputs = []
        for conv in self.convs:
            conv_out = F.relu(conv(embedded))
            pooled = self.pool(conv_out).squeeze(-1)
            conv_outputs.append(pooled)
        combined = torch.cat(conv_outputs, dim=1)
        combined = self.dropout(combined)
        return {'logits': self.classifier(combined)}


class TextRNNForClassification(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_labels,
                 num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim, hidden_size=hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(lstm_output_dim * 2, num_labels)

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        embedded = self.embedding(input_ids)
        lstm_out, _ = self.lstm(embedded)
        lstm_out = lstm_out.permute(0, 2, 1)
        max_pooled = self.max_pool(lstm_out).squeeze(-1)
        avg_pooled = self.avg_pool(lstm_out).squeeze(-1)
        pooled = torch.cat([max_pooled, avg_pooled], dim=1)
        pooled = self.dropout(pooled)
        return {'logits': self.classifier(pooled)}


class BertCNNForClassification(nn.Module):
    def __init__(self, bert_model_name, num_labels, cnn_filters=128, kernel_sizes=(2, 3, 4)):
        super().__init__()
        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.hidden_size = self.bert.config.hidden_size
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=self.hidden_size, out_channels=cnn_filters,
                      kernel_size=k, padding='same' if k % 2 == 0 else 'valid')
            for k in kernel_sizes
        ])
        self.pool = nn.AdaptiveMaxPool1d(1)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(cnn_filters * len(kernel_sizes), num_labels)

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        seq = bert_outputs.last_hidden_state.permute(0, 2, 1)
        cnn_outputs = []
        for conv in self.convs:
            conv_out = torch.relu(conv(seq))
            pooled = self.pool(conv_out).squeeze(-1)
            cnn_outputs.append(pooled)
        combined = torch.cat(cnn_outputs, dim=1)
        combined = self.dropout(combined)
        return {'logits': self.classifier(combined)}


class BertTextRNNForClassification(nn.Module):
    def __init__(self, bert_model_name, num_labels,
                 hidden_dim=128, num_layers=2, dropout=0.3, bidirectional=True):
        super().__init__()
        self.bert = AutoModel.from_pretrained(bert_model_name)
        self.hidden_size = self.bert.config.hidden_size
        self.lstm = nn.LSTM(
            input_size=self.hidden_size, hidden_size=hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(lstm_output_dim * 2, num_labels)

    def forward(self, input_ids=None, attention_mask=None, **kwargs):
        bert_outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        seq = bert_outputs.last_hidden_state
        lstm_out, _ = self.lstm(seq)
        lstm_out = lstm_out.permute(0, 2, 1)
        max_pooled = self.max_pool(lstm_out).squeeze(-1)
        avg_pooled = self.avg_pool(lstm_out).squeeze(-1)
        pooled = torch.cat([max_pooled, avg_pooled], dim=1)
        pooled = self.dropout(pooled)
        return {'logits': self.classifier(pooled)}


# ============ Model registry ============

MODEL_REGISTRY = {
    'bert_cnn': {
        'name': 'BERT-CNN',
        'display_name': 'BERT + CNN',
        'description': 'BERT 编码 + 多尺度一维卷积，结合上下文表征与局部 n-gram 特征。对比实验中准确率最高，作为默认模型。',
        'kind': 'custom',
        'path': os.path.join(CUSTOM_MODELS_DIR, 'bert_cnn_news_classifier'),
        'badge': '★ 推荐',
        'tag': 'accent',
        'test_accuracy': 97.76,
    },
    'bert_textrnn': {
        'name': 'BERT-TextRNN',
        'display_name': 'BERT + BiLSTM',
        'description': 'BERT 编码 + 双向 LSTM，擅长建模序列长距依赖关系，准确率与 BERT-CNN 接近。',
        'kind': 'custom',
        'path': os.path.join(CUSTOM_MODELS_DIR, 'bert_textrnn_news_classifier'),
        'badge': '混合架构',
        'tag': 'navy',
        'test_accuracy': 97.69,
    },
    'bert': {
        'name': 'BERT',
        'display_name': 'BERT 中文',
        'description': '标准 BERT-base 模型，参数量较大、表征能力强，作为经典基线模型。',
        'kind': 'hf',
        'path': os.path.join(HF_MODELS_DIR, 'bert_news_classifier'),
        'hf_class': BertForSequenceClassification,
        'badge': '经典基线',
        'tag': 'navy',
        'test_accuracy': 97.15,
    },
    'albert': {
        'name': 'ALBERT',
        'display_name': 'ALBERT 中文',
        'description': '轻量级 Transformer，参数少、推理快、内存占用低，适合实时场景。',
        'kind': 'hf',
        'path': os.path.join(HF_MODELS_DIR, 'albert_news_classifier'),
        'hf_class': AlbertForSequenceClassification,
        'badge': '速度优先',
        'tag': 'success',
        'test_accuracy': 95.35,
    },
    'textcnn': {
        'name': 'TextCNN',
        'display_name': 'TextCNN',
        'description': '纯 CNN 文本分类（无预训练），训练快、推理极快，适合资源受限场景。',
        'kind': 'custom',
        'path': os.path.join(CUSTOM_MODELS_DIR, 'textcnn_news_classifier'),
        'badge': '极速基线',
        'tag': 'warning',
        'test_accuracy': 94.80,
    },
    'textrnn': {
        'name': 'TextRNN',
        'display_name': 'TextRNN',
        'description': '纯 BiLSTM 文本分类（无预训练），适合作为传统深度学习对照。',
        'kind': 'custom',
        'path': os.path.join(CUSTOM_MODELS_DIR, 'textrnn_news_classifier'),
        'badge': '极速基线',
        'tag': 'warning',
        'test_accuracy': 95.75,
    },
}

DEFAULT_MODEL_ID = 'bert_cnn'


# ============ Loaders ============

def _load_hf(cfg):
    tokenizer = BertTokenizer.from_pretrained(cfg['path'])
    model = cfg['hf_class'].from_pretrained(cfg['path'])
    return tokenizer, model, DEFAULT_LABEL_MAP


def _load_custom(cfg):
    pkl_cfg = joblib.load(os.path.join(cfg['path'], 'config.pkl'))
    label_encoder = joblib.load(os.path.join(cfg['path'], 'label_encoder.pkl'))
    label_map = {i: cls for i, cls in enumerate(label_encoder.classes_)}

    mtype = pkl_cfg['model_type']

    if mtype == 'textcnn':
        tokenizer = BertTokenizer.from_pretrained(cfg['path'])
        model = TextCNNForClassification(
            vocab_size=pkl_cfg['vocab_size'],
            embedding_dim=pkl_cfg['embedding_dim'],
            num_labels=pkl_cfg['num_labels'],
            filter_sizes=pkl_cfg['filter_sizes'],
            num_filters=pkl_cfg['num_filters'],
            dropout=pkl_cfg['dropout'],
        )
    elif mtype == 'textrnn':
        tokenizer = BertTokenizer.from_pretrained(cfg['path'])
        model = TextRNNForClassification(
            vocab_size=pkl_cfg['vocab_size'],
            embedding_dim=pkl_cfg['embedding_dim'],
            hidden_dim=pkl_cfg['hidden_dim'],
            num_labels=pkl_cfg['num_labels'],
            num_layers=pkl_cfg['num_layers'],
            dropout=pkl_cfg['dropout'],
            bidirectional=pkl_cfg['bidirectional'],
        )
    elif mtype == 'bert_cnn':
        # bert_cnn 的目录里没有 tokenizer，从 BERT base 加载
        tokenizer = BertTokenizer.from_pretrained(BERT_BASE_PATH)
        model = BertCNNForClassification(
            bert_model_name=BERT_BASE_PATH,
            num_labels=pkl_cfg['num_labels'],
            cnn_filters=pkl_cfg['cnn_filters'],
            kernel_sizes=pkl_cfg['kernel_sizes'],
        )
    elif mtype == 'bert_textrnn':
        tokenizer = BertTokenizer.from_pretrained(cfg['path'])
        model = BertTextRNNForClassification(
            bert_model_name=BERT_BASE_PATH,
            num_labels=pkl_cfg['num_labels'],
            hidden_dim=pkl_cfg['hidden_dim'],
            num_layers=pkl_cfg['num_layers'],
            dropout=pkl_cfg['dropout'],
            bidirectional=pkl_cfg['bidirectional'],
        )
    else:
        raise ValueError(f'Unknown model_type in config.pkl: {mtype}')

    state_dict = torch.load(
        os.path.join(cfg['path'], 'pytorch_model.bin'),
        map_location='cpu',
    )
    model.load_state_dict(state_dict)
    return tokenizer, model, label_map


def _pick_device():
    """设备选择(默认 auto:有 GPU 用 GPU,没有走 CPU)。
    可用环境变量覆盖:CLASSIFIER_DEVICE=cpu / cuda / auto
    """
    pref = os.environ.get('CLASSIFIER_DEVICE', 'auto').lower()
    if pref == 'cpu':
        return torch.device('cpu')
    if pref == 'cuda' and torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class TransformerClassifier:
    def __init__(self, model_id):
        if model_id not in MODEL_REGISTRY:
            raise ValueError(f'Unknown model: {model_id}')
        cfg = MODEL_REGISTRY[model_id]
        self.model_id = model_id
        self.model_name = cfg['name']

        if cfg['kind'] == 'hf':
            self.tokenizer, self.model, self.label_map = _load_hf(cfg)
        else:
            self.tokenizer, self.model, self.label_map = _load_custom(cfg)

        self.model.eval()
        self.device = _pick_device()
        try:
            self.model.to(self.device)
        except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
            # 显存装不下,回落到 CPU
            print(f'[classifier] {self.device} 加载失败,回落到 CPU: {e}')
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.device = torch.device('cpu')
            self.model.to(self.device)

    def classify(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding='max_length',
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
        except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
            # 推理时 OOM:回落到 CPU 并重试一次
            if 'out of memory' in str(e).lower() or 'CUDA' in str(e):
                print(f'[classifier] 推理 OOM,迁移到 CPU 重试: {e}')
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                self.device = torch.device('cpu')
                self.model.to(self.device)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model(**inputs)
            else:
                raise

        if isinstance(outputs, dict):
            logits = outputs['logits']
        else:
            logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
        return {
            'category': self.label_map.get(predicted_class, '未知'),
            'confidence': confidence,
            'model_id': self.model_id,
            'model_name': self.model_name,
        }


# ============ Cache ============
_classifier_cache = {}


def get_classifier(model_id=None):
    if not _TORCH_AVAILABLE:
        raise RuntimeError(
            f'分类引擎不可用:torch 加载失败 ({_TORCH_IMPORT_ERROR})。'
            f'常见原因:Windows 分页文件太小 / C 盘没空间。请扩大 pagefile 后重启服务。'
        )
    if not model_id or model_id not in MODEL_REGISTRY:
        model_id = DEFAULT_MODEL_ID
    if model_id not in _classifier_cache:
        cfg = MODEL_REGISTRY[model_id]
        print(f"[classifier] Loading {cfg['name']} from {cfg['path']}")
        _classifier_cache[model_id] = TransformerClassifier(model_id)
    return _classifier_cache[model_id]


def get_available_models():
    return [
        {
            'id': mid,
            'name': cfg['name'],
            'display_name': cfg['display_name'],
            'description': cfg['description'],
            'badge': cfg['badge'],
            'tag': cfg.get('tag', 'accent'),
            'kind': cfg['kind'],
            'is_loaded': mid in _classifier_cache,
        }
        for mid, cfg in MODEL_REGISTRY.items()
    ]


def get_model_display(model_id):
    return MODEL_REGISTRY.get(model_id, {}).get('display_name', model_id or '未知')
