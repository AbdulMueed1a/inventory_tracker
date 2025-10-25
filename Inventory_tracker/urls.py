from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('stock.urls')),
    path('auth/', include('user.urls')),
]
