
from django.contrib import admin
from django.urls import path, include

from auth.views import home, signup, signin, signout, activate

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('ativate/<uidb64>/<token>', activate, name='activate'),
]