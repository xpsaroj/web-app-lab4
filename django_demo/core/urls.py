from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("concepts/", views.concepts_view, name="concepts"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("preferences/", views.preferences_view, name="preferences"),
    path("articles/", views.article_list_view, name="article_list"),
    path("articles/create/", views.article_create_view, name="article_create"),
    path("articles/<slug:slug>/", views.article_detail_view, name="article_detail"),
    path("articles/<slug:slug>/edit/", views.article_edit_view, name="article_edit"),
    path("articles/<slug:slug>/delete/", views.article_delete_view, name="article_delete"),
    path("articles/<slug:slug>/comment/", views.comment_create_view, name="comment_create"),
    path("profile/", views.profile_view, name="profile"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("api/articles/", views.articles_api_view, name="articles_api"),
]
