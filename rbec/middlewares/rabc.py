from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponse, redirect, reverse
import re


class RbecMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 1. 获取当前访问的URL
        url = request.path_info

        # 白名单
        for i in settings.WHITE_LIST:
            if re.match(i, url):
                return

        # 2. 获取当前用户的权限信息
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if not permission_dict:
            return redirect(reverse('login'))

        # 需要登录但是不需要进行权限校验的列表
        for i in settings.NO_PERMISSION_LIST:
            if re.match(i, url):
                return

        # 路径导航
        setattr(request, settings.BREADCRUMB, [
            {'url': '/index/', 'title': '首页'}
        ])

        # 3. 权限的校验

        for i in permission_dict.values():
            if re.match(r"^{}$".format(i['url']), url):
                pid = i.get('pid')
                id = i.get('id')
                pname = i.get('pname')
                if pid:
                    #  有PID表示当前访问的权限是子权限   它有父权限 要让这个父权限展开
                    # request.current_parent_id = pid
                    setattr(request, settings.CURRENT_MENU, pid)
                    p_dict = permission_dict[pname]  # 父权限的信息
                    print('p_dict', p_dict)
                    getattr(request, settings.BREADCRUMB).append({'url': p_dict['url'], 'title': p_dict['title']})
                    getattr(request, settings.BREADCRUMB).append({'url': i['url'], 'title': i['title']})

                else:
                    # 表示当前访问的权限是父权限  要让自己展开
                    # request.current_parent_id = id
                    setattr(request, settings.CURRENT_MENU, id)

                    # 路径导航
                    getattr(request, settings.BREADCRUMB).append({'url': i['url'], 'title': i['title']})

                return
        # 拒绝访问
        return HttpResponse('没有访问权限')
