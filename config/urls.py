from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from frontend.views import home, login_view, register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='registro'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
