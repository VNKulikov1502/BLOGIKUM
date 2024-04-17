from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse

from blog.models import Comment, Post

from .forms import CommentForm, PostForm


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверяет авторство публикаций"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class BasePostMixin(LoginRequiredMixin):
    """Базовая логика для работы публикаций."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class BaseCommentMixin(OnlyAuthorMixin):
    """Базовая логика для удаления и редактирования комментов."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id).comment.all()

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})
