from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProfileView, ProfileUpdateView, PostCreateView,\
    add_comment, PostUpdateView, PostDeleteView,\
    CommentUpdateView, CommentDeleteView

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<int:pk>/edit/',
         ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/',
         PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>',
         CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>',
         CommentDeleteView.as_view(), name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
