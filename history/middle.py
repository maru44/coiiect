from collect.models import Collect, Photo, Category, Place, Comment
from user.models import User
from .models import History, LastVisit
from collect.views import Detail
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from django.utils import timezone

dview = Detail.as_view()

class LastVisitMiddleware(MiddlewareMixin):
    def process_view(self, request, dview, user, pk):
        #if self.request.user.is_authenticated():
        user = request.user
        collect = get_object_or_404(Collect, id=pk)
        if user == collect.user:
            if LastVisit.objects.filter(user=user, collect=collect):
                visit = LastVisit.objects.filter(user=user, collect=collect)
                visit.save(time=timezone.now)
                return None
            else:
                LastVisit.create(user=user, collect=collect, time=timezone.now)
                return None
        return None
        #return None

class HistoryMiddleware(MiddlewareMixin):
    def process_view(self, request, dview, user, *args, **kwargs):
        if self.request.user.is_authenticated():
            user = self.request.user
            collect = get_object_or_404(Collect, id=self.kwargs.get('pk'))
            if user != collect.user:
                if History.objects.filter(user=user, collect=collect):
                    history = History.objects.filter(user=user, collect=collect)
                    history.save(time=timezone.now)
                    return None
                else:
                    History.create(user=user, collect=collect, time=timezone.now)
                    return None
            return None
        return None
            