from django.conf import settings


def init_permisson(request, obj):
    """
    权限信息的初始化
    保存权限信息和菜单的信息
    :param request:
    :param obj:
    :return:
    """
    ret = obj.roles.all().filter(permissions__url__isnull=False).values('permissions__url',
                                                                        'permissions__title',
                                                                        'permissions__menu__title',
                                                                        'permissions__menu__icon',
                                                                        'permissions__menu__weight',
                                                                        'permissions__menu_id',
                                                                        'permissions__parent_id',
                                                                        'permissions__parent__name',
                                                                        'permissions__id',
                                                                        'permissions__name', ).distinct()

    print('ret', ret)
    # 存放权限信息
    permission_dict = {}
    # 存放菜单信息
    menu_dict = {}
    for item in ret:
        # 将所有的权限信息添加到 per_list
        permission_dict[item['permissions__name']] = ({'url': item['permissions__url'],
                                                       'id': item['permissions__id'],
                                                       'pid': item['permissions__parent_id'],
                                                       'pname': item['permissions__parent__name'],
                                                       'title': item['permissions__title'],
                                                       })
        # 构造菜单的数据结构
        menu_id = item.get('permissions__menu_id')
        # 表示当前权限是不做菜单的权限
        if not menu_id:
            continue
        # 可以做菜单的权限
        if menu_id not in menu_dict:
            menu_dict[menu_id] = {
                'title': item['permissions__menu__title'],  # 一级菜单标题
                'icon': item['permissions__menu__icon'],
                'weight': item['permissions__menu__weight'],
                'children': [{'title': item['permissions__title'],
                              'url': item['permissions__url'],
                              'id': item['permissions__id'], }]
            }
        else:
            menu_dict[menu_id]['children'].append(
                {'title': item['permissions__title'], 'url': item['permissions__url'],
                 'id': item['permissions__id'], })

    print(permission_dict)

    # 保存权限信息
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    # print('per_list', per_list)
    # 保存菜单信息
    request.session[settings.PERMISSION_MENU_KEY] = menu_dict
    # print('menu_list', menu_list)
