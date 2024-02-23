from django.contrib import admin
from django.urls import path


admin.site.site_header = "Granadota"
admin.site.site_title = ""
admin.site.index_title = "Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
]
