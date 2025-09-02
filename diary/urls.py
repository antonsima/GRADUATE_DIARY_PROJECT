from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = 'diary'

router = DefaultRouter()
router.register(r'entries', views.EntryViewSet, basename='entry')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'moods', views.MoodViewSet, basename='mood')
router.register(r'reminders', views.ReminderViewSet, basename='reminder')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),

    # Authentication endpoints (перенаправляем в users приложение)
    # path('api/auth/login/', views.UserLoginView.as_view(), name='login_api'),
    # path('api/auth/register/', views.UserRegistrationView.as_view(), name='register_api'),
    # path('api/auth/token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/auth/profile/', views.UserProfileView.as_view(), name='user_profile_api'),
    # path('api/auth/logout/', views.logout_view, name='logout_api'),

    # HTML pages
    path('', views.DiaryHomeView.as_view(), name='index'),
    # path('register/', views.RegistrationPageView.as_view(), name='register_page'),
    # path('login/', views.LoginPageView.as_view(), name='login_page'),
    path('profile/', views.ProfilePageView.as_view(), name='profile_page'),
    # path('logout/', views.LogoutPageView.as_view(), name='logout_page'),

    # Diary pages
    path('entries/', views.EntryListView.as_view(), name='entry_list'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('stats/', views.StatisticsView.as_view(), name='statistics'),

    path('settings/', views.SettingsPageView.as_view(), name='settings'),
]