from django.db import models
from django.utils.translation import ugettext

from authnz.models import User
from utils import utils


class Rss(models.Model):
    title = models.CharField(max_length=50, unique=True, help_text=ugettext('Title of rss feed.'))
    link = models.CharField(max_length=100, unique=True, help_text=ugettext('Link of rss feed.'))
    followers = models.ManyToManyField(User, through='FollowRss')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return 'Rss: {}'.format(self.title)


class FollowRss(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rss = models.ForeignKey(Rss, on_delete=models.CASCADE)
    last_seen = models.IntegerField(default=0)


class Feed(models.Model):
    title = models.CharField(max_length=200, help_text=ugettext('Title of feed.'))
    link = models.CharField(max_length=500, help_text=ugettext('Link of feed.'))
    published = models.IntegerField(help_text=ugettext('Epoch Time of feed.'))
    description = models.CharField(max_length=2000, help_text=ugettext('Description of feed.'))
    rss = models.ForeignKey(Rss, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(User)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-published',)
        unique_together = ('link', 'published')

    def __str__(self):
        return 'Feed: {}'.format(self.title)


class Comment(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, help_text=ugettext('Body of comment.'))
    is_deleted = models.BooleanField(default=False)
    created = models.IntegerField(default=utils.now_time(), help_text=ugettext('Epoch Time of comment creation.'))

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Comment: {}'.format(self.body)
