from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth



register = template.Library()

@register.inclusion_tag('left_menu.html')
def left_menu(username):
    # 构造所需数据
    user_obj = models.UserInfo.objects.filter(username=username).first()
    usersite = models.Usersite.objects.filter(userinfo__username=username).first()
    classify = models.Classify.objects.filter(usersite=usersite).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    # tag = models.Tag.objects.filter(usersite2tag__usersite=usersite).annotate(count_num=Count('article__pk')).values_list('name','count_num','pk')
    date_list = models.Article.objects.filter(usersite=usersite).order_by('create_time').reverse().annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    tags = models.Tag.objects.filter(usersite2tag__usersite=usersite)
    tags_count = {}
    tag_name = []
    x = 0
    for i in tags:
        if models.Article.objects.filter(usersite=usersite,tags=i):
            if not i.name in tag_name:
                tags_count[x] = {0:i.name,1:models.Article.objects.filter(usersite=usersite,tags=i).count(),2:i.pk}
                tag_name.append(i.name)
                x += 1
    return locals()

