from django.db import models
from django.contrib.auth.models import User


class Album(models.Model):
    title = models.CharField(max_length=128)
    photog = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Photo(models.Model):
    caption = models.TextField(blank=True)
    photog = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    title = models.TextField(max_length=64)
    photos = models.ManyToManyField(Photo)
