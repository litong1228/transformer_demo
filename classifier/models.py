from django.db import models
from django.contrib.auth.models import User

class ClassificationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    text = models.TextField(verbose_name='待分类文本')
    predicted_category = models.CharField(max_length=100, verbose_name='预测分类')
    confidence = models.FloatField(verbose_name='置信度')
    model_used = models.CharField(max_length=50, default='albert', verbose_name='使用模型')
    elapsed_ms = models.IntegerField(default=0, verbose_name='推理耗时(ms)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='分类时间')

    class Meta:
        verbose_name = '分类结果'
        verbose_name_plural = '分类结果'

    def __str__(self):
        return f"{self.predicted_category} - {self.confidence:.2f} ({self.model_used})"

class BatchClassification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    total_count = models.IntegerField(verbose_name='总条数')
    success_count = models.IntegerField(verbose_name='成功条数')
    model_used = models.CharField(max_length=50, default='albert', verbose_name='使用模型')
    elapsed_ms = models.IntegerField(default=0, verbose_name='总耗时(ms)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '批量分类记录'
        verbose_name_plural = '批量分类记录'

    def __str__(self):
        return f"{self.file_name} - {self.total_count}条 ({self.model_used})"


class BatchClassificationItem(models.Model):
    batch = models.ForeignKey(
        BatchClassification, on_delete=models.CASCADE,
        related_name='items', verbose_name='所属批次',
    )
    row_index = models.IntegerField(verbose_name='行号')
    text = models.TextField(verbose_name='文本')
    predicted_category = models.CharField(max_length=100, verbose_name='预测分类')
    confidence = models.FloatField(verbose_name='置信度')

    class Meta:
        verbose_name = '批量分类明细'
        verbose_name_plural = '批量分类明细'
        ordering = ['batch_id', 'row_index']
        indexes = [models.Index(fields=['batch', 'row_index'])]

    def __str__(self):
        return f"#{self.batch_id}-{self.row_index} {self.predicted_category}"
