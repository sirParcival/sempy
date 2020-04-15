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
    GroupDetail,
    add_user_to_group,
    decline_request,
)

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    path('signup/', SignUpRequestView.as_view(), name="signup"),
    path('thanks/', ThanksView.as_view(), name="thanks"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/upload_users/', FileField.as_view(), name="upload"),
    path('profile/upload_users/checkout', Checkout.as_view(), name="checkout"),
    path('profile/change_password', change_password, name='change_password'),
    path('profile/<slug:name>_<int:pk>_<int:creator_id>', GroupDetail.as_view(), name='group_detailed_view'),
    path('profile/add_<int:pk>', add_user_to_group, name='add'),
    path('profile/decline_<int:pk>', decline_request, name='decline')
] + static(settings.FILES_URL, document_root=settings.FILES_ROOT)