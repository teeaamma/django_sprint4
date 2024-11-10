from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('blog.urls')),
    path('', include('blog.urls')),
    path('', include('pages.urls')),
    path('admin/', admin.site.urls),
]
