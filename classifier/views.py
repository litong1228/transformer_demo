from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import ClassificationResult, BatchClassification, BatchClassificationItem
from .model_loader import (
    get_classifier, get_available_models, get_model_display,
    MODEL_REGISTRY, DEFAULT_MODEL_ID, DEFAULT_LABEL_MAP,
)
import io
import csv
import chardet
import time
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404


def _lazy_pd():
    """延迟导入 pandas:在内存紧张时避免模块加载阶段失败。"""
    import pandas as pd
    return pd


def _resolve_model_id(request):
    mid = request.POST.get('model', '').strip()
    if mid not in MODEL_REGISTRY:
        mid = DEFAULT_MODEL_ID
    return mid


# 可识别的文本列名 (小写)。命中任何一个就使用该列作为待分类文本。
_TEXT_COLUMN_NAMES = {
    'text', 'content', 'body', 'news', 'article',
    '内容', '正文', '文本', '新闻', '正文内容',
}


def _extract_texts_from_csv(decoded_data):
    """从 CSV 中提取待分类文本。
    优先级:
      1) 首行中含有已知文本列名 (text/content/内容/正文 等) → 使用该列
      2) 否则视为无表头 CSV → 取平均字符长度最长的列 (跳过看起来像 URL/时间戳的列)
    返回: (texts: list[str], total_rows: int)
    """
    pd = _lazy_pd()
    # 第一次以默认 header 读取
    try:
        df = pd.read_csv(io.StringIO(decoded_data), dtype=str, keep_default_na=False)
    except Exception:
        df = None

    if df is not None and not df.empty:
        lower_to_orig = {str(c).strip().lower(): c for c in df.columns}
        for name in _TEXT_COLUMN_NAMES:
            if name in lower_to_orig:
                col = lower_to_orig[name]
                series = df[col].astype(str)
                return series.tolist(), len(df)

    # 无表头分支: 重新读取, 把所有行都当作数据
    df2 = pd.read_csv(io.StringIO(decoded_data), header=None, dtype=str, keep_default_na=False)
    if df2.empty:
        return [], 0
    if df2.shape[1] == 1:
        col_values = df2[df2.columns[0]].astype(str)
        return col_values.tolist(), len(df2)

    # 多列: 排除明显的 URL/时间/极短列, 选平均字符长度最长的中文/普通文本列
    def _is_url_like(s):
        s = str(s)
        return s.startswith('http://') or s.startswith('https://')

    candidates = []
    for c in df2.columns:
        col = df2[c].astype(str)
        sample = col.head(20)
        url_ratio = sample.map(_is_url_like).mean() if len(sample) else 0
        avg_len = col.str.len().mean()
        if url_ratio > 0.5:
            continue
        candidates.append((c, avg_len))

    if not candidates:
        # 退回全部列
        candidates = [(c, df2[c].astype(str).str.len().mean()) for c in df2.columns]

    text_col = max(candidates, key=lambda t: t[1])[0]
    return df2[text_col].astype(str).tolist(), len(df2)


@ensure_csrf_cookie
def classify_text(request):
    """渲染分类页面（POST 走 JSON API）。"""
    recent = []
    user_stats = None
    if request.user.is_authenticated:
        recent = list(
            ClassificationResult.objects
            .filter(user=request.user)
            .order_by('-created_at')[:5]
        )
        for r in recent:
            r.model_display = get_model_display(r.model_used)
            r.confidence_pct = f'{r.confidence * 100:.2f}'

        from django.db.models import Count
        cat_rows = list(
            ClassificationResult.objects
            .filter(user=request.user)
            .values('predicted_category')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')
        )
        total = sum(r['cnt'] for r in cat_rows)
        if total > 0:
            user_stats = {
                'total': total,
                'distinct': len(cat_rows),
                'rows': [
                    {
                        'name': r['predicted_category'],
                        'count': r['cnt'],
                        'percent': round(r['cnt'] * 100 / total, 1),
                    }
                    for r in cat_rows
                ],
            }

    return render(request, 'classifier/classify_text.html', {
        'available_models': get_available_models(),
        'default_model_id': DEFAULT_MODEL_ID,
        'supported_categories': list(DEFAULT_LABEL_MAP.values()),
        'recent_results': recent,
        'user_stats': user_stats,
    })


