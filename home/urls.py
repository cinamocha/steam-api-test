from django.urls import path
from . import views 


urlpatterns = [
    path('', views.index, name='home'), #views.pyのindex関数を呼び出す
]