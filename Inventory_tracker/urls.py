from django.contrib import admin
from django.urls import path, include

# python
# `Inventory_tracker/urls.py`
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stock.urls')),       # mount stock under /api/
    path('api/auth/', include('user.urls')),   # mount auth under /api/auth/
]
