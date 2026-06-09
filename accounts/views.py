from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum

from .models import Bookmark, ReadingHistory, UserProfile
from news.models import News


REMEMBER_USERNAME_COOKIE = 'remembered_username'
REMEMBER_SESSION_SECONDS = 7 * 24 * 60 * 60


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = bool(request.POST.get('remember'))

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if remember:
                request.session.set_expiry(REMEMBER_SESSION_SECONDS)
            else:
                request.session.set_expiry(0)
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            response = redirect(next_url)
            if remember:
                response.set_cookie(
                    REMEMBER_USERNAME_COOKIE,
                    user.username,
                    max_age=REMEMBER_SESSION_SECONDS,
                    httponly=True,
                    samesite='Lax',
                )
            else:
                response.delete_cookie(REMEMBER_USERNAME_COOKIE)
            return response
        else:
            messages.error(request, '用户名或密码错误！')

    context = {
        'remembered_username': request.COOKIES.get(REMEMBER_USERNAME_COOKIE, ''),
    }
    return render(request, 'accounts/login.html', context)


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致！')
            return render(request, 'accounts/register.html')

        if len(password) < 8:
            messages.error(request, '密码长度至少为8位！')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在！')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册！')
            return render(request, 'accounts/register.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'欢迎加入，{user.username}！')
            return redirect('/')
        except Exception:
            messages.error(request, '注册失败，请稍后重试！')
            return render(request, 'accounts/register.html')

    return render(request, 'accounts/register.html')


def user_logout(request):
    logout(request)
    return redirect('/')


@require_POST
@login_required(login_url='/accounts/login/')
def toggle_bookmark(request, news_id):
    news = get_object_or_404(News, id=news_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, news=news)
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    total = news.bookmarked_by.count()
    return JsonResponse({'bookmarked': bookmarked, 'count': total})


def _profile_context(user, password_form=None, password_form_open=False):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    history_qs = ReadingHistory.objects.filter(user=user)
    week_history = history_qs.filter(last_read_at__gte=week_ago)
    month_history = history_qs.filter(last_read_at__gte=month_ago)

    # 统计指标
    week_unique = week_history.count()
    week_total_reads = week_history.aggregate(s=Sum('read_count'))['s'] or 0
    month_unique = month_history.count()
    month_total_reads = month_history.aggregate(s=Sum('read_count'))['s'] or 0
    total_reads = history_qs.aggregate(s=Sum('read_count'))['s'] or 0

    # 类别分布（最近 30 天）
    category_rows = list(
        month_history
        .values('news__category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    total_cat = sum(row['count'] for row in category_rows) or 1
    cleaned_categories = []
    for row in category_rows:
        name = row['news__category__name'] or '未分类'
        cleaned_categories.append({
            'name': name,
            'count': row['count'],
            'percent': round(row['count'] * 100 / total_cat),
            'slug': 'tech',
        })

    # 最近 7 天每天的阅读次数（按 last_read_at 计）
    daily_reads = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = history_qs.filter(
            last_read_at__gte=day_start, last_read_at__lt=day_end
        ).count()
        daily_reads.append({
            'label': day_start.strftime('%m-%d'),
            'count': count,
        })

    # 最近读过的新闻 Top 5
    top_news = list(
        history_qs.select_related('news', 'news__category')
        .order_by('-read_count', '-last_read_at')[:5]
    )
    # 最近阅读列表（按最近阅读时间排序,模板使用 read_at 字段名）
    recent_history = list(
        history_qs.select_related('news', 'news__category')
        .order_by('-last_read_at')[:10]
    )
    for h in recent_history:
        h.read_at = h.last_read_at

    # 收藏：分页嵌入
    bookmarks_qs = (
        Bookmark.objects.filter(user=user)
        .select_related('news', 'news__category')
    )
    bookmark_total = bookmarks_qs.count()

    # 新闻分类次数 + 平均置信度 + 最常用模型
    classify_count = 0
    avg_conf_display = '—'
    top_model_display = '—'
    try:
        from classifier.models import ClassificationResult
        from django.db.models import Avg
        cr_qs = ClassificationResult.objects.filter(user=user)
        classify_count = cr_qs.count()
        if classify_count:
            avg_conf = cr_qs.aggregate(a=Avg('confidence'))['a'] or 0
            avg_conf_display = f'{avg_conf * 100:.1f}%'
            top_model_row = (
                cr_qs.values('model_used')
                .annotate(n=Count('id'))
                .order_by('-n')
                .first()
            )
            if top_model_row:
                try:
                    from classifier.model_loader import get_model_display
                    top_model_display = get_model_display(top_model_row['model_used'])
                except Exception:
                    top_model_display = top_model_row['model_used']
    except Exception:
        pass

    days_registered = max((now.date() - user.date_joined.date()).days, 1) if user.date_joined else 1

    # 连续阅读天数:
    #   streak       = 截至今天往前数连续有阅读的天数
    #   streak_best  = 该用户历史上最长连续段
    read_dates = set(history_qs.dates('last_read_at', 'day'))
    today = now.date()
    streak = 0
    d = today
    while d in read_dates:
        streak += 1
        d -= timedelta(days=1)

    best = current = 0
    prev = None
    for cur in sorted(read_dates):
        if prev is not None and (cur - prev).days == 1:
            current += 1
        else:
            current = 1
        if current > best:
            best = current
        prev = cur

    stats = {
        'read_count': total_reads,
        'bookmark_count': bookmark_total,
        'classify_count': classify_count,
        'month_reads': month_total_reads,
        'streak': streak,
        'streak_best': best,
        'avg_confidence': avg_conf_display,
        'top_model': top_model_display,
    }

    return {
        'profile_user': user,
        'bookmark_total': bookmark_total,
        'bookmarks': bookmarks_qs[:12],
        'bookmarks_more': bookmark_total > 12,
        'week_unique': week_unique,
        'week_total_reads': week_total_reads,
        'month_unique': month_unique,
        'month_total_reads': month_total_reads,
        'category_breakdown': cleaned_categories,
        'reading_breakdown': cleaned_categories,
        'daily_reads': daily_reads,
        'top_news': top_news,
        'reading_history': recent_history,
        'stats': stats,
        'days_registered': days_registered,
        'password_form': password_form or PasswordChangeForm(user),
        'password_form_open': password_form_open,
    }


@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user

    if request.method == 'POST' and request.POST.get('action') == 'update_email':
        new_email = request.POST.get('email', '').strip()
        if not new_email:
            messages.error(request, '邮箱不能为空')
        elif new_email == user.email:
            messages.info(request, '邮箱未变更')
        elif User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, '该邮箱已被其他用户使用')
        else:
            user.email = new_email
            user.save(update_fields=['email'])
            messages.success(request, '邮箱已更新')
        return redirect('/accounts/profile/')

    return render(request, 'accounts/profile.html', _profile_context(user))


@require_POST
@login_required(login_url='/accounts/login/')
def password_change(request):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, '密码已修改')
        return redirect('/accounts/profile/')
    return render(
        request, 'accounts/profile.html',
        _profile_context(request.user, password_form=form, password_form_open=True),
    )


@login_required(login_url='/accounts/login/')
def bookmark_list(request):
    # 收藏功能已合并到个人中心，旧 URL 重定向
    return redirect('/accounts/profile/#bookmarks')


ALLOWED_AVATAR_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_AVATAR_SIZE = 3 * 1024 * 1024  # 3MB


@require_POST
@login_required(login_url='/accounts/login/')
def avatar_upload(request):
    file = request.FILES.get('avatar')
    if not file:
        messages.error(request, '请选择要上传的头像图片')
        return redirect('/accounts/profile/')

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        messages.error(request, '仅支持 JPG / PNG / WEBP / GIF 格式')
        return redirect('/accounts/profile/')

    if file.size > MAX_AVATAR_SIZE:
        messages.error(request, f'文件过大，最多 {MAX_AVATAR_SIZE // 1024 // 1024} MB')
        return redirect('/accounts/profile/')

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.avatar:
        profile.avatar.delete(save=False)
    profile.avatar = file
    profile.save()
    messages.success(request, '头像已更新')
    return redirect('/accounts/profile/')


@require_POST
@login_required(login_url='/accounts/login/')
def avatar_delete(request):
    try:
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
            messages.success(request, '已恢复默认头像')
    except UserProfile.DoesNotExist:
        pass
    return redirect('/accounts/profile/')
