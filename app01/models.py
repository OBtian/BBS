from django.db import models

# Create your models here.

# 用户表
# UserInfo
# 继承AbstractUser
# phone verbose_name=电话号码 CharField max_length
# creat_time verbose_name=创建时间 DateTimeField auto_now_add
# avatar verbose_name=头像 FileField upload_to
# 外键字段
# 一对一个人站点表
from django.contrib.auth.models import AbstractUser
class UserInfo(AbstractUser):
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.png')
    create_time = models.DateTimeField(auto_now_add=True)

    usersite = models.OneToOneField(to='Usersite',null=True)
    # class Meta:
    #     verbose_name_plural = '用户表' # 修改admin后台管理默认的表名
    #     verbose_name = 'str' # 末尾自动加s
# 个人站点
# Usersite
# site_name verbose_name=站点名称 CharField max_length
# site_title verbose_name=站点标题 CharField max_length
# site_style verbose_name=站点样式 TextField upload_to
class Usersite(models.Model):
    site_name = models.CharField(verbose_name='站点名称',max_length=32)
    site_title = models.CharField(verbose_name='站点标题',max_length=32)

    tags = models.ManyToManyField(to='Tag', through='Usersite2Tag', through_fields=('usersite', 'tag'))
    def __str__(self):
        return self.site_name

class Tag(models.Model):
    name = models.CharField(verbose_name='标签名', max_length=32)
    def __str__(self):
        return self.name
# 文章标签表
# Tap
# name verbose_name=标签名 CharField max_length
# 外键字段
# 多对多个人站点表
class Usersite2Tag(models.Model):
    usersite = models.ForeignKey(to='Usersite')
    tag = models.ForeignKey(to='Tag')

# 文章分类表
# Classify
# name verbose_name=分类名 CharField max_length
# 外键字段
# 一对多个人站点表
class Classify(models.Model):
    name = models.CharField(verbose_name='分类名',max_length=32)
    usersite = models.ForeignKey(to='Usersite',null=True)
    def __str__(self):
        return self.name
# 文章表
# Article
# title verbose_name=文章标题 CharField max_length
# desc verbose_name=文章简介 CharField max_length
# content verbose_name=文章内容 TextField upload_to
# create_time verbose_name=上传时间 DateTimeField auto_now_add
# 数据库优化,减少跨表次数，提高效率
# up_num verbose_name=点赞数 IntegerField
# down_num verbose_name=点踩数 IntegerField
# comment_num verbose_name=评论数 IntegerField
# 外键字段
# 一对多个人站点表
# 多对多文章标签表
# 一对多文章分类表
class Article(models.Model):
    title = models.CharField(verbose_name='文章标题',max_length=32)
    desc = models.CharField(verbose_name='文章简介',max_length=256)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True)
    up_num = models.BigIntegerField(verbose_name='点赞数',default=0)
    down_num = models.BigIntegerField(verbose_name='点踩数',default=0)
    comment_num = models.BigIntegerField(verbose_name='评论数',default=0)


    usersite = models.ForeignKey(to='Usersite',null=True)
    classify = models.ForeignKey(to='Classify',null=True)
    tags = models.ManyToManyField(to='Tag',through='Article2Tag',through_fields=('article','tag'))

    def __str__(self):
        return self.title
class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')
# 点赞点踩表
# Up_Or_Down
# user verbose_name=用户名
# article verbose_name=文章名
# is_up verbose_name=是否点赞 BooleanField
# is_down verbose_name=是否点踩 BooleanField
# 外键字段
# 一对多文章表
class Up_Or_Down(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()
    is_down = models.BooleanField()
# 文章评论表
# Comment
# user verbose_name=用户名 CharField max_length
# article verbose_name=文章名 CharField max_length
# content verbose_name=评论内容 CharField max_length
# comment_time verbose_name=评论时间 DateTimeField auto_now_add
# 外键字段
# 一对多文章表
class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(verbose_name='评论内容',max_length=255)
    create_time = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    parent = models.ForeignKey(to='self',null=True)
    def __str__(self):
        return self.content