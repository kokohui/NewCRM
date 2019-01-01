from django.conf.urls import url
from rbec import views
from app1.views import account

urlpatterns = [
    url(r'^role/list/$', views.role_list, name='role_list'),
    url(r'^role/add/$', views.role, name='role_add'),
    url(r'^role/edit/(\d+)$', views.role, name='role_edit'),
    url(r'^role/del/(\d+)$', views.role_del, name='role_del'),

    url(r'^menu/list/$', views.menu_list, name='menu_list'),
    url(r'^menu/add/$', views.menu, name='menu_add'),
    url(r'^menu/edit/(\d+)$', views.menu, name='menu_edit'),
    url(r'^menu/del/(\d+)$', views.menu_del, name='menu_del'),

    url(r'^permission/edit/(\d+)$', views.permission, name='permission_edit'),
    url(r'^permission/add/$', views.permission, name='permission_add'),
    url(r'^permission/del/(\d+)$', views.permission_del, name='permission_del'),

    url(r'^multi/permissions/$', views.multi_permissions, name='multi_permissions'),
    url(r'^distribute/permissions/$', views.distribute_permissions, name='distribute_permissions')

]
