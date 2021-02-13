from django.contrib import admin
from .models import Collect, Category, Place, Comment, Photo, Reply, Tag, Nice

admin.site.register(Tag)
admin.site.register(Collect)
admin.site.register(Category)
admin.site.register(Place)
admin.site.register(Photo)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Nice)