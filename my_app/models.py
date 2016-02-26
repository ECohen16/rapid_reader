from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    name = models.CharField(max_length=100) #article headline
    short_source = models.CharField(max_length=10) #WSJ, etc.
    url_address = models.CharField(max_length=140, blank=True, null=True)
    date_added = models.DateTimeField() #When added to database
    def __str__(self):
        return self.short_source + ": "+ self.name

class Text(models.Model):
    article_identifier = models.ForeignKey(Article)
    article_text = models.CharField(max_length=50000)
    def __str__(self):
        return self.article_text

class Reader(models.Model):
    user = models.OneToOneField(User)
    account_number = models.CharField(max_length=10)

class ReadingList(models.Model):
    account_holder = models.ForeignKey(Reader)
    temp_field = models.FloatField(default=0.0)

class ArticleSource(models.Model):
    source_name = models.CharField(max_length=30)
    def __str__(self):
        return self.source_name