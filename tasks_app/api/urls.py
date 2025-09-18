from django.urls import path
from .views import AssignedTasksListView, CommentCreateView, CommentDetailView, ReviewingTasksListView, TaskCreateView, TaskDetailView

urlpatterns = [
    path('assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-to-me'),
    path('reviewing/', ReviewingTasksListView.as_view(), name='reviewing'),
    path('', TaskCreateView.as_view(), name='task-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),  
    path('<int:task_id>/comments/', CommentCreateView.as_view(), name='task-comments'),
    path('<int:task_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='task-comment-detail'),

]