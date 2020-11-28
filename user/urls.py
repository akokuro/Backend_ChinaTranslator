from django.urls import re_path, include  
from .views import RegistrationAPIView, LoginAPIView

urlpatterns = [
    re_path(r'^register/?$', RegistrationAPIView.as_view(), name='user_registration'),
    re_path(r'^login/?$', LoginAPIView.as_view(), name='user_login'),
]