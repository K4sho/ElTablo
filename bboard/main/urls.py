from django.urls import path
from .views import index, other_page, BBLoginView, BBLogoutView, profile, ChangeUserInfoView, BBPasswordChangeView
from .views import RegisterUserView, RegisterDoneView

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BBLoginView.as_view(), name='login'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done')
]
