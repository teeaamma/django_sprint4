from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.urls import reverse

User = get_user_model()


class AbstrCl(models.Model):
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(AbstrCl):
    title = models.CharField("Заголовок", max_length=256)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; разрешены символы"
                  " латиницы, цифры, дефис и подчёркивание."
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(AbstrCl):
    name = models.CharField(
        "Название места",
        max_length=256
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(AbstrCl):
    title = models.CharField(
        "Заголовок",
        max_length=256
    )
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату и время в будущем "
                  "— можно делать отложенные публикации."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="posts"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Местоположение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
        verbose_name="Категория"
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)
    comment_count = models.IntegerField("Количество комментариев", default=0)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.id})


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.id})
