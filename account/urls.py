from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    # path("sendemail/", views.sendEmailView, name="SendEmail"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("submit_record/", views.submit_status_list_view, name="submit_record"),
    path("show-user-submited-code/", views.show_user_submited_code,
         name="show_user_submited_code"),
    # path("show-user-notes/", views.note_list, name="show_user_notes"),
    # path("classrecode/", views.ClassRecodeView.as_view(), name="classrecode"),
    path("check-email/", views.check_email_repeat),
    path("check-nick-name/", views.check_nick_name_repeat),
    path("get_captcha/", views.get_captcha),
    path("check_captcha/", views.check_captcha),
    path("check_login/", views.CheckLoginView.as_view()),
    path("upload_file/", views.load_file, name='upload_file'),
    path('send_email/', views.send_email_captcha),
    path('verify_email/', views.VerifyEmail.as_view()),
]
