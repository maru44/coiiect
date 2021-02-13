from django.contrib import admin
from .models import History, LastVisit, SearchHistory

admin.site.register(History)
admin.site.register(LastVisit)
admin.site.register(SearchHistory)