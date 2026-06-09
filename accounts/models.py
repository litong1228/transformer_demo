from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def avatar_upload_path(instance, filename):
    ext = (filename.rsplit('.', 1)[-1] or 'png').lower()
    return f'avatars/user_{instance.user_id}.{ext}'


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='用户'
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True, null=True,
        verbose_name='头像'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.user.username} 的资料'


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Bookmark(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='bookmarks', verbose_name='用户'
    )
    news = models.ForeignKey(
        'news.News', on_delete=models.CASCADE,
        related_name='bookmarked_by', verbose_name='新闻'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'news')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.news.title[:30]}'


class ReadingHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reading_history', verbose_name='用户'
    )
    news = models.ForeignKey(
        'news.News', on_delete=models.CASCADE,
        related_name='read_by', verbose_name='新闻'
    )
    read_count = models.PositiveIntegerField(default=1, verbose_name='阅读次数')
    first_read_at = models.DateTimeField(auto_now_add=True, verbose_name='首次阅读')
    last_read_at = models.DateTimeField(auto_now=True, verbose_name='最近阅读')

    class Meta:
        verbose_name = '阅读历史'
        verbose_name_plural = '阅读历史'
        unique_together = ('user', 'news')
        ordering = ['-last_read_at']
        indexes = [
            models.Index(fields=['user', '-last_read_at']),
        ]

    def __str__(self):
        return f'{self.user.username} 读过 {self.news.title[:30]} ×{self.read_count}'
