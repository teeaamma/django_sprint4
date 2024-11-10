from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Post, Category


def get_published_posts():
    current_time = timezone.now()
    posts = Post.objects.filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True
    ).select_related('category', 'author', 'location')
    return posts


def index(request):
    template = 'blog/index.html'
    posts = get_published_posts()[:5]

    context = {
        'post_list': posts,
    }

    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'

    current_time = timezone.now()

    post = get_object_or_404(
        Post, id=pk,
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True
    )

    context = {
        'post': post,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    current_time = timezone.now()
    post_list = category.posts.filter(
        pub_date__lte=current_time,
        is_published=True
    ).select_related('author', 'location')

    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context)
