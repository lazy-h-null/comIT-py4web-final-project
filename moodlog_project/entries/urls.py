from django.urls import path
from .views import EmotionListView, EmotionCreateView, EmotionUpdateView, EmotionDeleteView, EmotionStatsView

urlpatterns = [
    path('', EmotionListView.as_view(), name='index'),
    path('add/', EmotionCreateView.as_view(), name='emotion-add'),
    path('<int:pk>/edit/', EmotionUpdateView.as_view(), name='emotion-edit'),
    path('<int:pk>/delete/', EmotionDeleteView.as_view(), name='emotion-delete'),
    path('stats/', EmotionStatsView.as_view(), name='emotion-stats'),
]