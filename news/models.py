from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '新闻分类'
        verbose_name_plural = '新闻分类'
    
    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    summary = models.TextField(max_length=500, blank=True, null=True, verbose_name='摘要')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    source = models.CharField(max_length=100, blank=True, null=True, verbose_name='来源')
    publish_time = models.DateTimeField(blank=True, null=True, verbose_name='发布时间')
    image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='图片URL')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    is_featured = models.BooleanField(default=False, verbose_name='设为头条')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = '新闻'
        ordering = ['-publish_time']
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name='新闻')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='用户')
    content = models.TextField(max_length=1000, verbose_name='评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='回复目标')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'
