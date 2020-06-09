from django.contrib import admin
from .models import Problem, SubmitStatus, ProblemLabel

admin.site.register(Problem)
admin.site.register(SubmitStatus)
admin.site.register(ProblemLabel)
