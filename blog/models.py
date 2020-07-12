from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.utils.functional import cached_property

import markdown
import re
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Post(models.Model):
    # 文章标题
    title = models.CharField('标题', max_length=70)

    # 文章正文
    body = models.TextField('正文')

    # 创建时间和最后一次修改时间
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('修改时间')

    # 文章摘要，允许为空
    excerpt = models.CharField('摘要',max_length=200, blank=True)

    # 分类和标签
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)

    # 文章作者
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)

    # 记录阅读量
    views = models.PositiveIntegerField(default=0, editable=False)
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def save(self, *args, **kwargs):
        '''复写保存的方法'''
        self.modified_time = timezone.now()

        # 实例一个Markdown类，用于渲染body的文本
        md = markdown.Markdown(extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',

                                      ])
        # strip_tags 去掉 HTML 文本的全部 HTML 标签
        self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        '''自定义获取相对url路径'''
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    @cached_property
    def rich_content(self):
        return generate_rich_content(self.body)

    @property
    def toc(self):
        return self.rich_content.get("toc", "")

    @property
    def body_html(self):
        return self.rich_content.get("content", "")


def generate_rich_content(value):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify),
    ])
    content = md.convert(value)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    toc = m.group(1) if m is not None else ''
    return {"content": content, "toc": toc}
