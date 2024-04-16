from datetime import datetime as dt

from blog.models import Category, Comment, Post
from core.constants import PAGINATOR
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CommentForm, PostForm

User = get_user_model()


def get_related_post_list():
    """Функция возвращает объекты модели Post со связанными моделями."""
    return Post.objects.select_related(
        'category', 'location', 'author')


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


class IndexListView(ListView):
    """Отображение всех публикаций."""

    model = Post
    paginate_by = PAGINATOR
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = get_related_post_list().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=dt.now()
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')
        return queryset


class PostCreateView(BasePostMixin, CreateView):
    """Создание публикации."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(BasePostMixin, OnlyAuthorMixin, UpdateView):
    """Редактирование публикации."""

    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )

    def handle_no_permission(self):
        post_id = self.kwargs['post_id']
        return redirect('blog:post_detail', post_id=post_id)


class PostDeleteView(BasePostMixin, OnlyAuthorMixin, DeleteView):
    """Удалениe публикации."""

    pk_url_kwarg = 'post_id'


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    """Редактирование аккаунта."""

    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def test_func(self):
        object = self.get_object()
        return object.username == self.request.user.username


class CommentDeleteView(BaseCommentMixin, DeleteView):
    """Удаление комментария."""

    ...


class CommentUpdateView(BaseCommentMixin, UpdateView):
    """Редактирование комментария."""

    ...


@login_required
def add_comment(request, post_id):
    """Представление для добавления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


def get_profile(request, username):
    """Представление профиля пользователя."""
    profile = get_object_or_404(User, username=username)
    publications = get_related_post_list().filter(
        author__username=username
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')
    paginator = Paginator(publications, PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Функция отображает отдельную публикацию."""
    post = get_object_or_404(
        get_related_post_list(),
        pk=post_id,
    )
    if request.user == post.author:
        form = CommentForm()
        comment = post.comment.select_related('author')
        context = {
            'post': post,
            'form': form,
            'comments': comment
        }
        return render(request, 'blog/detail.html', context)
    post = get_object_or_404(
        get_related_post_list(),
        is_published=True,
        pub_date__lte=dt.now(),
        category__is_published=True,
        pk=post_id,
    )
    form = CommentForm()
    comment = post.comment.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comment
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """Функция отображает публикации в категории."""
    post_list = Post.objects.filter(
        is_published=True,
        category__slug=category_slug,
        pub_date__lte=dt.now(),
    ).annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')
    paginator = Paginator(post_list, PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    context: dict = {'category': category,
                     'page_obj': page_obj}
    return render(request, 'blog/category.html', context)
