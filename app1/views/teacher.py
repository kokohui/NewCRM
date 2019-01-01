from django.shortcuts import render, redirect, HttpResponse, reverse
from app1 import models
from django.views import View
from django.db.models import Q
from app1.utils.paginationg import Pagination
from app1.forms import ClassForm, CourseRecordForm, StudyRecordForm
from app1.utils.url import rev_url


# 班级展示
class ClassList(View):

    def get(self, request):
        q = self.search([])
        all_class = models.ClassList.objects.filter(q)

        pager = Pagination(request.GET.get('page', '1'), all_class.count(), request.GET.copy(), 10)
        return render(request, 'teacher/class_list.html', {
            'all_class': all_class[pager.start:pager.end],
            'page_html': pager.page_html})

    def post(self, request):
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('非法操作')
        res = getattr(self, action)()  # 如果操作中有返回值, 直接返回res
        if res:
            return res
        return self.get(request)

    def search(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()  # Q(Q(qq__contains=query)|Q(name__contains=query))
        # Q(Q(qq__contains=query)|Q(name__contains=query)) 等同于 Q(Q((qq__contains, query)),)
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))
        return q


# 新增和编辑班级
def classes(request, edit_id=None):
    obj = models.ClassList.objects.filter(pk=edit_id).first()
    form_obj = ClassForm(instance=obj)
    title = '编辑班级' if edit_id else '新增班级'
    if request.method == 'POST':
        form_obj = ClassForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(rev_url(request, 'class_list'))
    return render(request, 'teacher/classes.html', {'form_obj': form_obj, 'title': title})


# 班级记录展示
class CourseRecordList(View):

    def get(self, request, class_id):
        q = self.search([])
        all_course_record = models.CourseRecord.objects.filter(q, re_class_id=class_id)
        pager = Pagination(request.GET.get('page', '1'), all_course_record.count(), request.GET.copy())
        return render(request, 'teacher/course_record_list.html', {
            'all_course_record': all_course_record[pager.start: pager.end],
            'page_html': pager.page_html,
            'class_id': class_id,
        })

    def post(self, request, class_id):
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')
        res = getattr(self, action)()
        # 如果操作中有返回值, 直接返回res
        if res:
            return res
        return self.get(request, class_id)

    def search(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i)), query))
        return q

    def multi_init(self):
        # 获取提交的客户ids
        course_record_ids = self.request.POST.getlist('id')
        # 从数据库中找到 选择的对应的id  班级跟进记录
        course_record_obj_list = models.ConsultRecord.objects.filter(id__in=course_record_ids)

        for course_record_obj in course_record_obj_list:
            # 根据课程记录创建学习记录
            all_students = course_record_obj.re_class.customer_set.all().filter(status='studying')
            list1 = []
            for student in all_students:
                list1.append(models.StudyRecord(course_record=course_record_obj, student=student))
            models.StudyRecord.objects.bulk_create(list1)


def course_record(request, class_id=None, course_record_id=None):
    obj = models.CourseRecord.objects.filter(
        pk=course_record_id).first() if course_record_id else models.CourseRecord(
        re_class_id=class_id, teacher=request.account)
    form_obj = CourseRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(rev_url(request, 'course_record_list', obj.re_class_id if course_record_id else class_id))
    return render(request, 'teacher/classes.html', {'form_obj': form_obj})


from django.forms import modelformset_factory


def study_record(request, course_record_id):
    FormSet = modelformset_factory(models.StudyRecord, StudyRecordForm, extra=0)

    all_study_record = models.StudyRecord.objects.filter(course_record_id=course_record_id)

    form_obj = FormSet(queryset=all_study_record)

    if request.method == 'POST':
        form_obj = FormSet(request.POST, queryset=all_study_record)
        if form_obj.is_valid():
            form_obj.save()
        print(form_obj.errors)
    return render(request, 'teacher/study_record_list.html', {
        'form_obj': form_obj
    })
