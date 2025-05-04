# main/middleware.py
from social_core.exceptions import AuthCanceled
from django.shortcuts import redirect
from django.contrib import messages

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            messages.info(request, 'Giriş iptal edildi, lütfen tekrar deneyin.')
            return redirect('login_page')
        return None 