from django.urls import path
from .views import (
    HomeView,
    SignUpRequestView,
    ThanksView,
    ProfileView,
    FileField,
    Checkout
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('signup/', SignUpRequestView.as_view(), name="signup"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/upload_users/', FileField.as_view(), name="upload"),
    path('profile/upload_users/checkout', Checkout.as_view(), name="checkout")
]