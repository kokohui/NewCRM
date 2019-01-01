from django.contrib import admin
from rbec import models


# Register your models here.
class PermissionModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'name']  # 展示的字段
    list_editable = ['url', 'name']  # 编辑的字段


admin.site.register(models.Permission, PermissionModelAdmin)
admin.site.register(models.Role)
# admin.site.register(models.User)
admin.site.register(models.Menu)
