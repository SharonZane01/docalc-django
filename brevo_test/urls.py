from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- 👇 ADD THIS LINE ---
    # This tells Django that all URLs starting with 'api/'
    # should be handled by the urls.py file in your 'brevo_app'
    path('api/', include('brevo_app.urls')),
    # --- END OF LINE TO ADD ---
    
    # You might also have your web-based dashboard URL here
    # path('dashboard/', views.dashboard_view, name='dashboard'), # Example
]