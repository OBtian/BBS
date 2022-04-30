"""BBS01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from BBS01 import settings
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.home,name='home'),
    url(r'^register/',views.register,name='reg'),
    url(r'^login/',views.login,name='log'),
    url(r'^comment/',views.comment),
    url(r'^backend/',views.backend),
    url(r'^get_code/',views.get_code),
    url(r'^set_password/',views.set_password,name='set_psw'),
    url(r'^set_avatar/',views.set_avatar,name='set_avt'),
    url(r'^set_info/',views.set_info),
    url(r'^up_or_down/',views.up_or_down),
    url(r'^add_article/',views.add_article),
    url(r'^add_classify/',views.add_classify),
    url(r'^del_classify/',views.del_classify),
    url(r'^del_comment/',views.del_comment),

    # 暴露后端指定文件夹资源
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^tag/(?P<param>.*)/',views.home),
    url(r'^search/(?P<method>multiple|article|user)/(?P<keyword>\w+)',views.search),
    url(r'^(?P<site_name>\w+)/$',views.site,name='site'),
    url(r'^(?P<site_name>\w+)/(?P<method>classify|tag|date)/(?P<param>.*)',views.site),
    url(r'^(?P<site_name>\w+)/article/(?P<article_id>\d+)/',views.article_detail),
]