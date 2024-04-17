from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'text',
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        'description',
        'is_published',
    )
    search_fields = ('title',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'created_at',
        'author',
    )
    search_fields = ('author',)
