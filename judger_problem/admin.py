from django.contrib import admin
from .models import Problem, SubmitStatus, ProblemLabel

admin.site.register(Problem)
# admin.site.register(SubmitStatus)
admin.site.register(ProblemLabel)


@admin.register(SubmitStatus)
class SubmitStatusAdmin(admin.ModelAdmin):
    list_display = ['fk_problem_id', 'user_code_status', 'create_time',
                    'author']
