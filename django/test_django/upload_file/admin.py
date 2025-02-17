from django.contrib import admin
from .models import Category, Keyword, UnusedKeyword

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Отображение полей в списке
    search_fields = ('name',)      # Поля для поиска

# Регистрация модели Category с настройками
admin.site.register(Category, CategoryAdmin)

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'word')  # Отображение полей в списке
    search_fields = ('word',)      # Поля для поиска

# Регистрация модели Category с настройками
admin.site.register(Keyword, KeywordAdmin)


admin.site.register(UnusedKeyword)