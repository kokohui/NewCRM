"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from app1.views import consultant
from app1.views import teacher

urlpatterns = [
    # 公户
    url(r'^customer_list/', consultant.CustomerList.as_view(), name='customer_list'),
    # 私户
    url(r'^my_customer/', consultant.CustomerList.as_view(), name='my_customer'),

    url(r'^user_list/', consultant.user_list, name='user_list'),

    # 添加
    # url(r'^customer_add/', views.customer_add, name='customer_add'),
    url(r'^customer_add/', consultant.customer_change, name='customer_add'),
    # 编辑
    # url(r'^customer_edit/(\d+)/', views.customer_edit, name='customer_edit'),
    url(r'^customer_edit/(\d+)/', consultant.customer_change, name='customer_edit'),

    # 展示跟进记录表
    url(r'^consult_list/(0)/', consultant.ConsultList.as_view(), name='all_consult_list'),
    url(r'^consult_list/(?P<customer_id>\d+)/', consultant.ConsultList.as_view(), name='consult_list'),
    url(r'^consult_add/', consultant.consult_add, name='consult_add'),
    url(r'^consult_edit/(\d+)', consultant.consult_edit, name='consult_edit'),

    # 展示报名记录
    url(r'^enrollment_list/(?P<customer_id>\d+)/', consultant.EnrollmentList.as_view(), name='enrollment_list'),
    # 添加报名记录
    url(r'^enrollment_add/(?P<customer_id>\d+)', consultant.enrollment, name='enrollment_add'),
    url(r'^enrollment_edit/(?P<record_id>\d+)', consultant.enrollment, name='enrollment_edit'),

    # 展示班级
    url(r'^class_list/', teacher.ClassList.as_view(), name='class_list'),
    # 新增班级
    url(r'^class_add/', teacher.classes, name='class_add'),
    # 编辑班级
    url(r'^class_edit/(\d+)', teacher.classes, name='class_edit'),

    # 展示课程记录
    url(r'^course_record_list/(?P<class_id>\d+)', teacher.CourseRecordList.as_view(), name='course_record_list'),
    url(r'^course_record_add/(?P<class_id>\d+)', teacher.course_record, name='course_record_add'),
    url(r'^course_record_edit/(?P<course_request_id>\d+)', teacher.course_record, name='course_record_edit'),

    # 展示学习记录
    url(r'^study_record_list/(?P<course_record_id>\d+)/', teacher.study_record, name='study_record_list'),
]
