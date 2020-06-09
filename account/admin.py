from django.contrib import admin
from .models import UserInfo, ClassRecode


# Register your models here.

class ClassRecodeAdmin(admin.ModelAdmin):
    list_display = ('fk_user', 'recode_time', 'recode_states', 'recode_video', 'fk_teacher')


admin.site.register(UserInfo)
admin.site.register(ClassRecode, ClassRecodeAdmin)
