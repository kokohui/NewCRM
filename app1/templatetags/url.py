from django import template
from django.urls import reverse
from django.http import QueryDict

register = template.Library()


@register.simple_tag()
def reverse_url(request, name, *args, **kwargs):
    """
    反向解析生成URL, 拼接参数
    :return:
    """
    # 根据传的url 别名和参数反向解析生成基本的URL
    base_url = reverse(name, args=args, kwargs=kwargs)
    # 从当前的URL上获取参数   query=1&page=2
    params = request.GET.urlencode()
    if not params:
        return base_url
    return "{}?{}".format(base_url, params)


@register.simple_tag()
def rev_url(request, name, *args, **kwargs):
    """
    get_full_path: app1/customer_list/?page=2
    QueryDict: mutable 不改为True 的话, 无法添加参数
    url:
    urlencode():
    :return:
    """
    base_url = reverse(name, args=args, kwargs=kwargs)
    url = request.get_full_path()
    qd = QueryDict(mutable=True)
    qd['next'] = url
    return "{}?{}".format(base_url, qd.urlencode())
