from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from core.constants import (MAX_LENGTH, MAX_LENGTH_FOR_COMMENT,
                            MAX_LENGTH_FOR_POST_TEXT, MAX_LENGTH_TEXT)
from core.models import BlogModel

User = get_user_model()


class Location(BlogModel):
    name = models.CharField('Название места', max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BlogModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы латиницы,'
        ' цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BlogModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH)
    text = models.TextField('Текст', max_length=MAX_LENGTH_FOR_POST_TEXT)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        null=True,
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts_in_location'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='posts_in_category'
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Comment(models.Model):
    text = models.TextField('Комментарий', max_length=MAX_LENGTH_FOR_COMMENT)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_author'
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комменатрии'

    def __str__(self):
        return self.text[:MAX_LENGTH_TEXT]

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"post_id": self.post.pk})
