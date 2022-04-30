import json
import random
from django.shortcuts import render,HttpResponse,redirect
from app01.myforms import MyRegForm,MySetForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction
# Create your views here.

def register(request):
    form_obj = MyRegForm()
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            form_obj = MyRegForm(request.POST)
            if form_obj.is_valid():
                clean_data = form_obj.cleaned_data
                # 去除重复密码
                clean_data.pop('re_password')
                file_obj = request.FILES.get('avatar')
                if file_obj:
                    clean_data['avatar'] = file_obj
                # 因为有默认值所以不传就是默认
                # 保存
                usersite_info = {}
                usersite_info['site_name'] = clean_data['sitename']
                usersite_info['site_title'] = clean_data['sitetitle']
                clean_data.pop('sitename')
                clean_data.pop('sitetitle')
                usersite = models.Usersite.objects.create(**usersite_info)
                clean_data['usersite'] = usersite
                user = models.UserInfo.objects.create_user(**clean_data)

                back_dic['url']='/login/'
            else:
                back_dic['code']=2000
                back_dic['msg']=form_obj.errors
            return JsonResponse(back_dic)
    return render(request,'register.html',locals())

def login(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            code = request.POST.get('code')
            if request.session.get('code').upper() == code.upper():
                user = auth.authenticate(request,username=username,password=password)
                if user:
                    auth.login(request,user)
                    back_dic['url']='/'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '用户名或密码错误'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '验证码错误'
            return JsonResponse(back_dic)
    return render(request,'login.html',locals())
from app01.utils.pagination import Pagination
def home(request,**kwargs):
    tag_list = models.Tag.objects.all()
    article_list = models.Article.objects.all().order_by('create_time').reverse()
    if request.method == 'GET':
        if request.GET.get('method') == 'logout':
            auth.logout(request)
            return redirect(to='/')
        if kwargs:
            param = kwargs.get('param')
            tag = models.Tag.objects.filter(pk=param)
            article_list = models.Article.objects.filter(tags=tag).order_by('create_time').reverse()
    current_page = request.GET.get("page", 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'home.html',locals())
# pip install pillow
# Image生成图片
# ImageDraw画笔
# ImageFont控制字体
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO,StringIO
# 内存管理模块
# BytesIO:临时存储数据，返回时为二进制
# StringIO:临时存储数据，返回时为字符串
def get_random():
    return random.randint(0,144),random.randint(0,144),random.randint(0,144)
def get_code(request):
    img_obj = Image.new('RGB',(220,30),'white')#mode size color
    img_draw = ImageDraw.Draw(img_obj)#产生一个画笔对象
    code = ''
    for i in range(5):
        random_font = random.randint(1,5)
        random_upper = chr(random.randint(65,90))
        random_lower = chr(random.randint(97,122))
        random_int = str(random.randint(0,9))
        temp = random.choice([random_int,random_upper,random_lower])
        font_path = 'static/font/' + str(random_font) + '.ttf'
        img_font = ImageFont.truetype(font_path,25)#字体样式 大小
        img_draw.text((i*40,0),temp,get_random(),img_font)
        code += temp
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj,'png')
    return HttpResponse(io_obj.getvalue())

@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code':1000,'msg':''}
        if request.method == 'POST':
            old_psw = request.POST.get('old_password')
            new_psw = request.POST.get('new_password')
            confirm_psw = request.POST.get('confirm_password')
            if len(new_psw) < 8 or len(confirm_psw) < 8:
                back_dic['code'] = 1003
                back_dic['msg'] = '密码最短为8位'
            else:
                is_right = request.user.check_password(old_psw)
                if is_right:
                    if new_psw == confirm_psw:
                        request.user.set_password(new_psw)
                        request.user.save()
                        auth.logout(request)
                        back_dic['msg'] = '修改成功'
                    else:
                        back_dic['code'] = 1001
                        back_dic['msg'] = '两次密码不一致'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '原密码错误'
            return JsonResponse(back_dic)
    return redirect(to='/')
