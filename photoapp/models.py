from django.db import models
from django.contrib.auth.models import User, Group
from registration.signals import user_activated
from django.dispatch import receiver


class Album(models.Model):
    title = models.CharField(max_length=128)
    photog = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    public = models.BooleanField()

    def __unicode__(self):
        return self.title


class Photo(models.Model):
    height = models.PositiveIntegerField(blank=True, null=True, default=0)
    width = models.PositiveIntegerField(blank=True, null=True, default=0)
    image = models.ImageField(
        upload_to='%Y/%m/%d',
        height_field='height',
        width_field='width',
        )
    caption = models.TextField(blank=True)
    photog = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Photo' + unicode(self.pk)

    def caption_rep(self):
        if self.caption == '':
            return 'Uncaptioned'
        return self.caption


class Tag(models.Model):
    title = models.TextField(max_length=64)
    photos = models.ManyToManyField(Photo)

    def __unicode__(self):
        return self.title


@receiver(user_activated)
def apply_perms(sender, **kwargs):
    auths = Group.objects.get(name='Activated')
    auths.user_set.add(kwargs['user'])
