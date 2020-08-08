from django.contrib import admin
from .models import Problem, SubmitStatus, ProblemLabel

# admin.site.register(Problem)
# admin.site.register(SubmitStatus)
admin.site.register(ProblemLabel)


@admin.register(SubmitStatus)
class SubmitStatusAdmin(admin.ModelAdmin):
    list_display = ['fk_problem_id', 'user_code_status', 'create_time',
                    'author']


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'Submits', 'difficulty', 'create_time')
    fieldsets = [
        ("题目内容", {'fields': ['title', 'problem_content']}),
        ("题目设置", {'fields': ['fk_labels', 'fk_author', 'difficulty']}),
        ("测试用例",
         {'fields': ['problem_test_case_input', 'problem_test_case_output',
                     'problem_std_code']}),

    ]
