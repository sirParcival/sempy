from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
from sempy import settings
from .views import (
    HomeView,
    SignUpRequestView,
    ThanksView,
    ProfileView,
    FileField,
    Checkout,
    change_password,

)

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    path('signup/', SignUpRequestView.as_view(), name="signup"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/upload_users/', FileField.as_view(), name="upload"),
    path('profile/upload_users/checkout', Checkout.as_view(), name="checkout"),
    path('profile/change_password', change_password, name='change_password')
] + static(settings.FILES_URL, document_root=settings.FILES_ROOT)