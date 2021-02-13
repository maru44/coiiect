from django.db import models
from collect.models import Collect, Photo, Comment, Reply
from user.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class History(models.Model):
    collect = models.ForeignKey(Collect, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(_('time'), default=timezone.now)

class LastVisit(models.Model):
    collect = models.ForeignKey(Collect,on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(_('time'), default=timezone.now)

class SearchHistory(models.Model):
    text = models.TextField(_('text'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(_('time'), default=timezone.now)
