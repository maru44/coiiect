import pytz
from urllib import parse
from django.utils import timezone, deprecation
from django.conf import settings

class TimezoneMiddleware(deprecation.MiddlewareMixin):
    @staticmethod
    def process_request(request):
        tzname = request.COOKIES.get('timezone') or settings.CLIENT_DEFAULT_TIME_ZONE
        timezone.activate(pytz.timezone(parse.unquote(tzname)))
