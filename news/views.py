from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.core.paginator import Paginator
from django.db.models import F, Count, ExpressionWrapper, IntegerField
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import News, Category, Comment
from accounts.models import Bookmark


def _bookmarked_ids_for(request, page):
    """返回当前用户在这一页里已收藏的 news.id 集合 (匿名用户返回空集)。"""
    if not request.user.is_authenticated:
        return set()
    page_ids = [n.id for n in page.object_list]
    if not page_ids:
        return set()
    return set(
        Bookmark.objects
        .filter(user=request.user, news_id__in=page_ids)
        .values_list('news_id', flat=True)
    )
import requests
from urllib.parse import urlparse


_ALLOWED_IMG_HOSTS = ('chinanews.com.cn', 'chinanews.com')


def image_proxy(request):
    url = request.GET.get('url', '')
    if not url:
        return HttpResponseBadRequest('missing url')
    host = urlparse(url).hostname or ''
    if not any(host.endswith(h) for h in _ALLOWED_IMG_HOSTS):
        return HttpResponseBadRequest('host not allowed')
    try:
        r = requests.get(
            url,
            timeout=10,
            proxies={'http': None, 'https': None},
            headers={'User-Agent': 'Mozilla/5.0'},
        )
    except requests.RequestException:
        return HttpResponse(status=502)
    resp = HttpResponse(r.content, status=r.status_code,
                        content_type=r.headers.get('Content-Type', 'image/jpeg'))
    resp['Cache-Control'] = 'public, max-age=86400'
    return resp


def home(request):
    # 未登录 -> 着陆页
    if not request.user.is_authenticated:
        has_image_for_landing = News.objects.exclude(image_url__isnull=True).exclude(image_url='')
        hero_lead = has_image_for_landing.filter(is_featured=True).first() or has_image_for_landing.first()
        curated_lead = (
            has_image_for_landing.exclude(id=hero_lead.id if hero_lead else 0)
            .order_by('-publish_time').first()
        )
        excluded_ids = [n.id for n in (hero_lead, curated_lead) if n]
        curated_side = list(
            News.objects.exclude(id__in=excluded_ids).order_by('-publish_time')[:3]
        )
        from django.db.models import Count as _Count
        classified_today_count = News.objects.count()  # 占位:用总条数代替
        return render(request, 'news/landing.html', {
            'hero_lead': hero_lead,
            'curated_lead': curated_lead,
            'curated_side': curated_side,
            'classified_today': f'{classified_today_count:,}',
            'trust_count': '86,000+',
        })

    # 已登录 -> 完整 feed
    # 头条：管理员后台勾选的"头条"优先（必须有图）；不够 3 条用最新有图补齐
    has_image = News.objects.exclude(image_url__isnull=True).exclude(image_url='')
    featured = list(has_image.filter(is_featured=True)[:3])
    if len(featured) < 3:
        need = 3 - len(featured)
        featured_ids = [n.id for n in featured]
        fallback = list(
            has_image.exclude(id__in=featured_ids).filter(is_featured=False)[:need]
        )
        headlines = featured + fallback
    else:
        headlines = featured
    headline_ids = [n.id for n in headlines]

    # 最新新闻：排除头条后的接下来 12 条
    latest_news = list(News.objects.exclude(id__in=headline_ids)[:12])

    # 热门新闻：综合热度 = 浏览量 + 收藏数 * 5
    popular_qs = (
        News.objects
        .annotate(bookmark_total=Count('bookmarked_by'))
        .annotate(
            hot_score=ExpressionWrapper(
                F('view_count') + F('bookmark_total') * 5,
                output_field=IntegerField(),
            )
        )
        .order_by('-hot_score', '-publish_time')
    )
    popular_news = list(popular_qs[:5])
    # 给 feed 模板的"热门新闻(侧栏)" / "热门新闻(右下卡)" 用,与上一份错开避免重复
    trending_news = list(popular_qs[:4])
    recommended_news = list(popular_qs[4:7])

    # 分类专区：从首页希望突出的分类中各取最新 4 条
    featured_category_names = ['国际', '财经', '社会', '体育', '文化', '健康']
    category_sections = []
    for name in featured_category_names:
        cat = Category.objects.filter(name=name).first()
        if not cat:
            continue
        items = list(
            News.objects.filter(category=cat).order_by('-publish_time')[:4]
        )
        if items:
            category_sections.append({'category': cat, 'items': items})

    categories = Category.objects.all()

    # 今日类别分布: 按各分类的新闻条数算占比 (展示全部 10 个类别)
    SLUG_MAP = {
        '科技': 'tech', '体育': 'sports', '财经': 'finance', '娱乐': 'ent',
        '时政': 'politics', '政治': 'politics', '军事': 'politics',
        '国际': 'politics', '台湾': 'politics',
        '教育': 'edu', '健康': 'health', '医疗': 'health',
        '社会': 'society', '家居': 'society', '文化': 'society', '生活': 'society',
        '游戏': 'game', '电竞': 'game',
        '房产': 'property', '汽车': 'property',
        '时尚': 'ent',
    }
    cat_rows = list(
        Category.objects.annotate(n=Count('news')).order_by('-n')[:10]
    )
    total_n = sum(r.n for r in cat_rows) or 1
    category_breakdown = [
        {
            'name': c.name,
            'count': c.n,
            'percent': round(c.n * 100 / total_n),
            'slug': SLUG_MAP.get((c.name or '').strip(), 'society'),
        }
        for c in cat_rows
    ]
    total_reads_today = sum(r.n for r in cat_rows)

    return render(request, 'news/home.html', {
        'headlines': headlines,
        'latest_news': latest_news,
        'popular_news': popular_news,
        'trending_news': trending_news,
        'recommended_news': recommended_news,
        'category_breakdown': category_breakdown,
        'category_sections': category_sections,
        'categories': categories,
        'total_reads_today': total_reads_today,
    })