@login_required
def set_avatar(request):
    if request.is_ajax():
        back_dic = {'code':1000,'msg':''}
        if request.method == 'POST':
            file_obj = request.FILES.get('avatar')
            if file_obj:
                request.user.avatar = file_obj
                request.user.save()
                back_dic['msg'] = '修改成功'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = '请上传正确文件'
            return JsonResponse(back_dic)
        return redirect(to='/')
def site(request,site_name,**kwargs):
    usersite = models.Usersite.objects.filter(site_name=site_name).first()
    user_obj = models.UserInfo.objects.filter(usersite__site_name=site_name).first()
    if usersite:
        article_list = models.Article.objects.filter(usersite=usersite)
        if kwargs:
            method = kwargs.get('method')
            param = kwargs.get('param')
            if method == 'classify':
                article_list = article_list.filter(classify__id=param)
            elif method == 'tag':
                article_list = article_list.filter(tags__id=param,usersite__site_name=site_name)
            elif method == 'date':
                year,month = param.split('-')
                article_list = article_list.filter(create_time__year=year,create_time__month=month)
            else:
                return render(request,'error.html',locals())
        current_page = request.GET.get("page", 1)
        all_count = article_list.count()
        page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
        page_queryset = article_list[page_obj.start:page_obj.end]
        return render(request,'site.html',locals())
    else:
        return render(request,'error.html',locals())

def article_detail(request,site_name,article_id):
    # 校验username和article_id
    usersite = models.Usersite.objects.filter(site_name=site_name).first()
    article_obj = models.Article.objects.filter(pk=article_id,usersite=usersite).first()
    user_obj = models.UserInfo.objects.filter(usersite=usersite).first()
    comment_list = models.Comment.objects.filter(article=article_obj)

    if not article_obj or not user_obj:
        return render(request,'error.html')
    # 很多地方都要用就不能这么干，将侧边栏制作成inclusion_tag
    # usersite = user_obj.usersite
    # classify = models.Classify.objects.filter(usersite=usersite).annotate(count_num=Count('article__pk')).values_list('name', 'count_num', 'pk')
    # tag = models.Tag.objects.filter(usersite=usersite).annotate(count_num=Count('article__pk')).values_list('name','count_num','pk')
    # date_list = models.Article.objects.filter(usersite=usersite).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')

    return render(request,'article_detail.html',locals())

