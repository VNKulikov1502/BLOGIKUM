from django.db import models


class BlogModel(models.Model):
    """Абстрактная модель"""

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True)

    class Meta:
        abstract = True
