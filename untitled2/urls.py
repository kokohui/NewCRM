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
from django.contrib import admin
from django.conf.urls import url, include
from app1.views import account
from app1.views import consultant

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^login/', account.login, name='login'),
    url(r'^index', consultant.index, name='index'),
    url(r'^reg/', account.reg, name='reg'),
    url(r'^logout/', account.logout, name='logout'),
    url(r'app1/', include('app1.urls')),
    url(r'^rbec/', include('rbec.urls', namespace='rbec')),

]
"""
    include: 让路径变为 app1/(urls)
    """
