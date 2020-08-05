from django.contrib import admin
from .models import UserInfo, ClassRecode


# Register your models here.

class ClassRecodeAdmin(admin.ModelAdmin):
    list_display = (
    'fk_user', 'recode_time', 'recode_states', 'recode_video', 'fk_teacher')


admin.site.register(UserInfo)
admin.site.register(ClassRecode, ClassRecodeAdmin)
admin.site.site_title = admin.site.site_header = "少儿编程教育管理系统"
