from django import forms
from app1 import models
from django.core.exceptions import ValidationError
import hashlib

# 因为每个都要添加此类名,所以对 BootstrapFrom进行封装
"""
widget: 插件
attrs: 添加
self.fields.values():一个字典的values
"""


class BootstrapForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 添加属性
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# 注册form
class ReForm(BootstrapForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='密码', min_length=6)
    re_password = forms.CharField(widget=forms.PasswordInput(), label='确认密码', min_length=6)

    class Meta:  # 通过models 自动创建表单
        model = models.UserProfile
        fields = "__all__"  # 所有字段
        # fields = ['username','password']
        exclude = ['is_active']  # 排除某些字段

        labels = {
            'username': '用户名',
            'password': '密码',
            # 're_password': '确认密码',
            'department': '部门',
        }

        widgets = {
            # 'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

        error_messages = {
            'username': {
                'required': '不能为空',
                'invalid': '格式错误'
            }

        }

    # # 给某些表单添加样式 类名
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.widget.attrs.update({'class': 'form-control'})

    # 全局钩子验证
    """
    clean_data:
    cleaned_data中的值类型与字段定义的Field类型一致。
    如果字段定义charfield，那么clean方法返回的cleaned_data中对应的字段值就是字符型，
    定义为ModelChoiceField，则cleaned_data中字段值是某个model实例。
    定义为ModelMultipleChoiceField，则cleaned_data中字段值是个model实例list。
    """

    def clean(self):
        pwd = self.cleaned_data.get('password', '')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            # 对密码进行加密
            md5 = hashlib.md5()
            md5.update(pwd.encode("utf-8"))
            pwd = md5.hexdigest()
            self.cleaned_data['password'] = pwd
            return self.cleaned_data  # 返回所有通过验证的
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')


# 客户form
class CustomerForm(BootstrapForm):
    class Meta:
        model = models.Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].widget.attrs = {}


class ConsultForm(BootstrapForm):
    class Meta:
        model = models.ConsultRecord
        fields = '__all__'

        # widget:,attrs:,????????????

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delete_status'].widget.attrs.pop('class')
        # self.instance.consultant 当前登录的用户(销售)
        customer_choices = [(i.pk, str(i)) for i in self.instance.consultant.customers.all()]
        print([(i.pk, str(i)) for i in self.instance.consultant.customers.all()])
        customer_choices.insert(0, ('', '---------'))

        self.fields['customer'].choices = customer_choices
        self.fields['consultant'].choices = [(self.instance.consultant.pk, self.instance.consultant.name)]


class EnrolForm(BootstrapForm):
    class Meta:
        model = models.Enrollment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.customer_id != '0':
            # 限制客户是当前客户
            self.fields['customer'].choices = [(self.instance.customer_id, str(self.instance.customer))]
            # 限制客户可选的班级是记录中已报的班级
            self.fields['enrolment_class'].choices = [(i.pk, str(i)) for i in self.instance.customer.class_list.all()]


class ClassForm(BootstrapForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'


# 课程记录Form
class CourseRecordForm(BootstrapForm):
    class Meta:
        model = models.CourseRecord
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制班级是当前班级
        self.fields['re_class'].choices = [(self.instance.re_class_id, str(self.instance.re_class))]
        # 限制老师是当前老师
        self.fields['teacher'].choices = [(self.instance.teacher_id, str(self.instance.teacher))]


class StudyRecordForm(BootstrapForm):
    class Meta:
        model = models.StudyRecord
        fields = "__all__"
