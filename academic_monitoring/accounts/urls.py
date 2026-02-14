from django.urls import path
from .views import login_view
from .views import home
urlpatterns = [
    path("", home, name="home"),
    path('login/', login_view, name='login'),
    
]
