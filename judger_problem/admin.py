from django.contrib import admin
from .models import Problem, SubmitStatus, ProblemLabel, ClassRecode


class ClassRecodeAdmin(admin.ModelAdmin):
    list_display = ('fk_user', 'recode_time', 'recode_states', 'recode_video', 'fk_teacher')


# Register your models here.
admin.site.register(Problem)
admin.site.register(SubmitStatus)
admin.site.register(ProblemLabel)
admin.site.register(ClassRecode, ClassRecodeAdmin)
