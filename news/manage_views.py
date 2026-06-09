from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, ExpressionWrapper, IntegerField, Q
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .models import News, Category
from accounts.models import Bookmark, ReadingHistory


def _staff(view):
    return staff_member_required(login_url='/accounts/login/')(view)


@_staff
def manage_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum

    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    month_start = today.replace(day=1)

    total_news = News.objects.count()

    # 真实统计 — 各分类发文数
    cat_rows = list(
        Category.objects.annotate(news_total=Count('news')).order_by('-news_total')[:8]
    )
    cat_total = sum(c.news_total for c in cat_rows) or 1
    category_breakdown = [
        {
            'name': c.name,
            'count': c.news_total,
            'percent': round(c.news_total * 100 / cat_total),
            'slug': 'tech',
        }
        for c in cat_rows
    ]

    # 今日 PV(基于阅读历史的 last_read_at 在今天)
    today_pv = ReadingHistory.objects.filter(last_read_at__date=today).aggregate(s=Sum('read_count'))['s'] or 0
    yesterday_pv = ReadingHistory.objects.filter(last_read_at__date=yesterday).aggregate(s=Sum('read_count'))['s'] or 0
    pv_delta = _pct(today_pv, yesterday_pv)

    # 注册:本月 vs 上月同期
    new_users_month = User.objects.filter(date_joined__date__gte=month_start).count()
    prev_month_start = (month_start - timedelta(days=1)).replace(day=1)
    new_users_prev = User.objects.filter(
        date_joined__date__gte=prev_month_start,
        date_joined__date__lt=month_start,
    ).count()
    users_delta = _pct(new_users_month, new_users_prev)

    # 新闻分类次数:今日 vs 昨日
    try:
        from classifier.models import ClassificationResult
        classify_today = ClassificationResult.objects.filter(created_at__date=today).count()
        classify_yesterday = ClassificationResult.objects.filter(created_at__date=yesterday).count()
        classify_total = ClassificationResult.objects.count()
    except Exception:
        classify_today = classify_yesterday = classify_total = 0
    classify_delta = _pct(classify_today, classify_yesterday)

    # 今日新建新闻
    today_new_news = News.objects.filter(created_at__date=today).count()

    # 模型性能监控:全部来自真实运行数据
    # - use_pct: ClassificationResult.id 计数 + BatchClassification.success_count 求和,占总量的比例
    # - latency_ms: ClassificationResult.elapsed_ms 平均;无单条记录时回退到 BatchClassification 的 (elapsed_ms / success_count) 加权平均
    # - accuracy: MODEL_REGISTRY 里离线测试集真实评估结果 (results/*_classification_report.txt)
    try:
        from classifier.model_loader import MODEL_REGISTRY, _classifier_cache
        from classifier.models import ClassificationResult, BatchClassification
        from django.db.models import Avg

        single_stats = {
            s['model_used']: s
            for s in ClassificationResult.objects.values('model_used')
                .annotate(uses=Count('id'), avg_ms=Avg('elapsed_ms'))
        }
        batch_stats = {
            b['model_used']: b
            for b in BatchClassification.objects.values('model_used')
                .annotate(
                    uses=Sum('success_count'),
                    total_ms=Sum('elapsed_ms'),
                )
        }

        total_uses = sum(
            single_stats.get(mid, {}).get('uses', 0) + (batch_stats.get(mid, {}).get('uses') or 0)
            for mid in MODEL_REGISTRY
        )
        model_perf = []
        for mid, cfg in MODEL_REGISTRY.items():
            s_uses = single_stats.get(mid, {}).get('uses', 0)
            b_uses = batch_stats.get(mid, {}).get('uses') or 0
            uses = s_uses + b_uses

            # 平均延迟:优先单条平均,其次批量按条均摊
            s_avg_ms = single_stats.get(mid, {}).get('avg_ms')
            b_total_ms = batch_stats.get(mid, {}).get('total_ms') or 0
            if s_avg_ms:
                latency_ms = round(s_avg_ms)
            elif b_uses and b_total_ms:
                latency_ms = round(b_total_ms / b_uses)
            else:
                latency_ms = None

            model_perf.append({
                'id': mid,
                'name': cfg['display_name'],
                'ok': mid in _classifier_cache,
                'uses': uses,
                'use_pct': round(uses * 100 / total_uses) if total_uses else 0,
                'latency_ms': latency_ms,
                'accuracy': cfg.get('test_accuracy'),
            })
    except Exception:
        model_perf = []

    # 近 7 天 PV 趋势(用 ReadingHistory.read_count 求和)
    weekly_pv = []
    max_v = 1
    raw_days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        v = ReadingHistory.objects.filter(last_read_at__date=d).aggregate(s=Sum('read_count'))['s'] or 0
        raw_days.append((d, v))
        if v > max_v:
            max_v = v
    for d, v in raw_days:
        weekly_pv.append({
            'day': d.strftime('%m/%d') if d != today else '今日',
            'label': f'{v // 1000}k' if v >= 1000 else str(v),
            'value': v,
            'percent': round(v * 100 / max_v) if max_v else 0,
        })

    ctx = {
        'news_count': total_news,
        'category_count': Category.objects.count(),
        'user_count': User.objects.count(),
        'bookmark_count': Bookmark.objects.count(),
        'featured_count': News.objects.filter(is_featured=True).count(),
        'history_count': ReadingHistory.objects.count(),
        'recent_news': News.objects.select_related('category').order_by('-created_at')[:8],
        'category_stats': cat_rows,
        'category_breakdown': category_breakdown,
        'month_total_news': News.objects.filter(created_at__date__gte=month_start).count(),
        'weekly_pv': weekly_pv,
        'model_perf': model_perf,
        'stats': {
            'today_pv': today_pv,
            'pv_delta': pv_delta,
            'new_users_month': new_users_month,
            'users_delta': users_delta,
            'classify_today': classify_today,
            'classify_total': classify_total,
            'classify_delta': classify_delta,
            'total_news': total_news,
            'today_new_news': today_new_news,
            'avg_ms': '—',
        },
    }
    return render(request, 'manage/dashboard.html', ctx)


