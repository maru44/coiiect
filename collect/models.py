from django.db import models
from django.utils import timezone
from PIL import Image
import uuid
from django.utils.translation import ugettext_lazy as _
from datetime import date
from user.models import User

class Tag(models.Model):
    class Text(models.TextChoices):
        Book = 'books', _("Books")
        Movie = 'moovie', _('Movie/Music')
        Electronics = 'ele', _('Electronics')
        PC = 'pc', _('PC')
        Drink = 'drink', _('Drink/Grocery')
        Interior = 'inte', _('Interior/Novelty')
        Commodity = 'commo', _('Commodities')
        Handmade = 'hand', _('Handmade')
        Hobby = 'hobby', _('Hobby/Toy')
        Clothes = 'clo', _('Clothes/Shoes/Bag')
        Car = 'car', _('Car/Bike')
        Sports = 'sports', _('Sports/Outdoors')
    text = models.CharField(_('Tag'), max_length=30, choices=Text.choices, blank=True, null=True)

    def __str__(self):
        return self.text

class Category(models.Model):
    name = models.CharField(_('category'), max_length=24)
    made = models.DateTimeField(_('date of made'), default=timezone.now)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(_('place'), max_length=24)
    made = models.DateTimeField(_('date of made'), default=timezone.now)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Collect(models.Model):
    id = models.SlugField(primary_key=True, editable=False)
    name = models.CharField(_('name'), max_length=24)
    product_name = models.CharField(_('product name'), max_length=32, blank=True, null=True)
    maker = models.CharField(_('maker name'), max_length=32, blank=True, null=True)
    num = models.PositiveIntegerField(_('number'), blank=True, null=True, default=1)
    saved = models.CharField(_('saved state'), max_length=36, blank=True, null=True)
    explain = models.TextField(_('explain'), blank=True, null=True)
    acq_day = models.DateField(_('day of acquisition'), blank=True, null=True)
    acq_place = models.CharField(_('place of acquisition'), max_length=36, blank=True, null=True)
    posted = models.DateTimeField(_('posted date'), default=timezone.now)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name=_('category'), blank=True, null=True, on_delete=models.SET_NULL)
    place = models.ForeignKey(Place, verbose_name=_('place'),blank=True, null=True, on_delete=models.SET_NULL)
    price = models.PositiveIntegerField(_('Price'), blank=True, null=True)
    nice_num = models.PositiveIntegerField(_('Nice'), default=0)
    public = models.BooleanField(_('public'), max_length=10, default=False)
    class State(models.TextChoices):
        NEGOTIABLE = "NEGOTIABLE", _("Negotiable")
        NONNEGOTIABLE = "NON-NEGOTIABLE", _("Non-negotiable")
        LOOKFORBUYER = "WANT-SELL", _("Looking for buyers")
        THIRSTING = "THIRSTY", _("Thirsting")
    state = models.CharField(_('state'), max_length=15, choices=State.choices, default='NON-NEGOTIABLE')
    tag = models.ManyToManyField(Tag, verbose_name='tag', blank=True)

    def __str__(self):
        return self.name

    def nice_count(self):
        return Nice.objects.filter(collect=self).count()

    def com_count(self):
        return Comment.objects.filter(collect=self).count()


class Photo(models.Model):
    photo = models.ImageField(_('picture'), upload_to='collect/', blank=True, null=True)
    collect = models.ForeignKey(Collect, verbose_name='collect', on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField(_('content'), max_length=400)
    collect = models.ForeignKey(Collect, verbose_name='collect', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    posted = models.DateTimeField(_('posted date'), default=timezone.now)

class Reply(models.Model):
    content = models.TextField(_('content'), max_length=400)
    comment = models.ForeignKey(Comment, verbose_name='comment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    posted = models.DateTimeField(_('posted date'), default=timezone.now)

class Nice(models.Model):
    collect = models.ForeignKey(Collect, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    posted = models.DateTimeField(_('date'), default=timezone.now)

class Offer(models.Model):
    target_col = models.ForeignKey(Collect, related_name="tar", on_delete=models.CASCADE)
    rec_col = models.ForeignKey(Collect, on_delete=models.CASCADE)
    posted = models.DateTimeField(_('date'), default=timezone.now)