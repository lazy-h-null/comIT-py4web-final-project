from django.urls import path, reverse_lazy
from .views import EmotionListView, EmotionCreateView, EmotionUpdateView, EmotionDeleteView, EmotionStatsView, CustomPasswordChangeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', EmotionListView.as_view(), name='index'),
    path('add/', EmotionCreateView.as_view(), name='emotion-add'),
    path('<int:pk>/edit/', EmotionUpdateView.as_view(), name='emotion-edit'),
    path('<int:pk>/delete/', EmotionDeleteView.as_view(), name='emotion-delete'),
    path('stats/', EmotionStatsView.as_view(), name='emotion-stats'),
    path('calendar/<int:year>/<int:month>/', EmotionListView.as_view(), name='index_month'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]