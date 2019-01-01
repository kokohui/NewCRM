from django.urls import reverse


def reverse_url(request, name, *args, **kwargs):
    base_url = reverse(name, args=args, kwargs=kwargs)
    params = request.GET.urlencode()  # 获取路径携带的路径信息
    if not params:
        return base_url
    return "{}?{}".format(base_url, params)


def rev_url(request, name, *args, **kwargs):
    base_url = reverse(name, args=args, kwargs=kwargs)
    next_url = request.GET.get('next')  # 获取路径携带的路径信息
    if next_url:
        return next_url
    return base_url
