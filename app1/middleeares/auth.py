# from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.deprecation import MiddlewareMixin
from app1 import models
from django.shortcuts import redirect, reverse


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):

        if request.path_info.startswith('/admin/'):
            return
        if request.path_info in [reverse('login'), reverse('reg')]:
            return
            # 获取用户ID
        pk = request.session.get('user_id')
        user = models.UserProfile.objects.filter(pk=pk).first()
        if user:
            request.account = user
        else:
            return redirect(reverse('login'))
