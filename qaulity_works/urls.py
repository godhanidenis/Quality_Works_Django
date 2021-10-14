from django import urls
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rest',include('rest_framework.urls')),
    path('api/', include('auth_login.urls')),
    path('elastic/', include('elastic_search.urls'))
]
