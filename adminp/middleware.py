from django.contrib.auth import logout
from django.http import HttpResponseForbidden

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            return HttpResponseForbidden("Your account has been blocked. Please contact the administrator.")
        return response
