from django.contrib import admin
from django.urls import path, include
from bom import views as bom_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('bom/', include('bom.urls')),
    path('', bom_views.home, name='home'),
]

