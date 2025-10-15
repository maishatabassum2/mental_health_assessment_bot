from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def home_view(request):
    return render(request, 'users/home.html')  # Always show home

urlpatterns = [
    path('', home_view, name='home'),  # Home always shows home.html
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
]
