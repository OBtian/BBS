# 针对用户表的forms组件代码
from django import forms
from app01 import models

class MyRegForm(forms.Form):
    username = forms.CharField(label='用户名',min_length=1,max_length=8,
                               error_messages={
                                   'required':'用户名不能为空',
                                   'max_length':'用户名不能超过8位'
                               },
                               widget=forms.widgets.TextInput(attrs={'class':'form-control'})
                               )
    password = forms.CharField(label='密码',min_length=8,max_length=16,
                               error_messages={
                                   'required':'密码不能为空',
                                   'min_length':'密码最短为8位',
                                   'max_length':'密码最长位16位'
                               },
                               widget=forms.widgets.PasswordInput(attrs={'class':'form-control'})
                               )
    re_password = forms.CharField(label='确认密码',min_length=8,max_length=16,
                               error_messages={
                                   'required':'确认密码不能为空',
                                   'min_length':'确认密码最短为8位',
                                   'max_length':'确认密码最长位16位'
                               },
                               widget=forms.widgets.PasswordInput(attrs={'class':'form-control'})
                               )
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required':'邮箱不能为空',
                                 'invalid':'邮箱格式不正确'
                             },
                             widget=forms.widgets.EmailInput(attrs={'class':'form-control'})
                             )
    sitename = forms.CharField(label='站点名称',min_length=1,max_length=32,
                               error_messages={
                                    'required':'站点名称不能为空',
                                   'max_length':'站点名称最长位32位',
                               },
                               widget = forms.widgets.TextInput(attrs={'class': 'form-control'}),
                               )
    sitetitle = forms.CharField(label='站点标题',min_length=1,max_length=32,
                               error_messages={
                                    'required':'站点标题不能为空',
                                   'max_length':'站点标题最长位32位',
                               },
                               widget = forms.widgets.TextInput(attrs={'class': 'form-control'}),
                               )
    # 钩子函数
    #局部钩子：校验用户是否已存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            self.add_error('username','用户已存在')
        return username
    def clean_sitename(self):
        sitename = self.cleaned_data.get('sitename')
        is_exist = models.Usersite.objects.filter(site_name=sitename)
        if is_exist:
            self.add_error('sitename','站点名称已存在')
        return sitename
    #全局钩子：校验两次密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if not password == re_password:
            self.add_error('re_password','两次密码不一致')
        return self.cleaned_data


class MySetForm(forms.Form):
    username = forms.CharField(label='用户名',min_length=1,max_length=8,
                               error_messages={
                                   'required':'用户名不能为空',
                                   'max_length':'用户名不能超过8位'
                               },
                               widget=forms.widgets.TextInput(attrs={'class':'form-control'})
                               )
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required':'邮箱不能为空',
                                 'invalid':'邮箱格式不正确'
                             },
                             widget=forms.widgets.EmailInput(attrs={'class':'form-control'})
                             )
    sitename = forms.CharField(label='站点名称',min_length=1,max_length=32,
                               error_messages={
                                    'required':'站点名称不能为空',
                                   'max_length':'站点名称最长位32位',
                               },
                               widget = forms.widgets.TextInput(attrs={'class': 'form-control'}),
                               )
    sitetitle = forms.CharField(label='站点标题',min_length=1,max_length=32,
                               error_messages={
                                    'required':'站点标题不能为空',
                                   'max_length':'站点标题最长位32位',
                               },
                               widget = forms.widgets.TextInput(attrs={'class': 'form-control'}),
                               )
