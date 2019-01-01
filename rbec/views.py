from django.shortcuts import render, reverse, redirect, HttpResponse
from rbec.forms import RoleForm, MenuForm, PermissionForm, MultiPermissionForm
from rbec import models
from django.db.models import Q
from collections import OrderedDict
from app1.models import UserProfile


# Create your views here.
# 展示角色
def role_list(request):
    all_role = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'all_role': all_role})


def role(request, edit_id=None):
    obj = models.Role.objects.filter(pk=edit_id).first()
    form_obj = RoleForm(instance=obj)
    if request.method == 'POST':
        form_obj = RoleForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('role_list'))
    return render(request, 'rbac/role_form.html', {'form_obj': form_obj})


def role_del(request, del_id):
    models.Role.objects.filter(pk=del_id).delete()
    return redirect(reverse('role_list'))


def menu_list(request, ):
    mid = request.GET.get('mid')
    all_menus = models.Menu.objects.all()

    if mid:
        all_permissions = models.Permission.objects.filter(Q(menu_id=mid) | Q(parent__menu_id=mid))  # 和menu 表一一对应

    else:
        all_permissions = models.Permission.objects.all()

    permission_query = all_permissions.values()
    print('permission_query', permission_query)
    permission_dict = OrderedDict()

    # print(permission_query)
    for item in permission_query:
        if item.get('menu_id'):
            permission_dict[item['id']] = item
            item['children'] = []

    for item in permission_query:
        pid = item.get('parent_id')
        if pid:
            permission_dict[pid]['children'].append(item)

    print(permission_dict)
    return render(request, 'rbac/menu_list.html',
                  {'all_menus': all_menus, 'all_permissions': permission_dict, 'mid': mid})


def menu(request, edit_id=None):
    obj = models.Menu.objects.filter(pk=edit_id).first()
    form_obj = MenuForm(instance=obj)
    if request.method == 'POST':
        form_obj = MenuForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbec:menu_list'))
    return render(request, 'rbac/menu_form.html', {'form_obj': form_obj})


def menu_del(request, del_id):
    models.Menu.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbec:menu_list'))


def permission(request, edit_id=None):
    obj = models.Permission.objects.filter(pk=edit_id).first()
    form_obj = PermissionForm(instance=obj)
    if request.method == 'POST':
        form_obj = PermissionForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbec:menu_list'))
    return render(request, 'rbac/menu_form.html', {'form_obj': form_obj})


def permission_del(request, del_id):
    models.Permission.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbec: menu_list'))


from django.forms import modelformset_factory, formset_factory
from rbec.service.routes import get_all_url_dict


def multi_permissions(request):
    post_type = request.GET.get('type')
    # 用做编辑和删除
    FormSet = modelformset_factory(models.Permission, MultiPermissionForm, extra=0)
    # 用做新增
    AddFormSet = formset_factory(MultiPermissionForm, extra=0)
    # 数据库中所有的权限信息
    permissions = models.Permission.objects.all()
    # 项目路由系统中的所有URL
    router_dict = get_all_url_dict(ignore_namespace_list=['admin'])

    # 数据库中权限的所有的别名
    permissions_name_set = set([i.name for i in permissions])
    # 路由系统中所有的别名
    router_name_set = set(router_dict.keys())

    # 带插入到数据库中权限的别名
    add_name_set = router_name_set - permissions_name_set
    add_formset = AddFormSet(initial=[row for name, row in router_dict.items() if name in add_name_set])

    if request.method == 'POST' and post_type == 'add':
        add_formset = AddFormSet(request.POST)
        if add_formset.is_valid():
            permission_obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]

            query_list = models.Permission.objects.bulk_create(permission_obj_list)

            for i in query_list:
                permissions_name_set.add(i.name)
            add_formset = AddFormSet()

    del_name_set = permissions_name_set - router_name_set
    del_formset = FormSet(queryset=models.Permission.objects.filter(name__in=del_name_set))

    update_name_set = permissions_name_set & router_name_set
    update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    if request.method == 'POST' and post_type == 'update':
        update_formset = FormSet(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'del_formset': del_formset,
            'update_formset': update_formset,
            'add_formset': add_formset,
        }
    )


def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 获取所有的用户
    user_list = UserProfile.objects.all()

    # 当前用户所拥有的角色
    user_has_roles = UserProfile.objects.filter(id=uid).values('id', 'roles')

    user_has_roles_dict = {item['roles']: None for item in user_has_roles}
    """
    user_has_roles_dict = { 角色的id：None  }
    """
    # 所有的角色
    role_list = models.Role.objects.all()

    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid).values('id', 'permissions')
    elif uid and not rid:
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        role_has_permissions = []

    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    """"
    role_has_permissions_dict = { 权限的id ：None  }
    """

    all_menu_list = []
    """
    all_menu_list  = [
        { 'id', 'title'， ‘children' : [
            { 'id', 'title', 'menu_id' , 'children': [
            {'id', 'title', 'parent_id'}
        ] }
           ]   },
        {'id': None, 'title': '其他', 'children': [
         {'id', 'title', 'parent_id'}
        ]}
    ]
    """
    queryset = models.Menu.objects.values('id', 'title')
    menu_dict = {}

    """
    menu_dict = { 一级菜单的id ： { 'id', 'title'，
    ‘children' : [
        { 'id', 'title', 'menu_id' , 'children': [
            {'id', 'title', 'parent_id'}
        ] }
     ]   },
             None : {'id': None, 'title': '其他', 'children': [
               {'id', 'title', 'parent_id'}
             ]}

    }
    """

    for item in queryset:
        item['children'] = []  # 放二级菜单  父权限
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other
    # 二级菜单  父权限
    root_permission = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')

    root_permission_dict = {}

    """
    root_permission_dict =  { 父权限的id: { 'id', 'title', 'menu_id' , 'children': [
        {'id', 'title', 'parent_id'}
    ] }  }
    """

    for per in root_permission:
        per['children'] = []  # 放子权限
        nid = per['id']
        menu_id = per['menu_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    # 除了父权限的其他的权限
    node_permission = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)

    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list': user_list,
            'role_list': role_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,
            'all_menu_list': all_menu_list,
            'uid': uid,
            'rid': rid
        }
    )
