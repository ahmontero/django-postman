from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from .models import Message

login_required_m = method_decorator(login_required)
never_cache_m = method_decorator(never_cache)


def ajax_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return wrapper
ajax_required_m = method_decorator(ajax_required)


class AjaxMixin(object):
    """Common code to Ajax calls."""

    @never_cache_m
    @ajax_required_m
    @login_required_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AjaxUnreadCountView(AjaxMixin, View):
    """Return the number of unread messages for a user."""
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return JsonResponse({'unread_count': Message.objects.inbox_unread_count(request.user)})
