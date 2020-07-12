import re
import markdown

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.utils.text import slugify

from markdown.extensions.toc import TocExtension
from pure_pagination import PaginationMixin
from .models import Post, Category, Tag


# 文章详情视图类
class PostDetailView(DetailView):
    model= Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    # def get_object(self, queryset=None):
    #     # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
    #     post = super().get_object(queryset=None)
    #     md = markdown.Markdown(extensions=[
    #         'markdown.extensions.extra',
    #         'markdown.extensions.codehilite',
    #         TocExtension(slugify=slugify),
    #     ])
    #     post.body = md.convert(post.body)
    #     m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    #     post.toc = m.group(1) if m is not None else ''
    #     return post


# 首页视图类
class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10


# 分类视图类
class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)



# 归档视图类
class ArchiveView(IndexView):
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchiveView, self)\
            .get_queryset()\
            .filter(created_time__year=year, created_time__month=month)

# 标签视图类
class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


# 作者分类视图类
class AuthorView(IndexView):
    def get_queryset(self):
        author = self.kwargs.get('pk')
        return super(AuthorView, self).get_queryset().filter(author=author)
