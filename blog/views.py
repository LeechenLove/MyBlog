import re
import markdown

from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify

from markdown.extensions.toc import TocExtension

from .models import Post, Category, Tag


# 博客首页函数
def index(request):
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 文章详情页面函数
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    md = markdown.Markdown(extensions=[
                             'markdown.extensions.extra',
                             'markdown.extensions.codehilite',
                             TocExtension(slugify=slugify),
                         ])
    post.body = md.convert(post.body)

    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    return render(request, 'blog/detail.html', context={'post': post})


# 归档视图
def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 分类视图
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 标签视图
def tag(request, pk):
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t)
    return render(request, 'blog/index.html', context={'post_list': post_list})


# 作者视图
def author(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post_list = Post.objects.filter(author=post.author)
    return render(request, 'blog/index.html', context={'post_list': post_list})