def news_list(request, category_id=None):
    if category_id:
        news_list = News.objects.filter(category_id=category_id)
        category = get_object_or_404(Category, id=category_id)
    else:
        news_list = News.objects.all()
        category = None

    # 分页（每页 12 条 = 3 列 × 4 行，刚好填满网格）
    paginator = Paginator(news_list, 12)
    page = request.GET.get('page', 1)
    news = paginator.get_page(page)

    # 获取所有分类（带文章数,供导航 chip 展示）
    categories = Category.objects.annotate(news_count=Count('news')).order_by('name')

    # 侧边栏热门新闻：综合热度（与首页一致）
    popular_news = list(
        News.objects
        .annotate(bookmark_total=Count('bookmarked_by'))
        .annotate(
            hot_score=ExpressionWrapper(
                F('view_count') + F('bookmark_total') * 5,
                output_field=IntegerField(),
            )
        )
        .order_by('-hot_score', '-publish_time')[:5]
    )

    return render(request, 'news/news_list.html', {
        'news': news,
        'news_list': news,
        'page_obj': news,
        'is_paginated': news.has_other_pages(),
        'category': category,
        'categories': categories,
        'all_categories': categories,
        'total_count': paginator.count,
        'popular_news': popular_news,
        'bookmarked_ids': _bookmarked_ids_for(request, news),
    })


def news_detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    # 浏览量原子自增
    News.objects.filter(id=news_id).update(view_count=F('view_count') + 1)
    news.view_count += 1
    # 获取相关新闻
    related_news = News.objects.filter(category=news.category).exclude(id=news_id)[:5]
    # 获取所有分类
    categories = Category.objects.all()

    # 收藏状态 + 阅读历史（仅登录用户）
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = news.bookmarked_by.filter(user=request.user).exists()
        from accounts.models import ReadingHistory
        history, created = ReadingHistory.objects.get_or_create(
            user=request.user, news=news
        )
        if not created:
            ReadingHistory.objects.filter(id=history.id).update(
                read_count=F('read_count') + 1
            )
    bookmark_count = news.bookmarked_by.count()

    # 侧边栏热门新闻：综合热度（与首页一致），排除当前文章
    popular_news = list(
        News.objects
        .exclude(id=news_id)
        .annotate(bookmark_total=Count('bookmarked_by'))
        .annotate(
            hot_score=ExpressionWrapper(
                F('view_count') + F('bookmark_total') * 5,
                output_field=IntegerField(),
            )
        )
        .order_by('-hot_score', '-publish_time')[:5]
    )

    # 评论区：只取顶层评论，回复通过 replies 反查
    # 评论按发布时间倒序显示(最新的在最上面)
    top_comments = (
        news.comments.filter(parent__isnull=True)
        .select_related('user', 'user__profile')
        .order_by('-created_at')
    )
    comment_count = news.comments.count()

    return render(request, 'news/news_detail.html', {
        'news': news,
        'related_news': related_news,
        'categories': categories,
        'is_bookmarked': is_bookmarked,
        'bookmark_count': bookmark_count,
        'popular_news': popular_news,
        'top_comments': top_comments,
        'comments': top_comments,
        'comment_count': comment_count,
        'can_comment': request.user.is_authenticated,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        news_list = News.objects.filter(title__icontains=query) | News.objects.filter(content__icontains=query)
    else:
        news_list = News.objects.none()
    
    # 分页（同列表页 12 条）
    paginator = Paginator(news_list, 12)
    page = request.GET.get('page', 1)
    news = paginator.get_page(page)

    # 获取所有分类
    categories = Category.objects.all()

    return render(request, 'news/search_result.html', {
        'news': news,
        'news_list': news,
        'page_obj': news,
        'is_paginated': news.has_other_pages(),
        'total_count': paginator.count,
        'query': query,
        'categories': categories,
        'bookmarked_ids': _bookmarked_ids_for(request, news),
    })


@login_required(login_url='/accounts/login/')
@require_POST
def add_comment(request, news_id):
    news = get_object_or_404(News, id=news_id)
    content = request.POST.get('content', '').strip()
    parent_id = request.POST.get('parent_id', '')

    if not content:
        messages.error(request, '评论内容不能为空')
        return redirect('/detail/{}/'.format(news_id))

    if len(content) > 1000:
        messages.error(request, '评论内容不能超过1000字')
        return redirect('/detail/{}/'.format(news_id))

    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(id=int(parent_id), news=news)
        except (Comment.DoesNotExist, ValueError):
            pass

    Comment.objects.create(
        news=news,
        user=request.user,
        content=content,
        parent=parent,
    )
    messages.success(request, '评论成功')
    return redirect('/detail/{}/#comments'.format(news_id))


@login_required(login_url='/accounts/login/')
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, '无权删除此评论')
        return redirect('/detail/{}/'.format(comment.news_id))
    news_id = comment.news_id
    comment.delete()
    messages.success(request, '评论已删除')
    return redirect('/detail/{}/#comments'.format(news_id))
