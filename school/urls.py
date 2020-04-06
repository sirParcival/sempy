from django.urls import path
from .views import (
    HomeView,
    SignUpRequestView,
    ThanksView,
    ProfileView,
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('signup/', SignUpRequestView.as_view(), name="signup"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('profile/', ProfileView.as_view(), name="profile"),
]