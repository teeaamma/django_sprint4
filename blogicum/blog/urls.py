from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProfileView, ProfileUpdateView, PostCreateView, PostUpdateView, PostDeleteView, \
    CommentUpdateView, CommentDeleteView, add_comment, CategoryPostsView, IndexView, PostDetailView

app_name = 'blog'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # Главная страница
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),  # Детали поста
    path('category/<slug:category_slug>/', CategoryPostsView.as_view(), name='category_posts'),  # Категории постов
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),  # Профиль пользователя
    path('profile/<int:pk>/edit/', ProfileUpdateView.as_view(), name='edit_profile'),  # Редактирование профиля
    path('posts/create/', PostCreateView.as_view(), name='create_post'),  # Создание поста
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),  # Редактирование поста
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),  # Удаление поста
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),  # Добавление комментария
    path('posts/<int:post_id>/edit_comment/<int:pk>/', CommentUpdateView.as_view(), name='edit_comment'),  # Редактирование комментария
    path('posts/<int:post_id>/delete_comment/<int:pk>/', CommentDeleteView.as_view(), name='delete_comment'),  # Удаление комментария
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Статические файлы для медиа