@require_POST
def classify_text_api(request):
    """JSON 端点：接收文本与模型，返回分类结果。"""
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'ok': False, 'error': '请输入要分类的文本'}, status=400)

    model_id = _resolve_model_id(request)

    t0 = time.time()
    try:
        classifier = get_classifier(model_id)
        result = classifier.classify(text)
    except OSError as e:
        # Windows 上常见: pagefile 不够大,无法把模型读入内存
        if 'os error 1455' in str(e) or '页面文件太小' in str(e):
            msg = '模型加载失败:Windows 虚拟内存(pagefile)不足。请前往"系统属性 → 高级 → 性能设置 → 高级 → 虚拟内存"将分页文件提升到 ≥ 8GB 后重启。'
        else:
            msg = f'模型加载失败:{e}'
        return JsonResponse({'ok': False, 'error': msg}, status=500)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'模型加载或推理失败:{e}'}, status=500)
    elapsed_ms = int((time.time() - t0) * 1000)

    ClassificationResult.objects.create(
        user=request.user if request.user.is_authenticated else None,
        text=text,
        predicted_category=result['category'],
        confidence=result['confidence'],
        model_used=model_id,
        elapsed_ms=elapsed_ms,
    )

    recent = []
    if request.user.is_authenticated:
        recent_qs = (
            ClassificationResult.objects
            .filter(user=request.user)
            .order_by('-created_at')[:5]
        )
        for r in recent_qs:
            recent.append({
                'id': r.id,
                'text': r.text,
                'snippet': (r.text[:30] + '…') if len(r.text) > 30 else r.text,
                'category': r.predicted_category,
                'confidence': r.confidence,
                'model_id': r.model_used,
                'model_name': get_model_display(r.model_used),
                'created_at': r.created_at.strftime('%H:%M:%S'),
            })

    return JsonResponse({
        'ok': True,
        'category': result['category'],
        'confidence': result['confidence'],
        'model_id': model_id,
        'model_name': get_model_display(model_id),
        'elapsed_ms': elapsed_ms,
        'recent': recent,
    })


