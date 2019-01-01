from django.shortcuts import render, redirect, HttpResponse, reverse
from app1 import models
import hashlib
from app1.forms import CustomerForm, ConsultForm, EnrolForm
from django.views import View
from django.db.models import Q
from app1.utils.paginationg import Pagination
from django.http.request import QueryDict
from django.conf import global_settings
from django.contrib.sessions.backends import db
from app1.utils.url import reverse_url
from django.conf import settings
from django.db import transaction


def index(request):
    return HttpResponse('hahahhahh')


# 展示
# '''
# request: 请求对象
# consultant__isnull=True: 该字段(销售)为空
# request.account: 当前请求的用户
# '''
def customer_list(request):
    if request.path_info == reverse('customer_list'):
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        all_customer = models.Customer.objects.filter(consultant=request.account)
        print(request.account)
    # all_customer = models.Customer.objects.all()
    return render(request, 'consultant/customer_list.html', {'all_customer': all_customer})


# VIew ??????
class CustomerList(View):

    def get(self, request):

        q = self.search(['qq', 'name', ])
        if request.path_info == reverse('customer_list'):  # 公户
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True, )
        else:
            all_customer = models.Customer.objects.filter(q, consultant=request.account)  # 私户

        pager = Pagination(request.GET.get('page', '1'), all_customer.count(), request.GET.copy(), 2)   #request.GET.copy() ,QueryDict(mutable=True)
        return render(request, 'consultant/customer_list.html', {
            'all_customer': all_customer[pager.start: pager.end],
            'page_html': pager.page_html
        })

    def post(self, request):
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        getattr(self, action)()

        return self.get(request)

    def multi_apply(self):

        # 公户变私户
        ids = self.request.POST.getlist('id')
        # 方式一   self.request.account : 表示当前用户
        models.Customer.objects.filter(id__in=ids).update(consultant=self.request.account)

        # 方式二
        # self.request.account.customers.add(*models.Customer.objects.filter(id__in=ids))

        # 如果当前有的私户+申请的数量 > 最大值  不允许
        if self.request.account.customers.all().count() + len(ids) > settings.MAX_CUSTOMER_NUM:
            return HttpResponse('太贪心了')
        # 事务
        with transaction.atomic():
            # 查询出数据枷锁
            queryset = models.Customer.objects.filter(id__in=ids, consultant__isnull=True).select_for_update()
            if len(ids) == queryset.count():
                queryset.update(consultant=self.request.account)
                return
            return HttpResponse('你的手速太慢了')

    def multi_public(self):
        ids = self.request.POST.getlist('id')
        print(ids)
        # 方式一
        models.Customer.objects.filter(id__in=ids).update(consultant=None)
        # 方式二
        # self.request.account.customers.remove(*models.Customer.objects.filter(id__in=ids))

    def search(self, query_list):
        query = self.request.GET.get('query', '')  # query为前段input的name,如果没有得到 query, 接收'', 否则为none
        q = Q()  # Q(Q(qq__contains=query) | Q(name__contains=query))    #contains像
        q.connector = 'OR'  # 相当于 |
        #  Q(('qq__contains', query))    Q(qq__contains=query)
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))
        return q


userlist = [{'name': '傻傻的兆满{}号'.format(i), 'pwd': '帅帅的灰灰{}号'.format(i)} for i in range(1, 667)]


def user_list(request):
    try:
        page = int(request.GET.get('page', '1'))  # 获取当前页码数
        if page <= 0:
            page = 1
    except Exception as e:
        page = 1
    print(page)

    per_num = 15  # 每页显示的数据
    all_count = len(userlist)  # 总的数据量
    page_num, more = divmod(all_count, per_num)  # 商和余数
    if more:
        page_num += 1
    max_show = 11  # 最多显示的分页数
    half_show = max_show // 2  # 当前页码左面和右面各多少个,

    if page_num < max_show:
        page_start = 1
        page_end = page_num
    else:
        if page <= half_show:
            page_start = 1
            page_end = max_show
        elif page + half_show > page_num:
            page_start = page_num - max_show + 1
            page_end = page_num
        else:
            page_start = page - half_show
            page_end = page + half_show

        start = (page - 1) * per_num
        end = page * per_num

    li_list = []  # 将分配好的页码,放入列表
    if page == 1:
        li_list.append('<li class="disabled" ><a> << </a></li>')
    else:
        li_list.append('<li ><a href="?page={}"> << </a></li>'.format(page - 1))

    for i in range(page_start, page_end + 1):
        if page == i:
            li_list.append('<li class="active"><a href="?page={}">{}</a></li>'.format(i, i))
        else:
            li_list.append('<li><a href="?page={}">{}</a></li>'.format(i, i))

    if page == page_num:
        li_list.append('<li class="disabled" ><a> >> </a></li>')
    else:
        li_list.append('<li ><a href="?page={}"> >> </a></li>'.format(page + 1))

    page_html = ''.join(li_list)  # 列表变成字符串
    return render(request, 'user_list.html', {'all_user': userlist[start:end],
                                              'page_num': range(page_start, page_end + 1),
                                              'page_html': page_html}, )


