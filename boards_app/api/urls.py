from django.urls import path
from .views import BoardDetailView, BoardListCreateView

urlpatterns = [
    path('', BoardListCreateView.as_view(), name='board-list-create'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'),   
    # path('../email-check/', views.EmailCheckView.as_view(), name='email-check'),
]