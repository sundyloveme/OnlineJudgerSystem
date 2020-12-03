from django.urls import path

from . import views
from .views import SearchJsonView

app_name = "problem"


urlpatterns = [
    path("list/", views.ProblemList.as_view(), name="problemList"),
    path("detail/<int:problem_id>/", views.ProblemDetail.as_view(), name="problemdetail"),
    path("save-note/<int:problem_id>/", views.saveNote, name="save_note"),
    path("search_problem/", views.search_problem_view, name="search"),
    path('search/', SearchJsonView()),

    path('get_problem_counts/', views.get_problem_counts_view),
    path('get_user_correct_problem_counts/', views.get_user_correct_problem_counts_view),
    path('get_problem_labes/', views.get_problem_labes_view),

    # path("liked-problem/<int:problem_id>", ),
    # path("collect-problem/<int:problem_id>", ),
]
