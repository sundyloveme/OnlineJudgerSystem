from django.contrib import admin
from django.urls import path
from . import views
from django.http import JsonResponse
from haystack.views import SearchView

app_name = "problem"

class SearchJsonView(SearchView):
    """
    重写haystack的视图函数
    原本返回的是html模板，重写后返回json数据
    """

    def create_response(self):
        results = self.get_context()
        ret = []

        for result in results['page'].object_list:
            ret.append({"id": result.object.id,
                        "title": result.object.title})

        return JsonResponse(ret, safe=False)

urlpatterns = [
    path("list/", views.ProblemList.as_view(), name="problemList"),
    path("detail/<int:problem_id>/", views.ProblemDetail.as_view(), name="problemdetail"),
    path("save-note/<int:problem_id>/", views.saveNote, name="save_note"),
    # path("search/", views.search_problem_view, name="search"),
    path('search/', SearchJsonView()),

    # path("liked-problem/<int:problem_id>", ),
    # path("collect-problem/<int:problem_id>", ),
]