def up_or_down(request):
    """
    校验用户是否登录
    该文章是否是该用户自己写的
    当前用户是否已经点过了
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code':1000,'msg':''}
        if request.user.is_authenticated():
            article_id = request.POST.get('article_id')
            is_up = json.loads(request.POST.get('is_up'))
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not request.user == article_obj.usersite.userinfo:
                is_click = models.Up_Or_Down.objects.filter(user=request.user,article=article_obj).first()
                if not is_click:
                    # 判断点了赞还是点了踩
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num = F('up_num')+1)
                        back_dic['msg'] = '点赞成功'
                        models.Up_Or_Down.objects.create(user=request.user,article=article_obj,is_up=True,is_down=False)
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                        models.Up_Or_Down.objects.create(user=request.user, article=article_obj, is_up=False,is_down=True)
                else:
                    back_dic['code'] = 1001
                    # back_dic['msg'] = '已经点过了哦'
                    if is_click.is_up:
                        back_dic['msg'] = '已经推荐过了哦'
                    else:
                        back_dic['msg'] = '已经反对过了哦'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '不能点自己的文章哦'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/login/">登录</a>'
        return JsonResponse(back_dic)
    return render(request,'error.html',locals())

def comment(request):
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code':1000,'msg':''}
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                if content == '':
                    back_dic['code'] = 1001
                    back_dic['msg'] = '评论内容不能为空'
                else:
                    # with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num = F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user,article_id=article_id,content=content,parent_id=parent_id)
                    back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '用户未登录'
            return JsonResponse(back_dic)
    return render(request,'article_detail.html')
@login_required
def backend(request):
    article_list = models.Article.objects.filter(usersite__userinfo__username=request.user)
    comment_list = models.Comment.objects.filter(article__usersite__userinfo__username=request.user)
    my_comment = models.Comment.objects.filter(user=request.user)
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    tags_list = models.Usersite2Tag.objects.filter(usersite__userinfo__username=request.user)
    tag_list = models.Tag.objects.all()

    if request.method == 'GET':
        if request.GET.get('method') == 'edit_art':
            article_obj = models.Article.objects.filter(pk=request.GET.get('pk')).first()
            return render(request,'edit_article.html',locals())
        elif request.GET.get('method') == 'del_art':
            models.Article.objects.filter(pk=request.GET.get('pk')).delete()
            return redirect(to='/backend/')
        elif request.GET.get('method') == 'del_com':
            if models.Comment.objects.filter(pk=request.GET.get('pk')):
                models.Comment.objects.filter(pk=request.GET.get('pk')).delete()
                models.Article.objects.filter(pk=request.GET.get('art')).update(comment_num=F('comment_num') - 1)
            return render(request,'del_comment.html',locals())
        elif request.GET.get('method') == 'edit_cla':
            classify_obj = models.Classify.objects.filter(pk=request.GET.get('pk')).first()
            return render(request,'edit_classify.html',locals())
        elif request.GET.get('method') == 'del_cla':
            classify_obj = models.Classify.objects.filter(pk=request.GET.get('pk'))
            models.Article.objects.filter(classify=classify_obj).update(classify=None)
            classify_obj.delete()
            return render(request,'del_classify.html',locals())
        elif request.GET.get('method') == 'edit_my_com':
            comment_obj = models.Comment.objects.filter(pk=request.GET.get('pk')).first()
            return render(request, 'edit_my_com.html', locals())
        elif request.GET.get('method') == 'del_my_com':
            if models.Comment.objects.filter(pk=request.GET.get('pk')):
                models.Comment.objects.filter(pk=request.GET.get('pk')).delete()
                models.Article.objects.filter(pk=request.GET.get('art')).update(comment_num=F('comment_num') - 1)
            return render(request, 'del_my_com.html', locals())
    if request.is_ajax():
        back_dic = {'code': 1000}
        if request.method == 'POST':
            url = request.get_full_path()
            shr_url = url.split('?')
            method_all = shr_url[1].split('&')
            method_half = method_all[0].split('=')
            pk_half = method_all[1].split('=')
            method = method_half[1]
            pk = int(pk_half[1])
            if method == 'edit_art':
                data = request.POST.dict()
                usersite = models.Usersite.objects.filter(userinfo__username=request.user).first()

                if 'classify' in data.keys():
                    classify = models.Classify.objects.filter(pk=data['classify']).first()
                    tag_id_list = []
                    i=0
                    for tag in tag_list:
                        i+=1
                        index = 'tags' + str(i)
                        if index in data.keys():
                            tag_id_list.append(data[index])
                            data.pop(index)
                    pk = data['id']
                    data.pop('id')
                    data['usersite'] = usersite
                    data['classify'] = classify
                    data.pop('csrfmiddlewaretoken')
                    # 先把data中的多对多数据取出，然后创建model，最后建立多对多关系。
                    # print(data)
                    article_obj = models.Article.objects.filter(pk=pk)
                    models.Article2Tag.objects.filter(article_id=pk).delete()
                    article_obj.update(**data)
                    # 半自动，自己建立多对多关系
                    article_obj_list = []
                    for x in tag_id_list:
                        article_obj_list.append(models.Article2Tag(article_id=pk,tag_id=x))

                    # 批量插入数据
                    models.Article2Tag.objects.bulk_create(article_obj_list)
                    back_dic['url']= '/backend/'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '请选择分类'
                return JsonResponse(back_dic)
            elif method == 'edit_cla':
                classify_obj = models.Classify.objects.filter(pk=pk).update(name=request.POST.get('name'))
                back_dic['url'] = '/del_classify/'
                return JsonResponse(back_dic)
            elif method == 'edit_my_com':
                models.Comment.objects.filter(pk=pk).update(content=request.POST.get('com_content'))
                back_dic['url'] = '/del_comment/'
                return JsonResponse(back_dic)
    return render(request,'backend.html',locals())
from bs4 import BeautifulSoup
@login_required
def add_article(request):
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    tag_list = models.Tag.objects.all()
    if request.is_ajax():
        back_dic = {'code': 1000}
        if request.method == 'POST':
            if not request.POST.get('title'):
                back_dic['code'] = 2000
                back_dic['msg'] = '标题不能为空'
            elif not request.POST.get('classify'):
                back_dic['code'] = 2000
                back_dic['msg'] = '请选择分类'
            elif len(request.POST.get('desc')) > 256:
                back_dic['code'] = 3000
                back_dic['msg'] = '简介应小于256个字符'
            elif len(request.POST.get('title')) > 32:
                back_dic['code'] = 4000
                back_dic['msg'] = '标题应小于32个字符'
            else:
                content = request.POST.get('content')
                soup = BeautifulSoup(content,'html.parser')
                tags = soup.find_all()
                for tag_obj in tags:
                    if tag_obj.name == 'script':
                        tag_obj.decompose()
                data = request.POST.dict()
                usersite = models.Usersite.objects.filter(userinfo__username=request.user).first()
                classify = models.Classify.objects.filter(pk=data['classify']).first()
                data['content'] = str(soup)
                tag_id_list = []
                i=0
                for tag in tag_list:
                    i+=1
                    index = 'tags' + str(i)
                    if index in data.keys():
                        print(1)
                        tag_id_list.append(data[index])
                        data.pop(index)
                data['usersite'] = usersite
                data['classify'] = classify
                data.pop('csrfmiddlewaretoken')
                # 先把data中的多对多数据取出，然后创建model，最后建立多对多关系。
                # print(data)
                article_obj = models.Article.objects.create(**data)
                # 半自动，自己建立多对多关系
                article_obj_list = []
                usersite_obj_list = []
                for i in tag_id_list:
                    article_obj_list.append(models.Article2Tag(article=article_obj,tag_id=i))
                    usersite_obj_list.append(models.Usersite2Tag(usersite=usersite,tag_id=i))
                # 批量插入数据
                models.Article2Tag.objects.bulk_create(article_obj_list)
                models.Usersite2Tag.objects.bulk_create(usersite_obj_list)
                back_dic['url']= '/backend/'
            return JsonResponse(back_dic)
    return render(request,'add_article.html',locals())
@login_required
def add_classify(request):
    if request.is_ajax():
        back_dic = {'code':1000}
        if request.method == 'POST':
            name = request.POST.get('name')
            if len(name) == 0:
                back_dic['code'] = 2000
                back_dic['msg'] = '分类名称不能为空'
            elif len(name) > 32:
                back_dic['code'] = 3000
                back_dic['msg'] = '分类名称最长为32位'
            else:
                usersite = models.Usersite.objects.filter(userinfo__username=request.user).first()
                models.Classify.objects.create(name=name,usersite=usersite)
                back_dic['url'] = '/del_classify/'
            return JsonResponse(back_dic)
    return render(request,'add_classify.html',locals())
@login_required
def del_classify(request):
    article_list = models.Article.objects.filter(usersite__userinfo__username=request.user)
    comment_list = models.Comment.objects.filter(article__usersite__userinfo__username=request.user)
    my_comment = models.Comment.objects.filter(user=request.user)
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    tags_list = models.Tag.objects.filter(usersite__userinfo__username=request.user)
    tag_list = models.Tag.objects.all()
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    return render(request,'del_classify.html',locals())
@login_required
def del_comment(request):
    article_list = models.Article.objects.filter(usersite__userinfo__username=request.user)
    comment_list = models.Comment.objects.filter(article__usersite__userinfo__username=request.user)
    my_comment = models.Comment.objects.filter(user=request.user)
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    tag_list = models.Tag.objects.filter(usersite__userinfo__username=request.user)
    my_comment = models.Comment.objects.filter(user=request.user)
    return render(request,'del_my_com.html',locals())
@login_required
def set_info(request):
    article_list = models.Article.objects.filter(usersite__userinfo__username=request.user)
    comment_list = models.Comment.objects.filter(article__usersite__userinfo__username=request.user)
    my_comment = models.Comment.objects.filter(user=request.user)
    classify_list = models.Classify.objects.filter(usersite__userinfo__username=request.user)
    tags_list = models.Tag.objects.filter(usersite__userinfo__username=request.user)
    tag_list = models.Tag.objects.all()
    my_comment = models.Comment.objects.filter(user=request.user)
    form_obj = MySetForm()
    if request.is_ajax():
        back_dic = {'code': 1000}
        if request.method == 'POST':
            form_obj = MySetForm(request.POST)
            if form_obj.is_valid():
                clean_data = form_obj.cleaned_data
                usersite_info = {}
                usersite_info['site_name'] = clean_data['sitename']
                usersite_info['site_title'] = clean_data['sitetitle']
                clean_data.pop('sitename')
                clean_data.pop('sitetitle')

                usersite = models.Usersite.objects.filter(userinfo__username=request.user)
                usersite1 = models.Usersite.objects.filter(site_name=usersite_info['site_name'])
                if clean_data['username'] == request.user.username:
                    if str(usersite) == str(usersite1):
                        usersite = models.Usersite.objects.filter(userinfo__username=request.user).update(site_title=usersite_info['site_title'])
                        models.UserInfo.objects.filter(username = request.user).update(**clean_data)
                        back_dic['msg'] = usersite_info['site_name']
                    else:
                        if usersite1:
                            form_obj.add_error('sitename', '站点名称已存在')
                            back_dic['code'] = 2000
                            back_dic['msg'] = form_obj.errors
                        else:
                            usersite = models.Usersite.objects.filter(userinfo__username=request.user).update(
                                **usersite_info)
                            models.UserInfo.objects.filter(username=request.user).update(**clean_data)
                            back_dic['msg'] = usersite_info['site_name']
                else:
                    flag = 0
                    if not usersite_info['site_name'] == usersite.values('site_name'):
                        if usersite1:
                            form_obj.add_error('sitename','站点名称已存在')
                            flag = 1
                    user_obj = models.UserInfo.objects.filter(username=clean_data['username'])
                    if user_obj:
                        form_obj.add_error('username','用户已存在')
                        flag = 1
                    if flag:
                        back_dic['code'] = 2000
                        back_dic['msg'] = form_obj.errors
                    else:
                        models.Usersite.objects.filter(userinfo__username=request.user).update(**usersite_info)
                        models.UserInfo.objects.filter(username=request.user).update(**clean_data)
                        back_dic['msg'] = usersite_info['site_name']
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request,'set_info.html',locals())
from django.db.models import Q
def search(request,method,keyword):
    tag_list = models.Tag.objects.all()
    articles_list = models.Article.objects.all()
    users_obj = models.UserInfo.objects.exclude(pk=1).first()
    users_list = models.UserInfo.objects.exclude(pk=1)
    current_page = request.GET.get("page", 1)
    all_count = articles_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_queryset_articles = articles_list[page_obj.start:page_obj.end]
    all_count = users_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_queryset_users = users_list[page_obj.start:page_obj.end]
    if not keyword == 'inputnull':
        user_obj = models.UserInfo.objects.exclude(pk=1).filter(Q(username__contains=keyword)).first()
        article_list = models.Article.objects.filter(Q(title__contains=keyword))
        user_list = models.UserInfo.objects.exclude(pk=1).filter(Q(username__contains=keyword))
        if user_obj:
            article_list = article_list.union(models.Article.objects.filter(Q(usersite__userinfo__username__contains=keyword)))
        if not (user_obj or article_list):
            return render(request,'search_empty.html',locals())
    else:
        article_list = models.Article.objects.all()
        user_obj = models.UserInfo.objects.exclude(pk=1).first()
        user_list = models.UserInfo.objects.exclude(pk=1)

    current_page = request.GET.get("page", 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_queryset_article = article_list[page_obj.start:page_obj.end]
    all_count = user_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_queryset_user = user_list[page_obj.start:page_obj.end]
    if method == 'article':
        return render(request,'search_art.html',locals())
    elif method == 'user':
        return render(request, 'search_user.html', locals())
    return render(request,'search.html',locals())