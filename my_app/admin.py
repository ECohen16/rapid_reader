from django.contrib import admin

# Register your models here.
from my_app.models import Article, Text, Reader, ReadingList, ArticleSource
class TextInline(admin.TabularInline):
    model = Text
    extra = 0

class ArticleAdmin(admin.ModelAdmin):
    fields = ['name','short_source','url_address','date_added']
    inlines = [TextInline]
    list_display = ('name','short_source','url_address','date_added')
    list_filter = ['name']
    search_field =['name']

class ReadingListInline(admin.StackedInline):
    model = ReadingList
    extra = 2

class ReaderAdmin(admin.ModelAdmin):
    inlines = [ReadingListInline]

class ArticleSourceAdmin(admin.ModelAdmin):
    fields = ['source_name']

admin.site.register(Article,ArticleAdmin)
admin.site.register(Reader,ReaderAdmin)
admin.site.register(ArticleSource,ArticleSourceAdmin)