from django.contrib import admin
from app1 import models
# 在admin后台注册某个字段
admin.site.register(models.Customer)
admin.site.register(models.ClassList)
admin.site.register(models.Campuses)
admin.site.register(models.UserProfile)