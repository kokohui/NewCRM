from django.db import models

""""
verbose_name_plural:
verbose_name: 
blank: 
"""


class Menu(models.Model):
    """
    一级菜单
    """
    title = models.CharField(max_length=32)
    icon = models.CharField(max_length=64, null=True)
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    权限表
    BooleanField: 返回True or False
    """
    url = models.CharField(max_length=108, verbose_name='权限')
    title = models.CharField(max_length=64, verbose_name='标题')
    menu = models.ForeignKey('Menu', null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)  # 自关联
    name = models.CharField(max_length=108, verbose_name='URL_别名')

    # is_menu = modlels.BooleanField(default=False, verbose_name='是否是菜单')
    # icon = models.CharField(max_length=64, null=True, blank=True, verbose_name='图标')

    class Meta:
        verbose_name_plural = '权限'
        verbose_name = '权限'

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色表
    """
    name = models.CharField(max_length=32, verbose_name='名字')
    permissions = models.ManyToManyField('Permission', verbose_name='角色拥有的权限', blank=True)

    def __str__(self):
        return self.name


class User(models.Model):
    """
    用户表
    """
    # name = models.CharField(max_length=32, verbose_name='名称')
    # password = models.CharField(max_length=32, verbose_name='密码')
    roles = models.ManyToManyField(Role, verbose_name='y用户拥有的角色', blank=True)

    # def __str__(self):
    #     return self.name
    class Meta:
        abstract = True  # 数据库迁移的时候不会生成表, 基类用作继承
