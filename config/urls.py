
from django.contrib import admin
from django.urls import include, path

from documents.pages import (
    home,
    upload_page,
    login_page,
    signup_page,
    logout_page,
)

urlpatterns = [
    path("", login_page, name="home"),
    path("dashboard/", home, name="dashboard"),
    path("upload/", upload_page, name="upload-page"),
    path("login/", login_page, name="login"),
    path("accounts/login/", login_page, name="accounts-login"),
    path("signup/", signup_page, name="signup"),
    path("logout/", logout_page, name="logout"),
    path("admin/", admin.site.urls),
    path("api/documents/", include("documents.urls")),
]