@ensure_csrf_cookie
def batch_classify(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, '请选择要上传的文件')
            return redirect('batch_classify')

        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            messages.error(request, '请上传 CSV 文件')
            return redirect('batch_classify')

        model_id = _resolve_model_id(request)

        try:
            # 读取文件原始内容（只读取一次）
            raw_data = file.read()

            # 自动检测编码
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding')

            if encoding is None:
                common_encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
            else:
                common_encodings = [encoding, 'utf-8', 'gbk']

            decoded_data = None
            for enc in common_encodings:
                try:
                    decoded_data = raw_data.decode(enc)
                    encoding = enc
                    break
                except (UnicodeDecodeError, LookupError):
                    continue

            if decoded_data is None:
                messages.error(request, '无法识别文件编码，请将文件另存为 UTF-8 编码后重试')
                return redirect('batch_classify')

            texts, total_rows = _extract_texts_from_csv(decoded_data)

            if not texts:
                messages.error(request, 'CSV 文件为空或无法识别文本内容')
                return redirect('batch_classify')

            # 批量分类
            results = []
            success_count = 0
            cat_counter = {}
            classifier = get_classifier(model_id)
            t0 = time.time()
            for raw in texts:
                text = str(raw).strip()
                if text:
                    result = classifier.classify(text)
                    results.append({
                        'text': text,
                        'category': result['category'],
                        'confidence': result['confidence'],
                        'confidence_pct': f'{result["confidence"] * 100:.2f}',
                    })
                    cat_counter[result['category']] = cat_counter.get(result['category'], 0) + 1
                    success_count += 1
            elapsed_ms = int((time.time() - t0) * 1000)

            batch = BatchClassification.objects.create(
                user=request.user if request.user.is_authenticated else None,
                file_name=file.name,
                total_count=total_rows,
                success_count=success_count,
                model_used=model_id,
                elapsed_ms=elapsed_ms,
            )
            BatchClassificationItem.objects.bulk_create([
                BatchClassificationItem(
                    batch=batch,
                    row_index=i + 1,
                    text=r['text'],
                    predicted_category=r['category'],
                    confidence=r['confidence'],
                )
                for i, r in enumerate(results)
            ])

            # 分类分布（按数量降序）
            distribution = sorted(
                [{'name': k, 'count': v} for k, v in cat_counter.items()],
                key=lambda x: -x['count'],
            )
            top_cat = distribution[0]['name'] if distribution else '—'
            max_count = distribution[0]['count'] if distribution else 1

            # 置信度统计与分桶
            confidences = [r['confidence'] for r in results]
            if confidences:
                avg_conf = sum(confidences) / len(confidences) * 100
                min_conf = min(confidences) * 100
                max_conf = max(confidences) * 100
                high_count = sum(1 for c in confidences if c >= 0.95)
                mid_count = sum(1 for c in confidences if 0.80 <= c < 0.95)
                low_count = sum(1 for c in confidences if c < 0.80)
            else:
                avg_conf = min_conf = max_conf = 0
                high_count = mid_count = low_count = 0

            conf_buckets_max = max(high_count, mid_count, low_count, 1)
            confidence_buckets = [
                {'label': '高置信 (≥95%)', 'count': high_count, 'tier': 'high'},
                {'label': '中置信 (80–95%)', 'count': mid_count, 'tier': 'mid'},
                {'label': '低置信 (<80%)', 'count': low_count, 'tier': 'low'},
            ]

            throughput = (success_count / (elapsed_ms / 1000)) if elapsed_ms else 0
            avg_latency = (elapsed_ms / success_count) if success_count else 0

            # 按结果模板要求的阈值再分桶 (≥90 / 70-90 / <70)
            high_conf_90 = sum(1 for c in confidences if c >= 0.90)
            mid_conf_70 = sum(1 for c in confidences if 0.70 <= c < 0.90)
            low_conf_70 = sum(1 for c in confidences if c < 0.70)

            elapsed_sec = elapsed_ms / 1000
            if elapsed_sec >= 60:
                elapsed_display = f'{int(elapsed_sec // 60)}m {int(elapsed_sec % 60)}s'
            else:
                elapsed_display = f'{elapsed_sec:.1f}s'

            from django.utils import timezone
            task = {
                'id': batch.id,
                'filename': file.name,
                'total': success_count,
                'model_name': get_model_display(model_id),
                'elapsed_display': elapsed_display,
                'avg_ms': f'{avg_latency:.0f}',
                'completed_at': timezone.now(),
                'high_conf': high_conf_90,
                'mid_conf': mid_conf_70,
                'low_conf': low_conf_70,
            }

            # 给详情表行补字段 (template 用的是 predicted_category / cat_slug / elapsed_ms)
            CAT_SLUG_MAP = {
                '科技': 'tech', '体育': 'sp', '财经': 'fn', '娱乐': 'et',
                '时政': 'po', '教育': 'ed', '健康': 'he',
                '社会': 'so', '家居': 'so', '文化': 'so',
                '游戏': 'game', '房产': 'property', '汽车': 'property',
                '时尚': 'et',
            }
            for r in results:
                r['predicted_category'] = r['category']
                r['cat_slug'] = CAT_SLUG_MAP.get(r['category'], 'tech')
                r['elapsed_ms'] = round(avg_latency)

            # 类别分布 (右侧条形)
            category_dist = []
            for d in distribution:
                category_dist.append({
                    'name': d['name'],
                    'count': d['count'],
                    'percent': round(d['count'] * 100 / success_count) if success_count else 0,
                    'slug': CAT_SLUG_MAP.get(d['name'], 'tech'),
                })

            return render(request, 'classifier/batch_result.html', {
                'task': task,
                'results': results,
                'category_dist': category_dist,
                'file_name': file.name,
                'total_count': total_rows,
                'success_count': success_count,
                'failed_count': total_rows - success_count,
                'model_id': model_id,
                'model_name': get_model_display(model_id),
                'elapsed_ms': elapsed_ms,
                'distribution': distribution,
                'distribution_count': len(distribution),
                'top_cat': top_cat,
                'max_count': max_count,
                'avg_confidence': avg_conf,
                'min_confidence': min_conf,
                'max_confidence': max_conf,
                'confidence_buckets': confidence_buckets,
                'conf_buckets_max': conf_buckets_max,
                'throughput': throughput,
                'avg_latency': avg_latency,
            })

        except Exception as e:
            messages.error(request, f'文件处理错误: {str(e)}')
            return redirect('batch_classify')

    # GET 请求：渲染上传页 + 历史批次（仅登录）
    recent_batches = []
    batch_stats = None
    if request.user.is_authenticated:
        all_batches = BatchClassification.objects.filter(user=request.user)
        recent_batches = list(all_batches.order_by('-created_at')[:5])
        for b in recent_batches:
            b.model_display = get_model_display(b.model_used)
            b.success_rate = (b.success_count / b.total_count * 100) if b.total_count else 0

        total_batches = all_batches.count()
        if total_batches > 0:
            agg = all_batches.aggregate(
                total_items=Sum('total_count'),
                total_success=Sum('success_count'),
            )
            total_items = agg['total_items'] or 0
            total_success = agg['total_success'] or 0
            avg_rate = (total_success / total_items * 100) if total_items else 0

            from collections import Counter
            model_counter = Counter(all_batches.values_list('model_used', flat=True))
            top_count = model_counter.most_common(1)[0][1]
            tied_models = [m for m, c in model_counter.items() if c == top_count]
            if len(tied_models) == 1:
                most_model_id = tied_models[0]
            else:
                # 平局：取最近一次使用过的那个
                most_model_id = (
                    all_batches.filter(model_used__in=tied_models)
                    .order_by('-created_at')
                    .values_list('model_used', flat=True)
                    .first()
                )

            batch_stats = {
                'total_batches': total_batches,
                'total_items': total_items,
                'avg_rate': avg_rate,
                'most_used_model': get_model_display(most_model_id),
            }

    return render(request, 'classifier/batch_classify.html', {
        'available_models': get_available_models(),
        'default_model_id': DEFAULT_MODEL_ID,
        'recent_batches': recent_batches,
        'batch_stats': batch_stats,
    })


