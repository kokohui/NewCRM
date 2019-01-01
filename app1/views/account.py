from django.shortcuts import render, redirect, reverse
from app1 import models
from app1.forms import ReForm
import hashlib
from rbec.service.permission import init_permisson


# 登录
def login(request):
    err_msg = ''
    if request.method == 'POST':
        # 获取提交的数据
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        print(user)
        print(pwd)
        # 对密码进行加密
        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        pwd = md5.hexdigest()
        # 按照输入账户密码从数据库中查找
        obj = models.UserProfile.objects.filter(username=user, password=pwd, is_active=True).first()

        if obj:
            # 认证成功 保存用户的id在session中
            request.session['user_id'] = obj.pk
            init_permisson(request, obj)
            print('obj', obj)
            # 跳转到首页
            return redirect('/app1/customer_list/')
        err_msg = '用户名或密码错误'
    return render(request, 'login.html', {'err_msg': err_msg})


# 清除session, .flush()删除cookie和session, .delete()不删除cookie
def logout(request):
    request.session.flush()
    return redirect(reverse('login'))


# 注册
def reg(request):
    form_obj = ReForm()  # form表单校验之后的结果
    if request.method == 'POST':
        form_obj = ReForm(request.POST)  # 把 POST 请求放入到form 验证
        if form_obj.is_valid():  # 如果通过验证
            form_obj.save()  # 保存数据
            return redirect('/login/')  # 重定向,返回登录界面
    return render(request, 'reg.html', {'form_obj': form_obj})
