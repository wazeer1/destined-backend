from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from . import views

app_name = "api_v1_accounts"

urlpatterns = [
    re_path(r"^check-phone/$", views.check_phone, name="check-phone"),
    re_path(r"^verify-otp/$", views.verify_otp, name="check-phone"),
    re_path(r"^update-user/$", views.update_user_profile, name="update-user"),
    re_path(r"^interest/$", views.create_interest, name="create-interest"),
    re_path(r"^user-interest/$", views.user_interest, name="user-interest"),

]