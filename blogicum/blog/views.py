from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    TemplateView, UpdateView, CreateView, DeleteView, ListView, DetailView
)

from .forms import PostCreateForm, CommentForm, UserUpdateForm
from .models import Post, Category, Comment


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        current_time = timezone.now()
        return Post.objects.select_related('category', 'author', 'location').filter(
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        current_time = timezone.now()
        current_user = self.request.user if self.request.user.is_authenticated else None
        return Post.objects.filter(
            Q(pub_date__lte=current_time) | Q(author=current_user),
            Q(is_published=True) | Q(author=current_user),
            Q(category__is_published=True) | Q(author=current_user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug, is_published=True)
        current_time = timezone.now()
        return Post.objects.select_related('category', 'author', 'location').filter(
            pub_date__lte=current_time,
            is_published=True,
            category=category
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        return context


class ProfileView(TemplateView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        context['profile'] = user
        posts = Post.objects.filter(author=user)
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def test_func(self):
        return self.request.user.id == self.get_object().author.id

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().id)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        return self.request.user.is_superuser or (self.request.user.id == self.get_object().author.id)

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.request.user.id == self.get_object().author.id

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().post.id)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.request.user.id == self.get_object().author.id

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.get_object().post.id})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)
