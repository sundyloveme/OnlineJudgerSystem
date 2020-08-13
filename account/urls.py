from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("sendemail/", views.sendEmailView, name="SendEmail"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("submit_record/", views.submit_status_list_view, name="submit_record"),
    path("show-user-submited-code/", views.show_user_submited_code,
         name="show_user_submited_code"),
    path("show-user-notes/", views.note_list, name="show_user_notes"),
    path("classrecode/", views.ClassRecodeView.as_view(), name="classrecode"),
]
