from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.shortcuts import redirect
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("api/", include("main.urls")),
    path("favicon.ico", lambda _: redirect("static/favicon.ico", permanent=True)),
    path("robots.txt", lambda _: redirect("static/robots.txt", permanent=True)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path(
        "reset_password/", auth_views.PasswordResetView.as_view(), name="reset_password"
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