# 调用封装好的分页
from app1.utils.paginationg import Pagination


def user_list(request):
    pager = Pagination(request.GET.get('page', '1'), len(user_list), per_num=10, max_show=15)
    return render(request, 'user_list.html',
                  {"all_user": userlist[pager.start:pager.end],
                   'page_html': pager.page_html
                   }, )


def customer_add(request):  # 添加用户
    # 创建一个空的form对象
    form_obj = CustomerForm()
    if request.method == 'POST':
        # 创建一个包含提交数据的form对象
        form_obj = CustomerForm(request.POST)
        # 对提交的数据进行校验
        if form_obj.is_valid():
            # 保存数据
            form_obj.save()
            # 跳转到展示页面, 反向解析
            return redirect(reverse('customer_list'))
    return render(request, 'consultant/customer_add.html', {'form_obj': form_obj})


def customer_edit(request, edit_id):
    # 查询出要编辑的对象
    obj = models.Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()  # 对要修改的对象进行修改
            # 跳转至展示页面
            return redirect(reverse("customer_list"))
    return render(request, 'consultant/customer_edit.html', {'form_obj': form_obj})


# 新增和编辑
def customer_change(request, edit_id=None):
    obj = models.Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():  # 没有instance新增, 有instance坐修改
            form_obj.save()
            # return redirect(reverse('customer_list'))
            return redirect(reverse_url(request, 'customer_list'))
    return render(request, 'consultant/customer_change.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 跟进记录表展示
class ConsultList(View):
    def get(self, request, customer_id):
        # 获取跟进记录
        if customer_id == '0':
            all_consult = models.ConsultRecord.objects.filter(consultant=request.account)

        else:
            all_consult = models.ConsultRecord.objects.filter(consultant=request.account, customer_id=customer_id)
        return render(request, 'consultant/consult_list.html', {'all_consult': all_consult})


# 增加跟进记录表
def consult_add(request):
    # 实例化一个包含当前销售的跟进记录 consultant,account, instance
    obj = models.ConsultRecord(consultant=request.account)
    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list', args=('0',)))
    return render(request, 'consultant/consult_add.html', {'form_obj': form_obj})


# 编辑跟进记录表
def consult_edit(request, edit_id):
    # 查找要编辑的对象
    obj = models.ConsultRecord.objects.filter(pk=edit_id).first()
    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list', args=('0',)))
    return render(request, 'consultant/consult_edit.html', {'form_obj': form_obj})


# 展示报名记录表
class EnrollmentList(View):
    def get(self, request, customer_id):
        if customer_id == '0':
            all_enrollment = models.Enrollment.objects.all()
        else:
            all_enrollment = models.Enrollment.objects.filter(customer_id=customer_id)
        return render(request, 'consultant/enrollment_list.html', {'all_enrollment': all_enrollment})


def enrollment(request, record_id=None, customer_id=None):
    if customer_id:
        obj = models.Enrollment(customer_id=customer_id)
        title = '添加记录表'
    else:
        obj = models.Enrollment.objects.filter(pk=record_id).first()
        title = '编辑记录表'
    print(customer_id)
    print(obj)
    form_obj = EnrolForm(instance=obj)  # 实例化
    if request.method == 'POST':
        form_obj = EnrolForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('enrollment_list', args=('0',)))
    return render(request, 'consultant/enrollment.html', {'form_obj': form_obj, 'title': title})
