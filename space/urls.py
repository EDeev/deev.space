from django.contrib import admin
from django.urls import path, include

handler404 = 'main_page.views.custom_page_not_found_view'
handler500 = 'main_page.views.custom_error_view'
handler403 = 'main_page.views.custom_permission_denied_view'
handler400 = 'main_page.views.custom_bad_request_view'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('main_page.urls')),
]