def _pct(now_v, prev_v):
    """计算同比变化百分比, 返回字符串如 '+12%' 或 '-3%'"""
    if not prev_v:
        return '+0%' if now_v == 0 else '新数据'
    pct = round((now_v - prev_v) * 100 / prev_v)
    sign = '+' if pct >= 0 else ''
    return f'{sign}{pct}%'


# ============ News CRUD ============

@_staff
def manage_news_list(request):
    qs = News.objects.select_related('category').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(title__icontains=q)
    cat_id = request.GET.get('category', '').strip()
    if cat_id:
        qs = qs.filter(category_id=cat_id)
    featured = request.GET.get('featured', '').strip()
    if featured == '1':
        qs = qs.filter(is_featured=True)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'manage/news_list.html', {
        'page': page,
        'page_obj': page,
        'is_paginated': page.has_other_pages(),
        'news_list': page,
        'total_count': paginator.count,
        'q': q,
        'cat_id': int(cat_id) if cat_id.isdigit() else None,
        'featured_only': featured == '1',
        'categories': Category.objects.all(),
        'total': qs.count(),
        'news_count': News.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': User.objects.count(),
    })


def _save_news(request, news=None):
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    if not title or not content:
        messages.error(request, '标题和内容不能为空')
        return None
    obj = news or News()
    obj.title = title
    obj.content = content
    obj.summary = request.POST.get('summary', '').strip() or None
    obj.author = request.POST.get('author', '').strip() or None
    obj.source = request.POST.get('source', '').strip() or None
    obj.image_url = request.POST.get('image_url', '').strip() or None
    cat = request.POST.get('category', '').strip()
    obj.category_id = int(cat) if cat.isdigit() else None
    obj.is_featured = bool(request.POST.get('is_featured'))
    obj.save()
    return obj


@_staff
def manage_news_create(request):
    if request.method == 'POST':
        obj = _save_news(request)
        if obj:
            messages.success(request, f'新闻"{obj.title}"已创建')
            return redirect('/manage/news/')
    return render(request, 'manage/news_form.html', {
        'mode': 'create',
        'news': None,
        'categories': Category.objects.all(),
    })


