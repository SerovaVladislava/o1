from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Keyword(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word
    
class UnusedKeyword(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word