def export_batch(request, batch_id):
    """导出某次批量分类的明细为 CSV (utf-8-sig)。
    权限规则:
      - 批次有 user: 仅本人可下载
      - 批次匿名: 所有人可下载 (因为本来就无法绑定身份)
    """
    batch = get_object_or_404(BatchClassification, id=batch_id)
    if batch.user_id is not None and (
        not request.user.is_authenticated or request.user.id != batch.user_id
    ):
        raise Http404('无权访问该批次')

    model_name = get_model_display(batch.model_used)
    completed_at = batch.created_at.strftime('%Y-%m-%d %H:%M:%S')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    safe_name = batch.file_name.rsplit('.', 1)[0] or 'batch'
    response['Content-Disposition'] = (
        f'attachment; filename="batch_{batch.id}_{safe_name}.csv"'
    )
    # utf-8-sig BOM 让 Excel 双击不乱码
    response.write('﻿')

    writer = csv.writer(response)
    writer.writerow(['序号', '文本', '预测分类', '置信度(%)', '状态', '模型', '完成时间'])
    for item in batch.items.all():
        conf_pct = round(item.confidence * 100, 2)
        status = 'OK' if item.confidence >= 0.9 else 'REVIEW'
        writer.writerow([
            item.row_index,
            item.text,
            item.predicted_category,
            f'{conf_pct:.2f}',
            status,
            model_name,
            completed_at,
        ])
    return response


def classification_history(request):
    if not request.user.is_authenticated:
        messages.error(request, '请先登录')
        return redirect('/accounts/login/?next=/classify/history/')

    qs = ClassificationResult.objects.filter(user=request.user).order_by('-created_at')

    # 筛选
    model_filter = request.GET.get('model', '').strip()
    cat_filter = request.GET.get('category', '').strip()
    if model_filter and model_filter in MODEL_REGISTRY:
        qs = qs.filter(model_used=model_filter)
    if cat_filter:
        qs = qs.filter(predicted_category=cat_filter)

    # 全集统计（不带筛选）
    total_qs = ClassificationResult.objects.filter(user=request.user)
    total_count = total_qs.count()
    from django.db.models import Count
    by_model = list(
        total_qs.values('model_used').annotate(cnt=Count('id')).order_by('-cnt')
    )
    by_cat = list(
        total_qs.values('predicted_category').annotate(cnt=Count('id')).order_by('-cnt')
    )
    top_model_id = by_model[0]['model_used'] if by_model else ''
    top_cat = by_cat[0]['predicted_category'] if by_cat else '—'

    # 给每条记录附加模型展示名 + 百分比形式的置信度
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page', 1))
    for r in page.object_list:
        r.model_display = get_model_display(r.model_used)
        r.confidence_pct = f'{r.confidence * 100:.2f}'

    return render(request, 'classifier/history.html', {
        'page': page,
        'page_obj': page,
        'is_paginated': page.has_other_pages(),
        'history': page,
        'total': total_count,
        'total_count': total_count,
        'filtered_count': qs.count(),
        'by_model_count': len([x for x in by_model if x['cnt'] > 0]),
        'by_cat_count': len([x for x in by_cat if x['cnt'] > 0]),
        'top_model_name': get_model_display(top_model_id),
        'most_used_model': get_model_display(top_model_id),
        'most_common_category': top_cat,
        'top_cat': top_cat,
        'available_models': get_available_models(),
        'supported_categories': list(DEFAULT_LABEL_MAP.values()),
        'current_model': model_filter,
        'current_model_name': get_model_display(model_filter) if model_filter else '',
        'current_cat': cat_filter,
    })
