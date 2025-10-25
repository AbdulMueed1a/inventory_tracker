from django.urls import path
from .views import SignupView
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('token/', TokenVerifyView.as_view()),
    path('signup/', SignupView.as_view()),
]