@_staff
def manage_news_edit(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        obj = _save_news(request, news)
        if obj:
            messages.success(request, '新闻已更新')
            return redirect('/manage/news/')
    return render(request, 'manage/news_form.html', {
        'mode': 'edit',
        'news': news,
        'categories': Category.objects.all(),
    })


@_staff
@require_POST
def manage_news_delete(request, news_id):
    news = get_object_or_404(News, id=news_id)
    title = news.title
    news.delete()
    messages.success(request, f'已删除新闻"{title}"')
    return redirect(request.META.get('HTTP_REFERER') or '/manage/news/')


@_staff
@require_POST
def manage_news_toggle_featured(request, news_id):
    news = get_object_or_404(News, id=news_id)
    news.is_featured = not news.is_featured
    news.save(update_fields=['is_featured'])
    state = '设为头条' if news.is_featured else '取消头条'
    messages.success(request, f'{state}：{news.title}')
    return redirect(request.META.get('HTTP_REFERER') or '/manage/news/')


# ============ Category CRUD ============

@_staff
def manage_category_list(request):
    categories = Category.objects.annotate(news_count=Count('news')).order_by('-news_count', 'name')
    return render(request, 'manage/category_list.html', {
        'categories': categories,
        'total_news': News.objects.count(),
        'news_count': News.objects.count(),
        'category_count': categories.count(),
        'user_count': User.objects.count(),
    })


@_staff
def manage_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, '分类名不能为空')
        elif Category.objects.filter(name=name).exists():
            messages.error(request, f'分类"{name}"已存在')
        else:
            cat = Category.objects.create(name=name)
            messages.success(request, f'分类"{cat.name}"已创建')
            return redirect('/manage/category/')
    return render(request, 'manage/category_form.html', {
        'mode': 'create',
        'category': None,
    })


@_staff
def manage_category_edit(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, '分类名不能为空')
        elif Category.objects.filter(name=name).exclude(id=cat.id).exists():
            messages.error(request, f'分类"{name}"已存在')
        else:
            cat.name = name
            cat.save(update_fields=['name'])
            messages.success(request, '分类已更新')
            return redirect('/manage/category/')
    return render(request, 'manage/category_form.html', {
        'mode': 'edit',
        'category': cat,
    })


@_staff
@require_POST
def manage_category_delete(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if cat.news_set.exists():
        messages.error(request, f'分类"{cat.name}"下还有新闻，不能删除')
    else:
        name = cat.name
        cat.delete()
        messages.success(request, f'已删除分类"{name}"')
    return redirect('/manage/category/')


# ============ User Management ============

@_staff
def manage_users_list(request):
    qs = User.objects.annotate(
        bookmark_total=Count('bookmarks', distinct=True),
        history_total=Count('reading_history', distinct=True),
    ).order_by('-date_joined')
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    role = request.GET.get('role', '').strip()
    if role == 'staff':
        qs = qs.filter(is_staff=True)
    elif role == 'inactive':
        qs = qs.filter(is_active=False)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'manage/user_list.html', {
        'page': page,
        'page_obj': page,
        'is_paginated': page.has_other_pages(),
        'user_list': page,
        'total_count': paginator.count,
        'q': q,
        'role': role,
        'total': qs.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'active_count': User.objects.filter(is_active=True).count(),
        'news_count': News.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': User.objects.count(),
    })


@_staff
def manage_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'update':
            email = request.POST.get('email', '').strip()
            if email and User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, '该邮箱已被其他用户使用')
            else:
                user.email = email
                # 不允许取消自己的 staff 权限以免锁死自己
                if user.id != request.user.id:
                    user.is_staff = bool(request.POST.get('is_staff'))
                    user.is_active = bool(request.POST.get('is_active'))
                user.save()
                messages.success(request, '用户信息已更新')
            return redirect(f'/manage/users/{user.id}/edit/')
        elif action == 'reset_password':
            new_pwd = request.POST.get('new_password', '').strip()
            if len(new_pwd) < 8:
                messages.error(request, '新密码至少 8 位')
            else:
                user.set_password(new_pwd)
                user.save()
                messages.success(request, f'已重置 {user.username} 的密码')
            return redirect(f'/manage/users/{user.id}/edit/')

    return render(request, 'manage/user_form.html', {
        'user_obj': user,
        'edit_user': user,
        'is_self': user.id == request.user.id,
        'bookmark_count': Bookmark.objects.filter(user=user).count(),
        'history_count': ReadingHistory.objects.filter(user=user).count(),
        'news_count': News.objects.count(),
        'category_count': Category.objects.count(),
        'user_count': User.objects.count(),
    })


@_staff
@require_POST
def manage_user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, '不能禁用自己')
    else:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f'已{"启用" if user.is_active else "禁用"} {user.username}')
    return redirect(request.META.get('HTTP_REFERER') or '/manage/users/')


@_staff
@require_POST
def manage_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.id == request.user.id:
        messages.error(request, '不能删除自己')
    else:
        username = user.username
        user.delete()
        messages.success(request, f'已删除用户 {username}')
    return redirect('/manage/users/')
