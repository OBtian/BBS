from django.contrib import admin
from app01 import models
# Register your models here.

admin.site.register(models.UserInfo)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Usersite)
admin.site.register(models.Article2Tag)
admin.site.register(models.Classify)
admin.site.register(models.Comment)
admin.site.register(models.Up_Or_Down)