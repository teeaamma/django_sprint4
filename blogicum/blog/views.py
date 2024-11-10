from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from blog.models import Post, Category
from django.views.generic import TemplateView,\
    UpdateView, CreateView, DeleteView

from .forms import PostCreateForm, CommentForm, UserUpdateForm
from .models import Comment


def index(request):
    template = 'blog/index.html'
    current_time = timezone.now()
    posts = Post.objects. \
        select_related('category', 'author', 'location'). \
        filter(
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True
        )
    for post in posts:
        post.comment_count = Comment.objects.filter(post=post).count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'post_list': posts,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    current_time = timezone.now()
    current_user = None
    if request.user.is_authenticated:
        current_user = request.user
    post = get_object_or_404(
        Post,
        Q(pub_date__lte=current_time) | Q(author=current_user),
        Q(is_published=True) | Q(author=current_user),
        Q(category__is_published=True) | Q(author=current_user),
        id=post_id,

    )

    comments = Comment.objects.filter(post=post)
    template = 'blog/detail.html'
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(Category,
                                 slug=category_slug, is_published=True)

    current_time = timezone.now()
    posts = Post.objects. \
        select_related('category', 'author', 'location'). \
        filter(
            pub_date__lte=current_time,
            is_published=True,
            category=category
        )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


class ProfileView(TemplateView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        user = get_object_or_404(get_user_model(), username=username)
        context['profile'] = user
        posts = Post.objects.filter(author=user)
        for post in posts:
            post.comment_count = Comment.objects.filter(post=post).count()
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        context = self.get_context_data()
        user = context['user']
        user_username = user.username
        return reverse('blog:profile', kwargs={'username': user_username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        print(instance)
        instance.save()
        return super().form_valid(instance)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def test_func(self):
        print('its work')
        return self.request.user.id == self.get_object().author.id

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        print('its work')
        return self.request.user.is_superuser or \
            (self.request.user.id == self.get_object().author.id)

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        post.comment_count += 1
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.request.user.id == self.get_object().author.id

    def handle_no_permission(self):
        comment = self.get_object()
        post = comment.post
        print(post.id)
        return redirect('blog:post_detail', post_id=post.id)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.request.user.id == self.get_object().author.id

    def get_success_url(self):
        context = self.get_context_data()
        comment = context['comment']
        post = comment.post
        return reverse('blog:post_detail', kwargs={'post_id': post.id})
