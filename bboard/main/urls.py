from django.urls import path
from .views import index, other_page

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('<str:page>/', other_page, name='other')
]
