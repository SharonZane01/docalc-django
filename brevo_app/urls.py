from django.urls import path
from . import views

# These are the URL patterns for your API
# Your React Native app will make requests to these endpoints
urlpatterns = [
    # Auth URLs
    # e.g., POST to /api/signup/
    path('signup/', views.signup_view, name='api-signup'),
    path('verify-otp/', views.verify_otp_view, name='api-verify-otp'),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),

    # Expense URLs
    # e.g., GET or POST to /api/expenses/
    path('expenses/', views.expense_view, name='api-expense-list-create'),
    # e.g., GET, PUT, or DELETE to /api/expenses/123/
    path('expenses/<int:pk>/', views.expense_detail_view, name='api-expense-detail'),

    # Stats & Profile URLs
    # e.g., GET to /api/stats/
    path('stats/', views.stats_view, name='api-stats'),
    # e.g., GET or PUT to /api/profile/
    path('profile/', views.profile_view, name='api-profile'),
]